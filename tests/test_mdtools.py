from mdtools.classes import *
from mdtools.convert import *
from mdtools.tabulate import *


def test_pipeline():
    res = MDResult("tests/test_images/",
                   "test_folder", "test_folder_output.json")
    assert isinstance(res, MDResult)

    res_tab = tabulate_md(res, write=True)
    assert isinstance(res_tab, pd.DataFrame)

    coco_res = md_to_coco_ct(res, write=True)
    assert isinstance(coco_res, COCOResult)

    ls = coco_ct_to_ls(coco_res, res_tab, write=True)
    assert isinstance(ls, list)
