"""Labelstudio output management miodule.

TODO.
"""

import pandas as pd
import ast
import json
import os


def post_process_annotations(ls_json, data_str="data/local-files/?d="):

    with open(ls_json, "r") as f:
        data = f.read()
    ls = json.loads(data)

    all_ann = pd.DataFrame()

    for ann in ls:

        all_bb = pd.DataFrame()

        assert ann["total_predictions"] == 1
        assert ann["total_annotations"] == 1
        assert ann["cancelled_annotations"] == 0

        print(ann["id"])
        print(ann["data"]["image"])

        for bb in ann["annotations"]:
            
            all_res = pd.DataFrame()

            if bb["result"]:
                bb = (
                    pd.json_normalize(bb["result"], sep = "_", max_level=1)
                    .assign(source_file = "/".join(ann["data"]["image"]
                        .replace(data_str, "").strip("/").split('/')[1:]))
                    .rename(columns={'from_name': 'variable'})
                )

                bb["label_temp"] = (
                    [val[0] if isinstance(val, list) else "" for val in bb["value_rectanglelabels"]]
                )
                bb["tags_temp"] = (
                    [val[0] if isinstance(val, list) else "" for val in bb["value_choices"]]
                )
                bb["tag"] = (
                    [bb['label_temp'][i] if bb['label_temp'][i] != "" else bb['tags_temp'][i] 
                    for i in range(bb.shape[0])]    
                )

                bb = bb.drop(columns=['value_rectanglelabels', 'value_choices', 
                    'value_rotation', 'image_rotation', 'type', 
                    'label_temp', 'tags_temp'])
                # print(bb)

                all_res = pd.concat([all_res, bb])

            else:
                print("EMPTY")
            # print(bb['id'])
            # if ann_set['result']:
            # print(bb['result'])

            all_bb = pd.concat([all_bb, all_res])

        all_ann = pd.concat([all_ann, all_bb])

    print(all_ann)
    return all_ann


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
    os.path.join(os.getcwd(), "../label_studio_downloads/P072.json")
)
