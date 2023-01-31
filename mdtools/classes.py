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

    # Utils methods
    def check_md_categories(self) -> None:
        """Check whether the categories are valid."""
        if not self.md_categories() == self._default_md_categories:
            raise Exception("Categories do not match megadetector defaults")

    def __repr__(self) -> str:
        """Represent the class."""
        return ("MD Results in MD format: \n" +
                f"  * MD file @ '{self.md_filepath}'")

    def make_coco_write_path(self) -> str:
        """Create the path to write coco out as json."""
        image_base_dir = os.path.join(self.root, self.folder)
        return image_base_dir + "_output_coco.json"

    def make_ls_write_path(self) -> str:
        """Create the path to write coco out as json."""
        image_base_dir = os.path.join(self.root, self.folder)
        return image_base_dir + "_output_ls.json"

    def make_csv_write_path(self) -> str:
        """Create the path to write coco out as json."""
        image_base_dir = os.path.join(self.root, self.folder)
        return image_base_dir + "_output.csv"

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
                 coco_data: dict = {}):
        """Initialize the class."""
        super().__init__(root, folder, md_file)

        # Provided
        self.coco_data: dict = coco_data

        # Computed
        self.coco_filepath: str = ""
        self.coco_file: str = ""

        # TODO: if empty, maybe load from file?

    # Utils methods
    def __repr__(self) -> str:
        """Represent the class."""
        # TODO check if coco_filepath is not equal to ""
        rep = ("MD Results in COCO format: \n" +
               f" * MD file   @ '{self.md_filepath}' \n" +
               f" * COCO file @ '{self.coco_filepath}'")
        return rep

    def to_json(self) -> bool:
        """Write to JSON."""
        path = self.make_coco_write_path()
        self.coco_filepath = path
        self.coco_file: str = os.path.basename(path)
        print(
            f"Writing .json file with {len(self.coco_images())} images, "
            + f"{len(self.coco_annotations())} annotations, and "
            + f"{len(self.coco_categories())} categories"
        )
        json.dump(self.coco_data, open(path, "w"), indent=2)
        return True

    # Data methods
    def coco_annotations(self) -> dict:
        """Get annotations dict."""
        return self.coco_data["annotations"]

    def coco_numannotations(self) -> int:
        """Compute number of images in the result."""
        return len(self.coco_annotations())

    def coco_images(self) -> dict:
        """Get images dict."""
        return self.coco_data["images"]

    def coco_numimages(self) -> int:
        """Compute number of images in the result."""
        return len(self.md_images())

    def coco_categories(self) -> dict:
        """Get categories dict."""
        return self.coco_data["categories"]

    def coco_info(self) -> dict:
        """Get info dict."""
        return self.coco_data["info"]
