"""Scrap module."""
# def md_to_ls(
#     md_json,
#     conf_threshold=0.1,
#     image_base_dir=".",
#     image_root_url="/data/local-files/?d=",
#     write_coco=False,
#     output_json_coco=None,
#     write_ls=False,
#     output_json_ls=None,
#     use_score_table=False,
#     score_table="",
# ):

#     if not isinstance(output_json_coco, str):
#         output_json_coco = os.path.splitext(md_json)[0] + "_coco.json"

#     if not isinstance(output_json_ls, str):
#         output_json_ls = os.path.splitext(md_json)[0] + "_ls.json"

#     coco_ct = md_to_coco_ct(md_json, output_json_coco, image_base_dir, write=write_coco)
#     ls = coco_ct_to_ls(
#         coco_ct,
#         output_json_ls,
#         conf_threshold,
#         image_root_url,
#         write=write_ls,
#         use_score_table=use_score_table,
#         score_table=score_table,
#     )
#     return ls

#         # generate and save labeling config
#     if generate_config_file:
#         label_config_file = output_coco.replace(".json", "") + ".label_config.xml"
#         print(f"Saving Label Studio XML to {label_config_file}")
#         generate_label_config(categories, tags, to_name, from_name, label_config_file)