# -*- coding:utf-8 -*-
from test.unittest.AntitheticTestBase import AntitheticTestCase
from nn.MyNNRegressor import WeightedQuadraticRegressCost as DefaultCost
from nn.MyNNRegressor import MyNNRegressor as Regressor
import numpy as np
from util.MathUtils import averageDistanceToLine
from util.MathUtils import uniform


class RegressionTestBase(AntitheticTestCase):
    def setUp(self):
        AntitheticTestCase.setUp(self)
        self._param_map = {}
        self._network = Regressor(self._get_network_size(), cost=DefaultCost)

    def _train(self, xs, ys):
        '''
        :param xs: training_xs
        :param ys: training_ys
        :return:
        '''
        batch_size = self._get_weight_element_cnt()
        batches = [
            (xs[i:i+batch_size], ys[i:i+batch_size])
            for i in range(0, len(xs), batch_size)
        ]
        ws = []
        for batch in batches:
            ws.extend([self._compute_weights1(batch[0], batch[1])] * len(batch[0]))
        ws = self._normalized(ws)
        xs = self._reshape_array(xs)
        ys = self._reshape_array(ys)
        training_data = [(x, y, w) for x, y, w in zip(xs, ys, ws)]
        self._network.SGD(training_data, self._get_epochs(), self._get_min_batch_size(), self._get_eta())

    def _predict(self, xs):
        xs = self._reshape_array(xs)
        ys = [self._network.feedforward(x) for x in xs]
        return [y[0][0] for y in ys]

    def _compute_weights(self, intervals):
        '''
        计算在各个区间内样本的权重
        :param intervals: list of tuple that representing a interval (a, b)
        :return: {(a, b): weight}
        '''
        sample_per_interval = 20
        weights = []
        for interval in intervals:
            check_results = []
            a, b = interval
            param_values = uniform(a, b, sample_per_interval)
            for param_value in param_values:
                self._set_parameter(self._get_parameter_name(), param_value)
                check_results.append(self._get_checker().run_checker())
            ws = (1.0 / averageDistanceToLine(param_values, check_results) ** 2) * len(param_values)
            weights.extend(ws)
        return weights

    def _compute_weights1(self, xs, ys):
        return len(xs) / (averageDistanceToLine(xs, ys) ** 2)

    def _normalized(self, nums):
        '''
        归一化nums返回
        :param nums: list of number
        :return:
        '''
        s = sum(nums)
        return [elem / s * len(nums) for elem in nums]

    def _get_weight_element_cnt(self):
        '''
        返回计算权重时每个区间包含的元素个数
        :return:
        '''
        pass

    def _get_parameter_name(self):
        pass

    def _gen_training_data(self):
        '''
        :return: xs, ys
        '''
        return [], []

    def _reshape_array(self, array):
        '''
        reshape using np.reshape
        :param array: list
        :return: ndarray
        '''
        if not array or not len(array):
            return np.ndarray([])
        elem0 = array[0]
        if not isinstance(elem0, list):
            shape = [1, 1]
        else:
            shape = [len(array[0]), 1]
        return [np.reshape(elem, shape) for elem in array]

    def _get_min_batch_size(self):
        '''
        :return:
        '''
        pass

    def _get_epochs(self):
        '''
        :return:
        '''
        pass

    def _get_eta(self):
        '''
        :return: learning rate
        '''

    def _get_network_size(self):
        '''
        返回神经网络的大小，即每层神经元数
        :return: list of number
        '''
        pass