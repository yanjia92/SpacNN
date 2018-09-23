# -*- coding: utf-8 -*-
from ModelTestBase import ModelTestBase
from checker.Checker import Checker

class TestMLPClassifier(ModelTestBase):
    '''
    测试MLPClassifier能否帮助判断单条路径是否满足属性
    '''
    def setUp(self):
        ModelTestBase.setUp(self)
        self.duration = 20
        self.ltl = "true U<={} result_4".format(self.duration)
        self.ltl = self._ltl_parser.parse_line(self.ltl)
        self.checker = Checker(model=self._model, ltl=self.ltl)

    def get_training_data(self):
        pass

    def _get_model_name(self):
        return "die"

    def testCompilerRight(self):
        pass