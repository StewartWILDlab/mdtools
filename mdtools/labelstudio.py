"""Labelstudio output management miodule.

TODO.
"""

import pandas as pd
import ast
import json
import os


def post_process_annotations(ls_json):
    
    with open(ls_json, "r") as f:
        data = f.read()
    ls = json.loads(data)

    for ann in ls[78:82]:

        print(ann['id'])
        # print(ann['annotations'])
        print(ann['data'])

        for bb in ann['annotations']:
            pass

            if bb['result']:
                bb = pd.json_normalize(bb['result'])
                print(bb)

            else:
                print("EMPTY")
            #print(bb['id'])
            #if ann_set['result']:
            #print(bb['result'])
    print(ls[0].keys())


def clean_csv_output(ls_csv, out_file, data_str="data/local-files/?d=", write=True):

    dat = pd.read_csv(ls_csv)

    assert "image" in dat.keys()
    assert "label_rectangles" in dat.keys()

    dat["SourceFile"] = [
        "/media/vlucet/TrailCamST/" + val.replace(data_str, "") for val in dat["image"]
    ]
    dat["label_rectangles"] = [
        ast.literal_eval(val)[0] if isinstance(val, str) else {}
        for val in dat["label_rectangles"]
    ]
    dat["label_rectangles"] = [
        ast.literal_eval(val)[0] if isinstance(val, str) else {}
        for val in dat["label_rectangles"]
    ]
    dat["bb_x"] = [val["x"] if val else 0 for val in dat["label_rectangles"]]
    dat["bb_y"] = [val["y"] if val else 0 for val in dat["label_rectangles"]]
    dat["bb_width"] = [val["width"] if val else 0 for val in dat["label_rectangles"]]
    dat["bb_height"] = [val["height"] if val else 0 for val in dat["label_rectangles"]]
    dat["bb_rotation"] = [
        val["rotation"] if val else 0 for val in dat["label_rectangles"]
    ]

    dat["original_height"] = [
        val["original_width"] if val else 0 for val in dat["label_rectangles"]
    ]
    dat["original_width"] = [
        val["original_height"] if val else 0 for val in dat["label_rectangles"]
    ]

    dat["pred"] = [
        val["rectanglelabels"][0] if val else "empty" for val in dat["label_rectangles"]
    ]

    if write:
        dat.to_csv(out_file, index=False)

    return dat


def join_ls_to_csv(csv_file, ls_file, join_file, write=True, by="SourceFile"):

    # TODO careful, this is duplication of code in join and should be changed

    csv = pd.read_csv(csv_file)
    csv["SourceFile"] = (
        "/media/vlucet/TrailCamST/TrailCamStorage/" + csv["folder"] + "/" + csv["file"]
    )
    ls = pd.read_csv(ls_file)

    joined = pd.merge(csv, ls, how="left", on=by)
    if write:
        joined.to_csv(join_file, index=False)

    return joined


post_process_annotations(
    os.path.join(os.getcwd(), "../../label_studio_downloads/P072.json")
)
