# -*- coding:utf-8 -*-
from test.unittest.RegressionTestBase import RegressionTestBase
from util.util import interval
import matplotlib.pyplot as plt
from util.CsvFileHelper import *
from PathHelper import *
from util.MathUtils import almost_equal
from math import sqrt
from util.CsvFileHelper import write_csv_rows
from copy import deepcopy
from math import fabs


class BroadcastRegressionTest(RegressionTestBase):
    def setUp(self):
        RegressionTestBase.setUp(self)
        self._parameter_name = 'psend'
        self._export_train_path = get_data_dir() + get_sep() + "broadcast9_train.csv"
        self._prism_data_path = get_data_dir() + get_sep() + "broadcast9_prism_data.csv"
        self._train_xs = interval(0, 1, 0.02)
        self._test_xs = interval(0, 1, 0.01)

    def _get_model_name(self):
        return "broadcast9"

    def _get_ltl(self):
        return "true U<=10 node8receive"

    def _get_sample_size(self):
        return 500

    def _get_rearrange_path_cnt(self):
        return 500

    def _get_network_size(self):
        return [1, 30, 1]

    def _get_eta(self):
        return 0.1

    def _get_min_batch_size(self):
        return 10

    def _get_epochs(self):
        return 20

    def _gen_training_data(self):
        '''
        返回x,y元祖的数组
        :return: [(x, y)]
        '''
        checker = self._get_checker()
        train_ys = []
        self._rearrange(params=[(self._parameter_name, interval(0, 1, 0.1))])
        checker.set_antithetic(True)
        for x in self._train_xs:
            self._set_parameter(self._parameter_name, x)
            train_ys.append(checker.run_checker())
        return [(x, y) for x, y in zip(self._train_xs, train_ys)]

    def _get_weight_element_cnt(self):
        return 10

    def testExportTrainData(self):
        train_xs, train_ys = self._gen_training_data()
        write_csv_rows(self._export_train_path, [(x, y) for x, y in zip(train_xs, train_ys)])

    def _errors(self, nums1, nums2):
        '''
        计算两个数组之间的偏差
        :param nums1: list of number
        :param nums2: list of number
        :return: 偏差的平均数
        '''
        errors = 0.0
        n1 = len(nums1)
        n2 = len(nums2)
        if n1 == n2 and n1:
            for x1, x2 in zip(nums1, nums2):
                errors += fabs(x1 - x2)
            errors /= n1
        return errors

    def testTrainAndPredictWithoutWeights(self):
        '''
        首先不加权重的对训练数据进行拟合，训练10次，得到每次的估计数据
        :return:
        '''
        for _ in range(10):
            train_data = parse_csv_rows(self._export_train_path, has_headers=False)
            train_ys = [row[-1] for row in train_data]
            for row in train_data:
                row[-1] *= 100
            train_data = self._reshape_train_data(train_data)
            self._train(train_data)
            test_ys = self._predict(self._test_xs)
            test_ys = map(lambda y: y / 100, test_ys)

