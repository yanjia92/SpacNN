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

    def _reinitialize_network(self):
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

    def _train(self, train_data, weights):
        '''
        对神经网络进行训练
        :param train_data: [(x,y)]
        :param weights: [int]
        :return:
        '''
        if not train_data or not len(train_data):
            return
        t_data = []
        for i, row in enumerate(train_data):
            l = list(row)
            l.append(weights[i])
            t_data.append(tuple(l))
        self._network.SGD(t_data, self._get_epochs(), self._get_min_batch_size(), self._get_eta(), monitor_training_cost=True)

    def _predict(self, xs):
        xs = np.array(xs)
        ys = [self._network.feedforward(x) for x in xs]
        return [y[0][0] for y in ys]

    def _compute_weights(self, train_data, default=True):
        '''
        计算训练样本集中每个样本点的可靠性权值
        :param train_data: [(x, y)]
        :return: [int]
        '''
        if not default:
            raise Exception("Not implemented yet.")
        return [1.0 for _ in range(len(train_data))]

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