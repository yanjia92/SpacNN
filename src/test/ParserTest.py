# -*- coding: utf-8 -*-
import unittest
from compiler.PRISMParser import ModelConstructor
from PathHelper import *
from util.CsvFileHelper import *
from util.util import interval
from checker.Checker import Checker
from compiler.LTLParser import LTLParser
from module.Module import Constant
import logging
import sys
from math import fabs


class ParserTest(unittest.TestCase):
    '''
    单元测试：测试parser出的模型运转良好
    '''
    def setUp(self):
        self.modelConstructor = ModelConstructor()
        self.model = self.modelConstructor.parseModelFile(get_prism_model_dir() + get_sep() + "smalltest.prism")
        prism_data_rows = parse_csv_rows(get_prism_model_dir() + get_sep() + "screen_thickness_1_10_01.csv")
        if prism_data_rows:
            self.prism_data_map = {}
            for thickness, prob in prism_data_rows:
                self.prism_data_map[thickness] = prob
        ltl = "true U<=180 failure"
        ltl_parser = LTLParser().build_parser()
        parsed_ltl = ltl_parser.parse_line(ltl)
        self.duration = 180
        self.checker = Checker(self.model, parsed_ltl, duration=self.duration)
        self.PARAM_NAME = "SCREEN_THICKNESS"
        self.checking_delta = 0.01
        self.thicknesses = interval(1, 10, 1)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.setLevel(logging.DEBUG)

    def testChecking(self):
        '''
        验证checker的算法结果和prism的结果的平均误差在0.01范围内
        :return: None
        '''
        thicknesses = self.thicknesses
        checked_result_map = {}
        for thickness in thicknesses:
            self.model.commPrepared = False
            constant_obj = Constant(self.PARAM_NAME, thickness)
            set_result = self.model.set_constant(constant_obj)
            assert set_result
            result = self.checker.run_checker()
            checked_result_map[thickness] = result
        error_map = {}
        self.logger.info("check result: %s", str(checked_result_map))
        for k, v in checked_result_map.items():
            error_map[float(k)] = fabs(v - self.prism_data_map[float(k)])
        self.logger.info("error_map: %s", str(error_map))
        self.assertGreaterEqual(0.001, sum(error_map.values()) / len(checked_result_map))

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

