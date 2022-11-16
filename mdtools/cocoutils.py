"""Utility functions for conversion module."""

from datetime import datetime

from mdtools.classes import MDResult

def create_coco_info_dict(md_result: MDResult, version: float=1.0) -> dict:
	"""Create the info directory for COCO data."""
	info = {}
	
	md_time = md_result.md_info()["detection_completion_time"]
	info["year"] = datetime.strptime(md_time, '%Y-%m-%d %H:%M:%S').year
	
	info["version"] = version
	
	md_version = md_result.md_info()["detector_metadata"]["megadetector_version"]
	info["description"] = f"COCO json generated from MegaDetector {md_version} Results"

	return info
