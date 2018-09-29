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

    def _reshape_train_data(self, train_data):
        '''
        将x矩阵化
        例如包含三个自变量的x: [1, 2, 3]
        矩阵化的之后的大小为(3, 1)
        而只包含一个变量的x，即x=1，则矩阵化之后的矩阵大小为[1, 1]
        :param train_data: [(x,y)] list of tuple
        :return:
        '''
        xs = [row[:-1] for row in train_data]
        ys = [row[-1:] for row in train_data]
        x_shape = (len(xs[0]), 1)
        xs = [np.reshape(x, x_shape) for x in xs]
        return [(x, y) for x, y in zip(xs, ys)]

    def _train(self, train_data, weights=None):
        '''
        对神经网络进行训练
        :param train_data: [(x,y)]
        :param weights: [int]
        :return:
        '''
        if not train_data or not len(train_data):
            return
        n = len(train_data)
        if not weights or not len(weights):
            weights = [1.0 for _ in range(n)]
        for i, row in enumerate(train_data):
            row = list(row)
            row.append(weights[i])
            train_data[i] = tuple(row)
        self._network.SGD(train_data, self._get_epochs(), self._get_min_batch_size(), self._get_eta(), monitor_training_cost=True)

    def _predict(self, xs):
        xs = np.array(xs)
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