from mdtools import __version__
from mdtools import convert

def test_version():
    assert __version__ == '0.1.0'
    
def test_md_to_coco_ct():
    convert.md_to_coco_ct("tests/test_images/test_images_output.json", 
                          "tests/test_images/test_images_output_coco_ct.json", 
                          "tests/test_images")