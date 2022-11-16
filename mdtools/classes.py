"""mdtools classes for MegaDetector results."""

import os
import json
import pandas as pd


class MDResult:
    """Megadetector result class (wrap around a json)."""

    def __init__(self, root: str, folder: str, file: str):
        """Initialize the class."""        
        # Check if dir
        if not os.path.isdir(root):
            raise Exception("Result root must be a directory.")

        # Property
        self._defaultcategories = {'1': 'animal', '2': 'person', '3': 'vehicle'}

        # Provided
        self.root: str = root
        self.folder: str = folder
        self.file: str = file

        # Created
        self.filepath: str = os.path.join(self.root, self.file)
        with open(self.filepath, "r") as f:
            data = json.loads(f.read()) 
        self.data: dict = data
        
        # Future placeholders
        self.annotations: dict = {}
        self.predictions: dict = {}

        # Check categories sanity
        self.check_categories()

    # Property methods
    @property
    def defaultcategories(self) -> dict:
        """Property default categories."""
        return(self._defaultcategories)

    # Utils methods
    def check_categories(self) -> None:
        """Check whether the categories are valid."""
        if not self.categories() == self._defaultcategories:
            raise Exception("Categories do not match megadetector defaults")

    def __repr__(self) -> str:
        """Represent the class."""
        return f"MD Result with root '{self.root}', folder '{self.folder}', and file '{self.file}' "

    def images(self) -> dict:
        """Get images dict."""
        return self.data["images"]

    def numimages(self) -> int:
        """Compute number of images in the result."""
        return len(self.images())

    def categories(self) -> dict:
        """Get categories dict."""
        return self.data["detection_categories"]

    def info(self) -> dict:
        """Get info dict."""
        return self.data["info"]

    # Write methods
    def write(self, format: str):
        """Write data out."""
        # TODO: check attributes, write if possible
        pass

    # Plot methods?
    # TODO


# class CTSurvey:
#     """Megadetector survey class (wrap around a list of jsons)."""

#     def __init__(self, root, results=[]):
#         """Initialize the class."""
#         # Check if nor dir
#         if not os.path.isdir(root):
#             raise Exception("Survey root must be a directory.")

#         self.root = root
#         self.results = results

#     def __repr__(self) -> str:
#         """Represent the class."""
#         return f"CT Survey with root '{self.root}' and {len(self.results)} results"

#     def load_from_folder_names(self, pattern):
#         """Load all the folders in a survey based on a file pattern."""
#         folders_paths = [f.path for f in os.scandir(self.root) if f.is_dir()]
#         results_paths = [(f + pattern) for f in folders_paths if os.path.isfile(f + pattern)]

#         if len(results_paths) == 0:
#             raise Exception("Not result files found.")
#         else:
#             results_files = [os.path.basename(f_path) for f_path in results_paths]
#             self.results = list(
#                 map(
#                     lambda x, y: MDResult(self.root, os.path.basename(x), y),
#                     folders_paths,
#                     results_files,
#                 )
#             )
