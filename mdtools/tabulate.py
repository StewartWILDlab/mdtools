"""CSV module."""

import os
import pandas as pd
from tqdm import tqdm

from mdtools.classes import MDResult, COCOResult
from mdtools.readexif import read_exif_from_md

# TODO consider making a MDResultTable class with a "has_exif" property


def tabulate_md(md_result: MDResult, include_exif: bool = True,
                batchsize: int = 100, write=False, repeat: bool = False) -> pd.DataFrame:
    """Convert md to csv."""
    dat = pd.json_normalize(md_result.md_images())
    full_data = pd.DataFrame()

    for image in tqdm(md_result.md_images()):
        if "detections" in image.keys():

            if image["detections"] is not None:

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
                        .assign(conf="0")
                        .assign(bbox="NA")
                        .assign(file=image["file"])
                        .assign(folder=md_result.folder)
                        .assign(source_file=os.path.join(md_result.folder,
                                                         image["file"]))
                    )

            full_data = pd.concat([full_data, dat])

        else:
            print("Error on file %s" % image["file"])

    if include_exif:
        exif_data = read_exif_from_md(md_result, batchsize=batchsize)
        full_data = pd.merge(full_data, exif_data, how="left",
                             on="source_file")

    if write:
        full_data.to_csv(md_result.make_csv_write_path(repeat = repeat), index=False)

    return full_data

# def tabulate_coco(coco_result: COCOResult, include_exif: bool = True,
#                   batchsize: int = 100, write=False) -> pd.DataFrame:
#     """Convert coco to csv."""
#     full_data = pd.DataFrame()

#     img_full_data = pd.DataFrame()
#     for image in tqdm(coco_result.coco_images()):

#         img_dat = (
#             pd.json_normalize(image)
#             .rename(columns={'id':'image_id'})
#             .assign(file=image["file_name"])
#             .assign(folder=coco_result.folder)
#             .assign(source_file=os.path.join(coco_result.folder,
#                                              image["file_name"]))
#         )
#         img_full_data = pd.concat([img_full_data, img_dat])

#     ann_full_data = pd.DataFrame()
#     for ann in tqdm(coco_result.coco_annotations()):

#         ann_dat = (
#             pd.json_normalize(ann)
#         )
#         ann_full_data = pd.concat([ann_full_data, ann_dat])

#     print(img_full_data.shape)
#     print(ann_full_data.shape)

#     full_data = pd.merge(img_full_data, ann_full_data, how='left', on='image_id')
#     print(full_data.shape)

#     # assert  

#     if include_exif:
#         exif_data = read_exif_from_md(coco_result, batchsize=batchsize)
#         full_data = pd.merge(full_data, exif_data, how="right",
#                              on="source_file")
#     print(full_data.shape)

#     if write:
#         full_data.to_csv(coco_result.make_csv_write_path(), index=False)

#     return full_data
