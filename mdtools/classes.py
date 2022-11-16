"""mdtools classes for MegaDetector results."""

import os
import json


class MDResult:
    """Megadetector result class."""

    def __init__(self, root: str, folder: str, md_file: str):
        """Initialize the class."""
        # Check if dir
        if not os.path.isdir(root):
            raise Exception("Result root must be a directory.")

        # Provided
        self.root: str = root
        self.folder: str = folder
        self.md_file: str = md_file

        # Computed
        self.md_filepath: str = os.path.join(self.root, self.md_file)

        # Properties
        self._default_md_categories = {'1': 'animal',
                                       '2': 'person',
                                       '3': 'vehicle'}
        # self._format: str="MD"

        # Created
        with open(self.md_filepath, "r") as f:
            md_data = json.loads(f.read())
        self.md_data: dict = md_data

        # Check categories sanity
        self.check_md_categories()

    # Property methods
    @property
    def default_md_categories(self) -> dict:
        """Property default categories."""
        return self._default_md_categories

    # @property
    # def __format__(self) -> str:
    #     """Property default categories."""
    #     return(self._format)

    # Utils methods
    def check_md_categories(self) -> None:
        """Check whether the categories are valid."""
        if not self.md_categories() == self._default_md_categories:
            raise Exception("Categories do not match megadetector defaults")

    def __repr__(self) -> str:
        """Represent the class."""
        return ("MD Results in MD format: \n" +
                f"  * MD file @ '{self.md_filepath}'")

    # Data methods
    def md_images(self) -> dict:
        """Get images dict."""
        return self.md_data["images"]

    def md_numimages(self) -> int:
        """Compute number of images in the result."""
        return len(self.md_images())

    def md_categories(self) -> dict:
        """Get categories dict."""
        return self.md_data["detection_categories"]

    def md_info(self) -> dict:
        """Get info dict."""
        return self.md_data["info"]


class COCOResult(MDResult):
    """Megadetector coco class (wrap around a json)."""

    def __init__(self, root: str, folder: str, md_file: str,
                 coco_filepath: str, coco_data: dict = {}):
        """Initialize the class."""
        super().__init__(root, folder, md_file)

        # Provided
        self.coco_file: str = os.path.basename(coco_filepath)
        self.coco_data: dict = coco_data

        # Computed
        self.coco_filepath: str = coco_filepath

        # TODO: if empty, maybe load from file?

        # # Property
        # self._format: str="JSON"

    # Utils methods
    def __repr__(self) -> str:
        """Represent the class."""
        rep = ("MD Results in COCO format: \n" +
               f" * MD file   @ '{self.md_filepath}' \n" +
               f" * COCO file @ '{self.coco_filepath}'")
        return rep

    # Data methods
    def annotations(self) -> dict:
        """Get annotations dict."""
        return self.coco_data["annotations"]

    def numannotations(self) -> int:
        """Compute number of images in the result."""
        return len(self.annotations())
