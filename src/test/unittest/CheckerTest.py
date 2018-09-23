# -*- coding:utf-8 -*-

from ModelTestBase import ModelTestBase
from checker.Checker import Checker
from util.FormatUtil import str2num


class CheckerTestBase(ModelTestBase):
    def setUp(self):
        ModelTestBase.setUp(self)
        self._parsed_ltl = self._ltl_parser.parse_line(self._get_ltl())
        self._duration = str2num(self._ltl_parser.parse_duration(self._get_ltl()))
        if self._duration is None:
            self._duration = self._get_duration()
        self._checker = Checker(self._model, self._parsed_ltl, self._duration, self._get_sample_size())

    def _get_ltl(self):
        pass

    def _get_sample_size(self):
        '''
        checker验证取样的随机样本数
        :return:
        '''
        pass

    def _get_duration(self):
        '''
        返回随机路径的时间长度
        :return: int or float type
        '''
        pass

    def _get_checker(self):
        return self._checker