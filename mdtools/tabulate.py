"""CSV module."""

import os
import pandas as pd
from tqdm import tqdm

from mdtools.classes import MDResult
from mdtools.readexif import read_exif_from_md

# TODO consider making a MDResultTable class with a "has_exif" property


def tabulate_md(md_result: MDResult, include_exif: bool = True,
                batchsize: int = 100, write=False) -> pd.DataFrame:
    """Convert md to csv."""
    dat = pd.json_normalize(md_result.md_images())
    full_data = pd.DataFrame()

    for image in tqdm(md_result.md_images()):
        if "detections" in image.keys():

            if len(image["detections"]) != 0:

                dat = (
                    pd.json_normalize(image["detections"])
                    .assign(file=image["file"])
                    .assign(folder=md_result.folder)
                    .assign(source_file=os.path.join(md_result.folder,
                                                     image["file"]))
                    .assign(
                        category=lambda df: df["category"].map(
                            lambda category: int(category)
                        )
                    )
                )

            else:

                dat = (
                    pd.DataFrame({"category": [0]})
                    .assign(conf="NA")
                    .assign(bbox="NA")
                    .assign(file=image["file"])
                    .assign(folder=md_result.folder)
                    .assign(source_file=os.path.join(md_result.folder,
                                                     image["file"]))
                )

            full_data = pd.concat([full_data, dat])

        else:
            print("Error on file %s" % image["file"])

    if write:
        base_path = md_result.root + md_result.folder
        name_out = base_path + "_output.csv"
        full_data.to_csv(name_out, index=False)

    if include_exif:
        exif_data = read_exif_from_md(md_result, batchsize=batchsize)
        print(exif_data)
        full_data = pd.merge(full_data, exif_data, how="left",
                             on="source_file")

    return full_data
