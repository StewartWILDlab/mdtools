"""Utility functions for conversion module."""

from datetime import datetime

from mdtools.classes import MDResult


def create_coco_info_dict(md_result: MDResult, version: float = 1.0) -> dict:
    """Create the info directory for COCO data."""
    coco_info = {}
    md_info = md_result.md_info()

    md_time = md_info["detection_completion_time"]
    coco_info["year"] = datetime.strptime(md_time, '%Y-%m-%d %H:%M:%S').year

    coco_info["version"] = version

    md_version = md_info["detector_metadata"]["megadetector_version"]
    coco_info["description"] = ("COCO json generated from MegaDetector " +
                                f"{md_version} Results")

    return coco_info
