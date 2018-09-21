import unittest
from compiler.PRISMParser import ModelConstructor
from PathHelper import get_prism_model_dir
from compiler.LTLParser import LTLParserFacade as LTLParser
from os.path import isdir
import logging
import sys


class ModelTestBase(unittest.TestCase):

    def setUp(self):
        self.constructor = ModelConstructor()
        self.ltl_parser = LTLParser()
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(sys.stdout)
        self.logger.setLevel(logging.INFO)
        path = self._get_model_root_path()
        # check whether path exist
        if not isdir(path):
            self.logger.error("model path not exist: %s", path)
        else:
            self.constructor.set_base_dir(base_dir=path)
        self._model = self.constructor.parse(self._get_model_name())

    def _get_model_name(self):
        '''
        return the name of model file(extension not included)
        supposed to be implemented by subclass
        :return: string
        '''
        pass

    def _get_model_root_path(self):
        '''
        could be overrided if necessary
        :return:
        '''
        return get_prism_model_dir()
