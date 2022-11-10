import exiftool
import json
import os
import pandas as pd

from tqdm import tqdm

# TODO add batch size arg


def read_exif_from_md(md_json, tags="all", write=True):
    """Convert md_json to CSV format.

    Extract EXIF information from the md_json.

    """
    # TODO fix the tags handling
    the_tags = [
        "File:FileName",
        "File:Directory",
        "MakerNotes:Sequence",
        "MakerNotes:EventNumber",
        "EXIF:DateTimeOriginal",
        "MakerNotes:DateTimeOriginal",
        "MakerNotes:DayOfWeek",
        "MakerNotes:MoonPhase",
        "MakerNotes:AmbientTemperature",
        "MakerNotes:MotionSensitivity",
        "MakerNotes:BatteryVoltage",
        "MakerNotes:BatteryVoltageAvg",
        "MakerNotes:UserLabel",
    ]

    with open(md_json, "r") as f:
        md = json.loads(f.read())
    folder = os.path.basename(md_json).split("_")[0]
    root = os.path.dirname(md_json) + "/"

    full_data = pd.DataFrame()
    images = md["images"]
    images_names = [img["file"] for img in images]
    images_has_detect_key = ["detections" in img.keys() for img in images]
    images = [img for i, img in enumerate(images) if images_has_detect_key[i]]

    # for image in tqdm(images):
    batchsize = 10
    base_path = md_json.split("_")[0]

    for i in tqdm(range(0, len(images), batchsize)):
        batch = images[i : i + batchsize]

        filenames = [os.path.join(base_path, img["file"]) for img in batch]

        with exiftool.ExifToolHelper() as et:
            tags = [et.get_tags(filename, the_tags)[0] for filename in filenames]

        tags_df = (pd.json_normalize(tags)
                   .assign(
                        source_file=lambda df: df["SourceFile"].map(
                            lambda SourceFile: SourceFile.replace(root, "")
                        )
                    ))
        full_data = pd.concat([full_data, tags_df])

    if write:
        name_out = os.path.join(os.path.dirname(md_json), folder) + "_exif.csv"
        full_data.to_csv(name_out, index = False)

    return full_data
