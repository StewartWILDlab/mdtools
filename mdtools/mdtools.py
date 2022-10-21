import click

from mdtools import convert as mdc


@click.group
def mdtools():
    pass


@mdtools.command('convert')
@click.argument("format",
                type=click.Choice(['cct', 'ls', 'csv'], case_sensitive=False))
@click.argument("md_json",
                type=click.Path(exists=True))
@click.option("-ct", "--conf-threshold", default=0.1,
              type=click.FLOAT)
@click.option("-bd", "--image-base-dir",
              help="Base directory of images",
              default=".")
@click.option("-ru", "--image-root-url",
              help="", default="/data/local-files/?d=")
@click.option("-wc", "--write-coco",
              help="", default=False)
@click.option("-wl", "--write-ls",
              help="", default=True)
@click.option("-oc", "--output-json-coco",
              help="", default=None)
@click.option("-ol", "--output-json-ls",
              help="", default=None)
def convert(out, md_json, conf_threshold, image_base_dir, image_root_url,
            write_coco, output_json_coco, write_ls, output_json_ls):

    if (format == "cct"):

        mdc.md_to_coco_ct(click.format_filename(md_json),
                          output_json_coco,
                          image_base_dir, 
                          write_coco)

    elif (format == "ls"):

        mdc.md_to_ls(click.format_filename(md_json),
                     conf_threshold,
                     image_base_dir,
                     image_root_url,
                     write_coco,
                     output_json_coco,
                     write_ls,
                     output_json_ls)

    elif (format == "csv"):

        mdc.md_to_csv(click.format_filename(md_json))
