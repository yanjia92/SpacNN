# -*- coding:utf-8 -*-
from test.unittest.AntitheticTestBase import AntitheticTestCase


class RegressionTestBase(AntitheticTestCase):
    def setUp(self):
        AntitheticTestCase.setUp(self)

    def _set_parameters(self, name, values):
        '''
        设置参数到model._constants中
        :param name: parameter name
        :param values: list of values
        :return:
        '''
        pass
