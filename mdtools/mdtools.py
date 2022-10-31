import click

from mdtools import convert as mdc
from mdtools import readexif as mdr


@click.group
def mdtools():
    pass


@mdtools.command("convert")
@click.argument(
    "output_format", type=click.Choice(["cct", "ls", "csv"], case_sensitive=False)
)
@click.argument("md_json", type=click.Path(exists=True))
@click.option(
    "-ct",
    "--conf-threshold",
    default=0.1,
    help="Threshold under which predictions are removed",
    type=click.FLOAT,
    show_default=True,
)
@click.option(
    "-bd",
    "--image-base-dir",
    help="Directory containing the raw images",
    default=".",
    show_default=True,
)
@click.option(
    "-ru",
    "--image-root-url",
    help="Label Studio local file url",
    default="/data/local-files/?d=",
    show_default=True,
)
@click.option("-wc", "--write-coco", help="", default=False, show_default=True)
@click.option("-wl", "--write-ls", help="", default=True, show_default=True)
@click.option("-re", "--read-exif", help="", default=True, show_default=True)
@click.option("-ws", "--write-csv", help="", default=True, show_default=True)
@click.option("-oc", "--output-json-coco", help="", default=None)
@click.option("-ol", "--output-json-ls", help="", default=None)
def convert(
    output_format,
    md_json,
    conf_threshold,
    image_base_dir,
    image_root_url,
    write_coco,
    output_json_coco,
    write_ls,
    read_exif,
    output_json_ls,
    write_csv,
):

    if output_format == "cct":

        mdc.md_to_coco_ct(
            click.format_filename(md_json), output_json_coco, image_base_dir, write_coco
        )

    elif output_format == "ls":

        mdc.md_to_ls(
            click.format_filename(md_json),
            conf_threshold,
            image_base_dir,
            image_root_url,
            write_coco,
            output_json_coco,
            write_ls,
            output_json_ls,
        )

    elif output_format == "csv":

        mdc.md_to_csv(click.format_filename(md_json), read_exif, write_csv)

@mdtools.command("readexif")
@click.argument("md_json", type=click.Path(exists=True))
@click.option("-ws", "--write-csv", help="", default=True, show_default=True)
def readexif(
    md_json,
    write_csv
):
    mdr.read_exif_from_md(md_json, tags='all', write=write_csv)