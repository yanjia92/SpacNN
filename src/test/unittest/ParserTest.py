# -*- coding: utf-8 -*-
import unittest
from compiler.PRISMParser import ModelConstructor
from util.CsvFileHelper import *
from util.util import interval
from checker.Checker import Checker
from compiler.LTLParser import LTLParser
from module.Module import Constant
import logging
import sys
from math import fabs
from experiment.ExperimentWrapper import ExperimentWrapper


class ParserTest(unittest.TestCase):
    '''
    单元测试：测试parser出的模型运转良好
    '''

    def __init__(self, model_path, ltl, path_length, params,  checking_delta=0.01, prism_data_path=None):
        '''
        :param model_path:
        :param ltl:
        :param path_length:
        :param params: value of unsure parameters: map with key to be param_name, value to be value list
        :param prism_data_path:
        '''
        unittest.TestCase.__init__(self)
        # todo check path exist and is a file
        self.model_path = model_path
        self.prism_data_path = prism_data_path
        self.ltl = ltl
        self.parsed_ltl = None
        self.modelConstructor = ModelConstructor()
        self.ltl_parser = LTLParser().build_parser()
        self.duration = path_length
        self.checking_delta = checking_delta
        self.params = params

    def setUp(self):
        self.model = self.modelConstructor._parseModelFile(self.model_path)
        self.parsed_ltl = self.ltl_parser.parse_line(self.ltl)

        if self.prism_data_path:
            self.prism_data_rows = parse_csv_rows(self.prism_data_path)
        if self.prism_data_rows:
            self.prism_data_map = {}
            for row in self.prism_data_rows:
                attr = row[:-1]
                label = row[-1]
                self.prism_data_map[tuple(attr)] = label
        checker = Checker(self.model, self.parsed_ltl, duration=self.duration)
        self.experiment_wrapper = ExperimentWrapper(checker, self.params)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.setLevel(logging.DEBUG)

    def testChecking(self):
        '''
        verify the difference between smc and provided prism_data is within checking_delta
        :return: None
        '''
        checked_result_map = {}
        for name, values in self.params.items():
            self.model.commPrepared = False
            constant_obj = Constant(name, )
            set_result = self.model.set_constant(constant_obj)
            assert set_result
            result = self.checker.run_checker()
            checked_result_map[thickness] = result
        error_map = {}
        self.logger.info("check result: %s", str(checked_result_map))
        for k, v in checked_result_map.items():
            error_map[float(k)] = fabs(v - self.prism_data_map[float(k)])
        self.logger.info("error_map: %s", str(error_map))
        self.assertGreaterEqual(0.01, sum(error_map.values()) / len(checked_result_map))

    def testGenRandomPath(self):
        '''
        验证model产生的随机路径的长度要么等于duration，要么其中包含failure状态
        :return: None
        '''
        self.model.set_constant_name_value(self.PARAM_NAME, self.thicknesses[4])
        genCnt = 0
        while True:
            genCnt += 1
            self.logger.info("genCnt = %d", genCnt)
            path = self.model.get_random_path_V2()
            ap_sets = [step.ap_set for step in path]
            ap_set = reduce(lambda set1, set2: set1.union(set2), ap_sets)
            if len(path) == self.duration:
                if "failure" not in ap_set:
                    self.assertFalse(self.checker.verify(path))
                else:
                    self.assertTrue(self.checker.verify(path))
                continue
            elif "failure" in ap_set:
                self.assertTrue(self.checker.verify(path))
            else:
                break

