from mdtools.convert import *


def test_md_to_ls():
    ret = md_to_ls("tests/test_images/test_images_output.json", 0.1, "tests/test_images",
                   write_coco = True, write_ls = True,
                   output_json_coco="tests/test_images/test_images_output_coco_ct.json",
                   output_json_ls="tests/test_images/test_images_output_ls.json")
    assert isinstance(ret, list)
    assert isinstance(ret[0], dict)
