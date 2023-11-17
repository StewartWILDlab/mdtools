
import os
import pandas as pd

from tqdm import tqdm
from PIL import Image as Img

from mdtools.classes import COCOResult, MDResult

def crop_annotations(
	result: MDResult,
	directory: str,
	output_folder: str, 
	write = True):
	""" Crop annotations from a coco or md results
	"""

	cat_pd = pd.DataFrame.from_dict(result.coco_data["categories"])
	im_pd = pd.DataFrame.from_dict(result.coco_images())
	print(cat_pd)
	print(directory)
	print(output_folder)
	print(im_pd)

	for i, ann in enumerate(tqdm(result.coco_annotations())):

		if not ann["isempty"]:

			ann_cat_id = ann["category_id"]
			ann_cat = cat_pd.query(f'id == {ann_cat_id}')["name"].iloc[0]
			ann_im_id = ann["image_id"]
			ann_im_path = im_pd.query(f"id == '{ann_im_id}'")["file_name"].iloc[0]
			
			# CCT: [x,y,width,height]
			# (absolute, origin upper-left)
			# PIL: left, upper, right, and lower
			ann_bbox = ann["bbox"]
			ann_bbox_crop = (ann_bbox[0], ann_bbox[1],
							 ann_bbox[0] + ann_bbox[2], ann_bbox[1] + ann_bbox[3],)

			folder_path = os.path.join(output_folder, os.path.basename(directory) + "_crop", ann_cat)

			if not os.path.exists(folder_path):
				os.makedirs(folder_path)

			file_name = os.path.join(
					folder_path,
					ann["id"] + "_" + ann_cat + ".jpg"
				)

			if write & (not os.path.isfile(file_name)):

				img = Img.open(os.path.join(directory, ann_im_path)).crop(ann_bbox_crop)
				img.save(file_name)
				img.close()
