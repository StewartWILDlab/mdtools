import os
import json
import uuid
import exiftool
import pandas as pd

from tqdm import tqdm
from PIL import Image
from collections import defaultdict

from label_studio_converter.imports.label_config import generate_label_config
from label_studio_converter.imports.coco import create_bbox
from label_studio_converter.imports.coco import new_task

# TODO Add info + license dict argument


def md_to_coco_ct(md_json, output_json, image_base_dir=".", write=True):
    """Convert MegaDetector output JSON into a COCO-CT JSON

    Code taken from https://github.com/microsoft/CameraTraps/tree/main/data_management.

    TODO
    """

    # Initialize empty arrays / dicts
    images = []
    annotations = []
    category_name_to_category = {}

    # Force the empty category to be ID 0
    empty_category = {}
    empty_category["name"] = "empty"
    empty_category["id"] = 0
    category_name_to_category["empty"] = empty_category
    next_category_id = 1

    print("Processing .json file {}".format(md_json))

    # Load .json annotations for this data set
    if isinstance(md_json, str):
        with open(md_json, "r") as f:
            data = f.read()
        data = json.loads(data)
    elif isinstance(md_json, dict):
        data = md_json

    categories_this_dataset = data["detection_categories"]

    # NOTE: i_entry is the "image number"
    i_entry = 0
    entry = data["images"][i_entry]

    # PERF: Not exactly trivially parallelizable, but about 100% of the
    # time here is spent reading image sizes (which we need to do to get from
    # absolute to relative coordinates), so worth parallelizing.
    for i_entry, entry in enumerate(tqdm(data["images"])):

        image_relative_path = entry["file"]

        # Generate a unique ID from the path
        image_id = (
            image_relative_path.split(".")[0]
            .replace("\\", "/")
            .replace("/", "_")
            .replace(" ", "_")
        )

        im = {}
        im["id"] = image_id
        im["file_name"] = image_relative_path

        pil_image = Image.open(os.path.join(
            image_base_dir, image_relative_path))
        width, height = pil_image.size
        im["width"] = width
        im["height"] = height

        images.append(im)

        if "detections" in entry.keys():
            detections = entry["detections"]

            if len(detections) >= 1:
                # detection = detections[0]
                for detection in detections:

                    category_name = categories_this_dataset[detection["category"]]
                    category_name = category_name.strip().lower()
                    category_name = category_name.replace(" ", "_")

                    # Have we seen this category before?
                    if category_name in category_name_to_category:
                        category_id = category_name_to_category[category_name]["id"]
                    else:
                        category_id = next_category_id
                        category = {}
                        category["id"] = category_id
                        print("Adding category {}".format(category_name))
                        category["name"] = category_name
                        category_name_to_category[category_name] = category
                        next_category_id += 1

                    # Create an annotation
                    ann = {}
                    ann["id"] = str(uuid.uuid1())
                    ann["image_id"] = im["id"]
                    ann["category_id"] = category_id
                    ann["confidence"] = detection["conf"]
                    ann["max_confidence"] = entry["max_detection_conf"]
                    ann["isempty"] = False

                    if category_id != 0:
                        ann["bbox"] = detection["bbox"]
                        # MegaDetector: [x,y,width,eight] (normalized, origin upper-left)
                        # CCT: [x,y,width,height] (absolute, origin upper-left)
                        ann["bbox"][0] = ann["bbox"][0] * im["width"]
                        ann["bbox"][1] = ann["bbox"][1] * im["height"]
                        ann["bbox"][2] = ann["bbox"][2] * im["width"]
                        ann["bbox"][3] = ann["bbox"][3] * im["height"]
                    else:
                        assert detection["bbox"] == [0, 0, 0, 0]

                    annotations.append(ann)

            else:
                ann = {}
                ann["id"] = str(uuid.uuid1())
                ann["image_id"] = im["id"]
                ann["category_id"] = 0
                ann["isempty"] = True
                annotations.append(ann)

        else:
            print("Error on file %s" % entry["file"])

    print("Finished creating CCT dictionaries")

    # Create info struct
    info = dict()
    info["year"] = 2020
    info["version"] = 1.0
    info["description"] = "Fun With Camera Traps"
    info["contributor"] = "Somebody"

    # Write .json output
    categories = list(category_name_to_category.values())
    json_data = {}

    json_data["images"] = images
    json_data["annotations"] = annotations
    json_data["categories"] = categories
    json_data["info"] = info

    if write:
        json.dump(json_data, open(output_json, "w"), indent=2)

        print(
            "Finished writing .json file with {} images, {} annotations, and {} categories".format(
                len(images), len(annotations), len(categories)
            )
        )

    return json_data


def coco_ct_to_ls(
    coco_json,
    output_json,
    conf_threshold=0.1,
    image_root_url="/data/local-files/?d=",
    to_name="image",
    from_name="label",
    out_type="predictions",
    generate_config_file=False,
    write=True,
):
    """Convert COCO CT labeling to Label Studio JSON

    Adapted from label_studio_converter.imports.coco

    :param input_file: file with COCO json
    :param output_json: output file with Label Studio JSON tasks
    :param image_root_url: root URL/path where images will be hosted
    :param to_name: object name from Label Studio labeling config
    :param from_name: control tag name from Label Studio labeling config
    :param out_type: annotation type - "annotations" or "predictions"
    :param generate_config_file: whether to generate the XML config file
    """

    # Initiate task dict
    tasks = {}  # image_id => task

    # Open file if needed
    if isinstance(coco_json, str):
        with open(coco_json, "r") as f:
            coco = json.loads(f.read())
    elif isinstance(coco_json, dict):
        coco = coco_json

    # build categories => labels dict
    new_categories = {}
    # list to dict conversion: [...] => {category_id: category_item}
    categories = {int(category["id"]): category for category in coco["categories"]}
    ids = sorted(categories.keys())  # sort labels by their origin ids

    for i in ids:
        name = categories[i]["name"]
        new_categories[i] = name

    # mapping: id => category name
    categories = new_categories

    # mapping: image id => image
    images = {item["id"]: item for item in coco["images"]}

    print(
        f'Found {len(categories)} categories, {len(images)} images and {len(coco["annotations"])} annotations'
    )

    # flags for labeling config composing
    bbox = False
    bbox_once = False
    rectangles_from_name = from_name + "_rectangles"
    tags = {}

    for i, annotation in enumerate(tqdm(coco["annotations"])):

        if annotation["isempty"]:
            next

        else:
            bbox |= "bbox" in annotation

            if bbox and not bbox_once:
                tags.update({rectangles_from_name: "RectangleLabels"})
                bbox_once = True

            # read image sizes & detection confidence
            image_id = annotation["image_id"]
            image = images[image_id]
            image_file_name, image_width, image_height = (
                image["file_name"],
                image["width"],
                image["height"],
            )
            annotation_conf = annotation["confidence"]

            if float(annotation_conf) >= float(conf_threshold):

                # get or create new task
                if image_id in tasks:
                    task = tasks[image_id]
                else:
                    task = new_task(out_type, image_root_url, image_file_name)
                    task[out_type][0]["score"] = 0

                if "bbox" in annotation:
                    item = create_bbox(
                        annotation,
                        categories,
                        rectangles_from_name,
                        image_height,
                        image_width,
                        to_name,
                    )
                    # Replace item id with id created in the first step
                    item["id"] = annotation["id"]
                    task[out_type][0]["result"].append(item)
                    if float(annotation_conf) > float(task[out_type][0]["score"]):
                        task[out_type][0]["score"] = annotation_conf

                tasks[image_id] = task

    # generate and save labeling config
    if generate_config_file:
        label_config_file = output_json.replace(
            ".json", "") + ".label_config.xml"
        print(f"Saving Label Studio XML to {label_config_file}")
        generate_label_config(categories, tags, to_name,
                              from_name, label_config_file)

    if len(tasks) > 0:
        tasks = [tasks[key] for key in sorted(tasks.keys())]
        task_len = len(tasks)

        if write:
            print(
                f"Saving {task_len} tasks to Label Studio JSON file {output_json}")
            with open(output_json, "w") as out:
                json.dump(tasks, out)

        return tasks
    else:
        print("ERROR: No labels converted")


def md_to_ls(
    md_json,
    conf_threshold=0.1,
    image_base_dir=".",
    image_root_url="/data/local-files/?d=",
    write_coco=False,
    output_json_coco=None,
    write_ls=False,
    output_json_ls=None,
):

    if not isinstance(output_json_coco, str):
        output_json_coco = os.path.splitext(md_json)[0] + "_coco.json"

    if not isinstance(output_json_ls, str):
        output_json_ls = os.path.splitext(md_json)[0] + "_ls.json"

    coco_ct = md_to_coco_ct(md_json, output_json_coco,
                            image_base_dir, write=write_coco)
    ls = coco_ct_to_ls(
        coco_ct, output_json_ls, conf_threshold, image_root_url, write=write_ls
    )
    return ls

# TODO review tags info

def md_to_csv(md_json, read_exif=True, write=True):
    """Convert md_json to CSV format

    Extract information from the md_json.

    """

    the_tags = ["File:FileName", "File:Directory",
                "EXIF:DateTimeOriginal", "MakerNotes:DateTimeOriginal",
                "MakerNotes:DayOfWeek", "MakerNotes:MoonPhase",
                "MakerNotes:AmbientTemperature", "MakerNotes:MotionSensitivity",
                "MakerNotes:BatteryVoltage", "MakerNotes:BatteryVoltageAvg",
                "MakerNotes:UserLabel"]

    with open(md_json, "r") as f:
        md = json.loads(f.read())

    dat = pd.json_normalize(md["images"])
    folder = os.path.basename(md_json).split("_")[0]

    full_data = pd.DataFrame()

    for image in tqdm(md["images"]):
        if "detections" in image.keys():

            if len(image["detections"]) != 0:

                dat = (
                    pd.json_normalize(image["detections"])
                    .assign(file=image["file"])
                    .assign(folder=folder)
                    .assign(
                        category=lambda df: df["category"].map(
                            lambda category: int(category)
                        )
                    )
                )

                if read_exif:
                    filename = os.path.join(
                        md_json.split("_")[0], image["file"])

                    with exiftool.ExifToolHelper() as et:
                        tags = et.get_tags(filename, the_tags)[0]

                    tags_df = pd.json_normalize(tags)
                    tags_df["file"] = image["file"]
                    dat = pd.merge(dat, tags_df, how="left", on="file")

            else:

                dat = (pd.DataFrame({"category": [0]})
                       .assign(conf='NA')
                       .assign(bbox='NA')
                       .assign(file=image["file"])
                       .assign(folder=folder)
                       )

                if read_exif:
                    filename = os.path.join(
                        md_json.split("_")[0], image["file"])

                    with exiftool.ExifToolHelper() as et:
                        tags = et.get_tags(filename, the_tags)[0]

                    tags_df = pd.json_normalize(tags)
                    tags_df["file"] = image["file"]
                    dat = pd.merge(dat, tags_df, how="left", on="file")

            full_data = pd.concat([full_data, dat])

        else:
            print("Error on file %s" % image["file"])

    if write:
        name_out = os.path.join(os.path.dirname(
            md_json), folder) + "_output.csv"
        full_data.to_csv(name_out)

    return full_data
