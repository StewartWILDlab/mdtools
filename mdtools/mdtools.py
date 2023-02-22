"""CLI utility module."""

import click
import os
import json

from mdtools import convert as mdc
from mdtools import readexif as mdr
from mdtools import tabulate as mdt
from mdtools import labelstudio as mdl
from mdtools.classes import COCOResult, MDResult

import pandas as pd


@click.group()
def mdtools():
    """Create main command."""
    pass


@mdtools.command("convert")
@click.argument("output_format", type=click.Choice(["cct", "ls", "csv"],
                case_sensitive=False))
@click.argument("md_json", type=click.Path(exists=True))
@click.argument("directory", type=click.STRING)
@click.option("-ct", "--conf-threshold", default=0.1,
              help="Threshold under which predictions are removed",
              type=click.FLOAT,
              show_default=True)
@click.option("-ru", "--image-root-url", help="Label Studio local file url",
              default="/data/local-files/?d=",
              show_default=True)
@click.option("--write-coco", is_flag=True)
@click.option("--write-csv", is_flag=True)
@click.option("--write-ls", is_flag=True)
def convert(
    output_format,
    md_json,
    directory,
    conf_threshold,
    image_root_url,
    write_coco,
    write_csv,
    write_ls
):
    """Convert MD results to different formats."""
    # First, create object
    root = os.path.dirname(md_json)
    md_result = MDResult(root, directory, md_json)

    if output_format == "cct":

        coco_path_out = md_result.make_coco_write_path()
        cct = mdc.md_to_coco_ct(md_result)

        if write_coco:
            coco_path_out = cct.make_coco_write_path()

            if os.path.isfile(coco_path_out):
                print(f"File {coco_path_out} already exist, " +
                      "overwriting file")

            cct.to_json()
        else:
            print(cct)

    elif output_format == "ls":

        coco_path_out = md_result.make_coco_write_path()
        ls_path_out = md_result.make_ls_write_path()
        csv_path_out = md_result.make_csv_write_path()

        if write_coco:
            if os.path.isfile(coco_path_out):
                print(f"File {coco_path_out} already exist, " +
                      "overwriting file")
            cct = mdc.md_to_coco_ct(md_result)
            cct.to_json()
        else:
            if os.path.isfile(coco_path_out):
                print(f"File {coco_path_out} already exist: " +
                      "set --write-coco to overwrite")
                with open(coco_path_out, "r") as f:
                    cct_data = json.loads(f.read())
                cct = COCOResult(md_result.root, md_result.folder,
                                 md_result.md_file, coco_data=cct_data)
            else:
                print("No COCO file, set --write-coco to create")

        if write_csv:
            if os.path.isfile(csv_path_out):
                print(f"File {csv_path_out} already exist, " +
                      "overwriting file")
            tab = mdt.tabulate_md(md_result, write=write_csv)
        else:
            if os.path.isfile(csv_path_out):
                print(f"File {csv_path_out} already exist: " +
                      "set --write-csv to overwrite")
                tab = pd.read_csv(csv_path_out)
            else:
                print("No CSV file, set --write-csv to create")

        if write_ls:
            if os.path.isfile(ls_path_out):
                print(f"File {ls_path_out} already exist, " +
                      "overwriting file")
            ls = mdc.coco_ct_to_ls(cct, tab, conf_threshold, write_ls,
                                   image_root_url)
        else:
            if os.path.isfile(ls_path_out):
                print(f"File {ls_path_out} already exist: " +
                      "set --write-ls to overwrite")
            else:
                print("No LS file, set --write-ls to create")

    elif output_format == "csv":

        print("Not directly implemented")
        # TODO re implement
        # mdc.md_to_csv(click.format_filename(md_json), read_exif, write_csv)


@mdtools.command("readexif")
@click.argument("md_json", type=click.Path(exists=True))
@click.option("-ws", "--write-csv", help="", default=True, show_default=True)
def readexif(md_json, write_csv):
    """Read exif from string filepath."""
    mdr.read_exif_from_md(md_json, write=write_csv)

@mdtools.command("postprocess")
@click.argument("ls_json", type=click.Path(exists=True))
@click.option("--write-csv", is_flag=True)
def post_process(ls_json, write_csv):
    """Post process json from label studio."""

    print(ls_json)

    base = mdl.get_name(ls_json)
    test = mdl.post_process_annotations(ls_json)
    if write_csv:
        test.to_csv(f"{base}_output.csv", index=False)

    pass
