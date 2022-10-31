import exiftool
import json
import os
import tqdm
import pandas as pd


def read_exif_from_md(md_json, tags='all', write=True):
    """Convert md_json to CSV format

    Extract EXIF information from the md_json.

    """
    # TODO fix the tags handling
    the_tags = ["File:FileName", "File:Directory",
                "EXIF:DateTimeOriginal", "MakerNotes:DateTimeOriginal",
                "MakerNotes:DayOfWeek", "MakerNotes:MoonPhase",
                "MakerNotes:AmbientTemperature", "MakerNotes:MotionSensitivity",
                "MakerNotes:BatteryVoltage", "MakerNotes:BatteryVoltageAvg",
                "MakerNotes:UserLabel"]

    with open(md_json, "r") as f:
        md = json.loads(f.read())
    folder = os.path.basename(md_json).split("_")[0]

    full_data = pd.DataFrame()

    for image in tqdm(md["images"]):
        if "detections" in image.keys():

            filename = os.path.join(
                md_json.split("_")[0], image["file"])

            with exiftool.ExifToolHelper() as et:
                tags = et.get_tags(filename, the_tags)[0]

            tags_df = pd.json_normalize(tags)
            full_data = pd.concat([full_data, dat])

        else:
            print("Error on file %s" % image["file"])

    if write:
        name_out = os.path.join(os.path.dirname(
            md_json), folder) + "_output.csv"
        full_data.to_csv(name_out)

    return full_data
