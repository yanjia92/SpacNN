from checker.Checker import Checker
from compiler.PRISMParser import ModelConstructor


class Manager(object):
    def __init__(self):
        self.mdl_parser = ModelConstructor()
        self.model = None

    def input_file(self, file_path):
        self.model = self.mdl_parser.parseModelFile(file_path)

