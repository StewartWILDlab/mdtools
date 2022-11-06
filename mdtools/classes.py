import os
import json


class CTSurvey:
    def __init__(self, root, results=[]):

        if not os.path.isdir(root):
            raise Exception("Survey root must be a directory.")

        self.root = root
        self.results = results
        
    def __repr__(self):
        return f"CT Survey with root '{self.root}' and {len(self.results)} results"

    def load_from_folder_names(self, pattern):

        folders_paths = [f.path for f in os.scandir(self.root)
                         if f.is_dir()]
        results_paths = [(f + pattern) for f in folders_paths if
                         os.path.isfile(f + pattern)]

        if len(results_paths) == 0:
            raise Exception("Not result files found.")
        else:
            results_files = [os.path.basename(f_path)
                             for f_path in results_paths]
            self.results = list(map(lambda x, y: MDResult(self.root, os.path.basename(x), y),
                                    folders_paths, results_files))


class MDResult:
    def __init__(self, root, folder, file):

        if not os.path.isdir(root):
            raise Exception("Result root must be a directory.")

        self.root = root
        self.folder = folder
        self.file = file

        # Property
        self._format = "json"
        
    def __repr__(self):
        return f"MD Result with root '{self.root}', folder '{self.folder}', and file '{self.file}' "

    @property
    def format(self):
        return self._format

    def update_format(self, new_format):
        self._format = new_format

    def convert(self):
        pass
