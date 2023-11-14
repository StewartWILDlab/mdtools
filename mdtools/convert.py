"""Conversion of MD results to coco_result and Label Studio Task json."""

import os
import json
import exiftool
import math

import pandas as pd
import numpy as np

from tqdm import tqdm
from PIL import Image

# from label_studio_converter.imports.label_config import generate_label_config
from label_studio_converter.imports.coco import create_bbox
from label_studio_converter.imports.coco import new_task

from mdtools.classes import COCOResult, MDResult
from mdtools.cocoutils import create_coco_info_dict
from mdtools.readexif import read_exif_from_md, DEFAULT_TAGS

# TODO Add info + license dict argument


def md_to_coco_ct(md_result: MDResult) -> COCOResult:
    """Convert MegaDetector output JSON into a coco_result-CT JSON.

    Code adapted from https://github.com/microsoft/CameraTraps/ from the
    `data_management` module.
    """
    # Get base dir
    image_base_dir = os.path.join(md_result.root, md_result.folder)

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

    print(f"Processing .json file {md_result.md_file}")

    # Load .json annotations for this data set
    categories_this_dataset = md_result.md_categories()

    # PERF: Not exactly trivially parallelizable, but about 100% of the
    # time here is spent reading image sizes (which we need to do to get from
    # absolute to relative coordinates), so worth parallelizing.
    for i_entry, entry in enumerate(tqdm(md_result.md_images())): # [90000:len(md_result.md_images())]

        # Get the relative path
        image_relative_path = entry["file"]

        # Generate a unique ID from the path
        # TODO turn this into a function
        image_id = (
            image_relative_path.split(".")[0]
            .replace("\\", "/")
            .replace("/", "_")
            .replace(" ", "_")
        )

        im = {}
        im["id"] = image_id
        im["file_name"] = image_relative_path

        pil_image = Image.open(os.path.join(image_base_dir,
                                            image_relative_path))
        width, height = pil_image.size
        im["width"] = width
        im["height"] = height

        images.append(im)

        if "detections" in entry.keys():
            detections = entry["detections"]

            if detections is None:

                print(entry)

            else:

                if len(detections) >= 1:
                    # detection = detections[0]
                    for i, detection in enumerate(detections):

                        category_name = (
                            categories_this_dataset[detection["category"]])
                        category_name = category_name.strip().lower()
                        category_name = category_name.replace(" ", "_")

                        # Have we seen this category before?
                        if category_name in category_name_to_category:
                            category_id = (
                                category_name_to_category[category_name]["id"])
                        else:
                            category_id = next_category_id
                            category = {}
                            category["id"] = category_id
                            category["name"] = category_name
                            category_name_to_category[category_name] = category
                            next_category_id += 1

                        # Create an annotation
                        ann = {}
                        ann["id"] = im["id"] + "_" + str(i)
                        ann["image_id"] = im["id"]
                        ann["category_id"] = category_id
                        ann["confidence"] = detection["conf"]
                        ann["max_confidence"] = entry["max_detection_conf"]
                        ann["isempty"] = False

                        if category_id != 0:
                            ann["bbox"] = detection["bbox"]
                            # MegaDetector: [x,y,width,height]
                            # (normalized, origin upper-left)
                            # CCT: [x,y,width,height]
                            # (absolute, origin upper-left)
                            ann["bbox"][0] = ann["bbox"][0] * im["width"]
                            ann["bbox"][1] = ann["bbox"][1] * im["height"]
                            ann["bbox"][2] = ann["bbox"][2] * im["width"]
                            ann["bbox"][3] = ann["bbox"][3] * im["height"]
                        else:
                            assert detection["bbox"] == [0, 0, 0, 0]

                        annotations.append(ann)

                else:
                    ann = {}
                    ann["id"] = im["id"] + "_0"
                    ann["image_id"] = im["id"]
                    ann["category_id"] = 0
                    ann["isempty"] = True
                    annotations.append(ann)

        else:
            print("Error on file %s" % entry["file"])

    print("Finished creating CCT dictionaries")

    # Create info struct
    info = create_coco_info_dict(md_result)

    # Write .json output
    categories = list(category_name_to_category.values())

    coco_data = {}
    coco_data["images"] = images
    coco_data["annotations"] = annotations
    coco_data["categories"] = categories
    coco_data["info"] = info

    coco_result = COCOResult(
        md_result.root,
        md_result.folder,
        md_result.md_file,
        coco_data=coco_data,
    )

    return coco_result


def coco_ct_to_ls(
    coco_result: COCOResult, exif_tab: pd.DataFrame, ls_path_out: str,
    conf_threshold: float = 0.1, write: bool = False,
    image_root_url: str = "/data/local-files/?d=",
    repeat: bool = False
) -> list:
    """Convert coco_result CT labeling to Label Studio JSON.

    Adapted from label_studio_converter.imports.coco_result

    :param input_file: file with coco_result json
    :param output_coco: output file with Label Studio JSON tasks
    :param image_root_url: root URL/path where images will be hosted
    :param to_name: object name from Label Studio labeling config
    :param from_name: control tag name from Label Studio labeling config
    :param out_type: annotation type - "annotations" or "predictions"
    """
    # TODO check if cocoresult HAS exif data

    # Initiate task dict
    tasks = {}  # image_id => task

    # build categories => labels dict
    new_categories = {}
    # list to dict conversion: [...] => {category_id: category_item}
    coco_cat = coco_result.coco_categories()
    categories = {
        int(category["id"]): category for category in coco_cat
    }
    ids = sorted(categories.keys())  # sort labels by their origin ids

    for i in ids:
        name = categories[i]["name"]
        new_categories[i] = name

    # mapping: id => category name
    categories = new_categories

    # mapping: image id => image
    images = {item["id"]: item for item in coco_result.coco_images()}

    print(
        f"Found {len(categories)} categories, {len(images)} images and " +
        f"{len(coco_result.coco_annotations())} annotations"
    )

    # Parameters for labeling config composing
    to_name = "image"
    from_name = "label"
    out_type = "predictions"
    bbox = False
    bbox_once = False
    rectangles_from_name = from_name + "_rectangles"
    tags = {}

    score_table = exif_tab.loc[
        :,
        [
            "file",
            "conf",
            "File:Directory",
            "MakerNotes:Sequence",
            "MakerNotes:EventNumber",
        ],
    ]

    score_table["conf"] = pd.to_numeric(score_table["conf"], errors='coerce')

    score_table_unique = score_table.drop_duplicates()

    for key in tqdm(images.keys()):

        filtered = score_table_unique[
            score_table_unique.file == images[key]["file_name"]
        ]

        if np.isnan(filtered["conf"]).all():
            
            file_name = images[key]["file_name"]
            print(f"skipping file {file_name}")
        
        else:

            if filtered.shape[0] == 0:

                file_name = images[key]["file_name"]
                print(f"skipping file {file_name}")

            else:

                file_name = images[key]["file_name"]
                # print(f"Processing file {file_name}") 
                # print(filtered)               

                images[key]["sequence_id"] = (
                    filtered["MakerNotes:Sequence"].iloc[0])
                images[key]["sequence_nb"] = (
                    filtered["MakerNotes:EventNumber"].iloc[0])
                images[key]["dir"] = filtered["File:Directory"].iloc[0]

                image_seq_id = images[key]["sequence_id"]
                image_seq_number = images[key]["sequence_nb"]
                image_dir = images[key]["dir"]

                if image_seq_id == "0 0":
                    subset = score_table_unique[
                        score_table_unique.file == images[key]["file_name"]
                    ]
                else:
                    query = (f"`MakerNotes:EventNumber` == {image_seq_number} " +
                             f"and `File:Directory` == '{image_dir}' " +
                             f"and `MakerNotes:Sequence` != '0 0'")
                    # print(query)
                    subset = score_table.query(query)

                if subset.shape[0] == 0:
                    images[key]["max_sequence_conf"] = 0
                else:
                    assert subset["file"].drop_duplicates().shape[0] <= 5
                    images[key]["max_sequence_conf"] = np.nanmax(subset["conf"])

    # print("Here 1")

    for i, annotation in enumerate(tqdm(coco_result.coco_annotations())):

        image_id = annotation["image_id"]
        image = images[image_id]

        ## Skip NonWildlife Images for second retrieval
        ## Only foe second deployment/retrieval at the moment
        image_file_name = image["file_name"]
        # if "NonWildlife" in file_name:
        #     # print(f"skipping file {file_name}")
        #     continue
        # else:
        #     print(f"Processing file {file_name}")

        print(f"Processing file {file_name}")

        image_conf = image["max_sequence_conf"]

        bbox |= "bbox" in annotation

        if bbox and not bbox_once:
            tags.update({rectangles_from_name: "RectangleLabels"})
            bbox_once = True

        # read image sizes & detection confidence

        image_file_name, image_width, image_height = (
            image["file_name"],
            image["width"],
            image["height"],
        )

        if image_conf >= float(conf_threshold):

            # get or create new task
            if image_id in tasks:
                task = tasks[image_id]
            else:
                task = new_task(out_type, image_root_url, image_file_name)
                task[out_type][0]["score"] = image_conf

            if "confidence" in annotation:

                annotation_conf = annotation["confidence"]

                if annotation_conf > float(conf_threshold):

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

            tasks[image_id] = task

    if len(tasks) > 0:
        tasks = [tasks[key] for key in sorted(tasks.keys())]
        task_len = len(tasks)

        if write:
            # base_path = coco_result.root + coco_result.folder
            # if repeat:
            #     output_ls = coco_result.folder + "_output_ls_norepeats.json"
            # else:
            #     output_ls = coco_result.folder + "_output_ls.json"
            print(f"Saving {task_len} tasks to Label Studio JSON " +
                  f"file {ls_path_out}")
            with open(ls_path_out, "w") as out:
                json.dump(tasks, out)

        return tasks

    else:
        print("ERROR: No labels converted")
