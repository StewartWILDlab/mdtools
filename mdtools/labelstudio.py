"""Labelstudio output management miodule.

TODO.
"""

from datetime import datetime
import pandas as pd
import ast
import json
import os


def post_process_annotations(ls_json, data_str="data/local-files/?d="):

    c=0

    with open(ls_json, "r") as f:
        data = f.read()
    ls = json.loads(data)

    all_ann = pd.DataFrame()

    for ann in ls:

        all_bb = pd.DataFrame()
        bb = None

        # print(ann)

        if ann["total_predictions"] != 0:

            assert ann["total_predictions"] == 1
            assert ann["total_annotations"] == 1
            assert ann["cancelled_annotations"] == 0

            for bb in ann["annotations"]:

                # if bb["parent_prediction"] == None:
                #     print("here")

                if bb["result"]: # actual validated bbs

                    # print("validated bbs")

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
                        'value_rotation', 'image_rotation',# 'type',
                        'label_temp', 'tags_temp'])

                    # Modify the bb table for new manual annotations
                    if "manual" in list(bb['origin']):
                        
                        path_split = os.path.sep.join(bb.source_file[0].split(".")[0].split(os.path.sep)[1:])
                        
                        source_file_id = (path_split
                            .replace("\\", "/")
                            .replace("/", "_")
                            .replace(" ", "_"))
                        # print(source_file_id)
                        
                        # m_counter = None
                        m_counter = 0
                        the_id = None
                        
                        for index, row in bb.iterrows():
                            
                            if row['origin'] != 'manual':
                                pass
                            
                            elif row['origin'] == 'manual':
                                
                                if the_id is None:
                                    the_id = row['id']

                                if the_id == row['id']:
                                    bb.loc[index, 'id'] = source_file_id + '_M' + str(m_counter)
                                else:
                                    # print(m_counter)
                                    m_counter += 1
                                    bb.loc[index, 'id'] = source_file_id + '_M' + str(m_counter)
                                    the_id = row['id']

                        # print(bb)

                elif bb["prediction"]:

                    # print("********")
                    # print(bb)
                    # print("********")

                    pred = bb["prediction"]

                    # print("********")
                    # print(pred)
                    # print("********")

                    if pred["result"]:

                        # print("********")
                        # print("pred results, deleted bbs")
                        # print(ann)
                        # print("********")

                        # deleted bbs $$$ => check if prediction is empty first THEN if it is, assign as empty somehow?

                        bb = (
                            pd.json_normalize(bb["prediction"]["result"], sep = "_", max_level=1)
                            .assign(source_file = "/".join(ann["data"]["image"]
                            .replace(data_str, "").strip("/").split('/')[1:]))
                            .rename(columns={'from_name': 'variable'})
                        )

                        bb = bb.drop(columns=[
                            'value_rotation', 'image_rotation',# 'type', 'value_rectanglelabels',
                            ])

                        # print(bb)

                    else:

                        # print("********")
                        # print("empty pred results")
                        # print(ann)
                        # c+=1
                        # print(c)
                        # print("********")

                        bb = (
                            pd.json_normalize(bb, sep = "_", max_level=1)
                            .assign(source_file = "/".join(ann["data"]["image"]
                                .replace(data_str, "").strip("/").split('/')[1:]))
                            .rename(columns={'from_name': 'variable'})
                        )[['id', 'source_file']]


                        # print(bb)

                else: # actually empty images

                    # print("#########")
                    # print("empty")
                    # print(bb)
                    # print("#########")

                    bb = (
                        pd.json_normalize(bb, sep = "_", max_level=1)
                        .assign(source_file = "/".join(ann["data"]["image"]
                            .replace(data_str, "").strip("/").split('/')[1:]))
                        .rename(columns={'from_name': 'variable'})
                    )[['id', 'source_file']]

                    # print(bb)

                all_bb = pd.concat([all_bb, bb])

            all_ann = pd.concat([all_ann, all_bb])

        else:

            print("********")
            print("no predictions")
            print(ann)
            c+=1
            print(c)
            print("********")

            # print(bb)

            # bb = (
            #     pd.json_normalize(bb, sep = "_", max_level=1)
            #     .assign(source_file = "/".join(ann["data"]["image"]
            #         .replace(data_str, "").strip("/").split('/')[1:]))
            #     .rename(columns={'from_name': 'variable'})
            # )[['id', 'source_file']]

            # bb = pd.DataFrame({
            #     "id" : [ann['id']],
            #     "source_file" : ["/".join(ann["data"]["image"].replace(data_str, "").strip("/").split('/')[1:])]
            #     })

            # print(bb)

            # all_ann = pd.concat([all_ann, bb])

    if 'value_text' not in all_ann:
        all_ann['value_text'] = ''

    # print(all_ann)
    return all_ann

def get_name(df):

    # with open(df, "r") as f:
    #     data = f.read()
    # ls = json.loads(data)

    source_file_ex = df["source_file"].iloc[0]
    print(source_file_ex)
    proj = source_file_ex.split("/")[0]
    print(proj)
    dt = datetime.now().strftime("%Y_%m_%d-%p%I_%M_%S")

    print(df.head())

    return f"{proj}_{dt}"

# def clean_csv_output(ls_csv, out_file, data_str="data/local-files/?d=", write=True):

#     dat = pd.read_csv(ls_csv)

#     assert "image" in dat.keys()
#     assert "label_rectangles" in dat.keys()

#     dat["SourceFile"] = [
#         "/media/vlucet/TrailCamST/" + val.replace(data_str, "") for val in dat["image"]
#     ]
#     dat["label_rectangles"] = [
#         ast.literal_eval(val)[0] if isinstance(val, str) else {}
#         for val in dat["label_rectangles"]
#     ]
#     dat["label_rectangles"] = [
#         ast.literal_eval(val)[0] if isinstance(val, str) else {}
#         for val in dat["label_rectangles"]
#     ]
#     dat["bb_x"] = [val["x"] if val else 0 for val in dat["label_rectangles"]]
#     dat["bb_y"] = [val["y"] if val else 0 for val in dat["label_rectangles"]]
#     dat["bb_width"] = [val["width"] if val else 0 for val in dat["label_rectangles"]]
#     dat["bb_height"] = [val["height"] if val else 0 for val in dat["label_rectangles"]]
#     dat["bb_rotation"] = [
#         val["rotation"] if val else 0 for val in dat["label_rectangles"]
#     ]

#     dat["original_height"] = [
#         val["original_width"] if val else 0 for val in dat["label_rectangles"]
#     ]
#     dat["original_width"] = [
#         val["original_height"] if val else 0 for val in dat["label_rectangles"]
#     ]

#     dat["pred"] = [
#         val["rectanglelabels"][0] if val else "empty" for val in dat["label_rectangles"]
#     ]

#     if write:
#         dat.to_csv(out_file, index=False)

#     return dat


# def join_ls_to_csv(csv_file, ls_file, join_file, write=True, by="SourceFile"):

#     # TODO careful, this is duplication of code in join and should be changed

#     csv = pd.read_csv(csv_file)
#     csv["SourceFile"] = (
#         "/media/vlucet/TrailCamST/TrailCamStorage/" + csv["folder"] + "/" + csv["file"]
#     )
#     ls = pd.read_csv(ls_file)

#     joined = pd.merge(csv, ls, how="left", on=by)
#     if write:
#         joined.to_csv(join_file, index=False)

#     return joined


# post_process_annotations(
#     os.path.join(os.getcwd(), "../label_studio_downloads/P072.json")
# )
