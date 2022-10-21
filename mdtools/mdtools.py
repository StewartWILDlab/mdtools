import click

from mdtools import convert as mdc


@click.group()
def mdtools():
    pass


@mdtools.command()
@click.argument("md_json", 
                type=click.Path(exists=True))
@click.argument("conf_threshold", 
                type=click.FLOAT)
@click.option("-bd", "--image-base-dir",
              help="Base directory of images", 
              default=".")
@click.option("-ru", "--image-root-url",
              help="", default="/data/local-files/?d=")
@click.option("-wc", "--write-coco",
              help="", default=True)
@click.option("-wl", "--write-ls",
              help="", default=True)
@click.option("-oc", "--output-json-coco",
              help="", default=None)
@click.option("-ol", "--output-json-ls",
              help="", default=None)
def convert(md_json, conf_threshold, image_base_dir, image_root_url, 
            write_coco, output_json_coco, write_ls, output_json_ls):
    mdc.md_to_ls(click.format_filename(md_json),
                 conf_threshold,
                 image_base_dir,
                 image_root_url,
                 write_coco,
                 output_json_coco,
                 write_ls,
                 output_json_ls)
