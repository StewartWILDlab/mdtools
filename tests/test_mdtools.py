from mdtools.classes import *
from mdtools.convert import *
from mdtools.tabulate import *


def test_pipeline():
    res = MDResult("tests/test_images/",
                   "test_folder", "test_folder_output.json")
    assert isinstance(res, MDResult)

    res_tab_test = pd.read_csv("tests/test_images/test_folder_output.csv")
    res_tab = tabulate_md(res, write=False)
    assert isinstance(res_tab, pd.DataFrame)
    assert pd.DataFrame.equals(
        res_tab.loc[:, res_tab.columns != 'bbox'],
        res_tab_test.loc[:, res_tab_test.columns != 'bbox'])

    with open("tests/test_images/test_folder_output_coco.json", "r") as f:
        coco_res_test = json.loads(f.read())
    coco_res = md_to_coco_ct(res)
    assert isinstance(coco_res, COCOResult)
    assert coco_res.coco_data == coco_res_test

    with open("tests/test_images/test_folder_output_ls.json", "r") as f:
        ls_test = json.loads(f.read())
    ls = coco_ct_to_ls(coco_res, res_tab, write=False)
    assert isinstance(ls, list)
    assert ls == ls_test
