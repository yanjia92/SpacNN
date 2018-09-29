# -*- coding:utf-8 -*-

import unittest
from compiler.PRISMParser import ModelConstructor
from PathHelper import *
from compiler.LTLParser import LTLParserFacade as LTLParser
from os.path import *
import logging
import sys
from compiler.RenamingHelper import RenamingHelper


class ModelTestBase(unittest.TestCase):

    PRISM_SUFFIX = ".prism"

    def setUp(self):
        self._constructor = ModelConstructor()
        self._ltl_parser = LTLParser()
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(sys.stdout)
        self.logger.setLevel(logging.INFO)
        if not isdir(get_prism_model_dir()):
            raise Exception("model root path not exist: {}".format(get_prism_model_dir()))
        self._constructor.set_base_dir(self._get_model_root_path())
        model_path = self._get_model_root_path() + get_sep() + self._get_model_name() + self.PRISM_SUFFIX
        if not isfile(model_path):
            raise Exception("Model file {} not exist".format(model_path))
        self._renaming_helper = RenamingHelper(model_path)
        self._renaming_helper.rewrite()
        rewritten_path = self._renaming_helper.export()
        filename = basename(rewritten_path)
        filename = splitext(filename)[0]
        self._model = self._constructor.parse(filename)
        self._param_map = {}

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

    def _set_parameters(self, name, values):
        '''
        store parameters in this object
        :param name: parameter name
        :param values: list of value
        :return:
        '''
        self._param_map[name] = values

    def _set_parameter(self, k, v):
        '''
        设置参数到_checker._constants
        :param k: parameter name
        :param v: parameter value
        :return:
        '''
        self._model.set_constant(k, v)

    def get_model(self):
        return self._model