from mdtools import __version__
from mdtools.convert import *

def test_version():
    assert __version__ == '0.1.0'
    
def test_md_to_coco_ct():
    ret = md_to_ls("tests/test_images/test_images_output.json",  "tests/test_images", 
                   output_json_coco = "tests/test_images/test_images_output_coco_ct.json", 
                   output_json_ls="tests/test_images/test_images_output_ls.json")
    assert isinstance(ret, dict)