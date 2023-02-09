"""Read exif data related to a megadetector result."""

import exiftool
import json
import os
import pandas as pd

from tqdm import tqdm

from mdtools.classes import MDResult

DEFAULT_TAGS = [
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


def read_exif_from_md(md_result: MDResult or str, tags: list = DEFAULT_TAGS,
                      batchsize: int = 100, write: bool = False
                      ) -> pd.DataFrame:
    """Extract EXIF information from the md_result.

    Accepts string or MDResult object.
    """
    # Initialize the final data
    full_data = pd.DataFrame()

    if isinstance(md_result, str):

        with open(md_result, "r") as f:
            md = json.loads(f.read())
        folder = os.path.basename(md_result).split("_")[0]
        root = os.path.dirname(md_result) + "/"
        base_path = md_result.split("_")[0]
        base_name_out = os.path.join(os.path.dirname(md_result), folder)
        name_out = base_name_out + "_exif.csv"

    elif isinstance(md_result, MDResult):

        md = md_result.md_data
        folder = md_result.folder
        root = md_result.root
        name_out = md_result.make_csv_write_path()
        base_path = os.path.join(os.path.dirname(name_out), folder)

    images = md["images"]
    images_has_detect_key = ["detections" in img.keys() for img in images]
    images = [img for i, img in enumerate(images) if images_has_detect_key[i]]

    for i in tqdm(range(0, len(images), batchsize)):
        batch = images[i: i + batchsize]

        filenames = [os.path.join(base_path, img["file"]) for img in batch]

        with exiftool.ExifToolHelper() as et:
            tags_data = [et.get_tags(filename, tags)[0]
                         for filename in filenames]

        tags_df = (pd.json_normalize(tags_data)
                   .assign(
                        source_file=lambda df: df["SourceFile"].map(
                            # TODO Issue with +"/" => test vs CLI discrepancy
                            # lambda SourceFile: SourceFile.replace(root+"/", "")
                            lambda SourceFile: SourceFile#.replace(root, "")
                        )
                    ))
        full_data = pd.concat([full_data, tags_df])

    if write:
        full_data.to_csv(name_out, index=False)

    return full_data
