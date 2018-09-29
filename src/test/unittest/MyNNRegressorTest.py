# -*- coding:utf-8 -*-
import unittest
import numpy as np
import matplotlib.pyplot as plt
from util.CsvFileHelper import *
from PathHelper import *
from nn.MyNNRegressor import MyNNRegressor as Regressor
from nn.MyNNRegressor import WeightedQuadraticRegressCost as DefaultCost
from copy import copy
from util.util import interval
from util.MathUtils import averageDistanceToLine, rel_index


class MyNNRegressorTest(unittest.TestCase):
    def setUp(self):
        self._train_data_path = get_data_dir() + get_sep() + "broadcast9_train.csv"
        self._raw_train_data = parse_csv_rows(
            self._train_data_path, has_headers=False)
        self._train_data = copy(self._raw_train_data)
        self._regressor = Regressor(
            self._get_network_sizes(), cost=DefaultCost)
        self._prism_result_path = get_data_dir() + get_sep() + "broadcast.csv"

    def _get_raw_training_data(self):
        return self._raw_train_data

    def _get_learning_rate(self):
        return 0.08

    def _get_regularation_parameter(self):
        return 0.0

    def _get_network_sizes(self):
        return [1, 30, 1]

    def _get_epochs(self):
        return 50

    def _get_batch_size(self):
        return 10

    def _get_group_size(self):
        '''
        返回计算权重时每组的元素的个数
        :return: int
        '''
        return 10

    def _compute_weight(self, data):
        '''
        对一组样本点计算每个样本点的权重
        :param data: [(x,y)]
        :return: [weight] whose length is equal to data
        '''
        xs = [row[0] for row in data]
        ys = [row[1] for row in data]
        return [rel_index(xs, ys)] * len(data)

    def _compute_weights(self):
        '''
        使用样本之间的相关系数作为样本的可靠性度量
        一个样本组内的样本点线性相关性越高，则这个样本组内的每个样本的可靠性越高
        计算每个样本的可靠性权重
        :return: [weight]
        '''
        train_data = self._get_raw_training_data()
        group_size = self._get_group_size()
        groups = [train_data[i:i+group_size] for i in range(0, len(train_data), group_size)]
        weights = []
        for group in groups:
            weights.extend(self._compute_weight(group))
        # 归一化使得所有权重之和等于len(weights)
        s = sum(weights)
        c = len(weights)
        weights = map(lambda weight: c * weight / s, weights)
        return weights

    def _predict(self, xs):
        '''
        predict ys for xs
        :param xs:
        :return:
        '''
        if not xs or not len(xs):
            return
        try:
            shape = [len(xs[0]), 1]
            xs = map(lambda x: np.reshape(x, shape), xs)
        except TypeError:
            xs = map(lambda x: np.reshape(x, [1, 1]), xs)
        finally:
            ys = [self._regressor.feedforward(x)[0][0] for x in xs]
            return ys

    def _reshape(self):
        def reshape(row):
            xs = row[:-1]
            y = row[-1]
            xs = np.reshape(xs, [len(xs), 1])
            y = np.reshape(y, [1, 1])
            return xs, y
        self._train_data = map(reshape, self._train_data)

    def _add_weight(self, weights=None):
        def add_weight(row_weight_tuple):
            row, weight = row_weight_tuple
            row = list(row)
            row.append(weight)
            return tuple(row)
        self._train_data = map(add_weight, [(r, w) for r, w in zip(self._train_data, weights)])

    def _train(self):
        self._reshape()
        weights = self._compute_weights()
        self._add_weight(weights=[1]*len(self._train_data))
        _, training_costs = self._regressor.SGD(
            self._train_data,
            self._get_epochs(),
            self._get_batch_size(),
            self._get_learning_rate(),
            self._get_regularation_parameter(),
            monitor_training_cost=True)
        return training_costs

    def testShowRelativeIndex(self):
        # 计算分段样本之间的相关系数
        group_size = self._get_group_size()
        train_data = self._train_data
        n = len(train_data)
        groups = [self._train_data[i:i+group_size] for i in range(0, n, group_size)]
        relative_indexs = []
        for group in groups:
            xs = [point[0] for point in group]
            ys = [point[1] for point in group]
            relative_indexs.extend([rel_index(xs, ys)] * group_size)
        plt.scatter([point[0] for point in train_data], [point[1] for point in train_data])
        plt.scatter([point[0] for point in train_data], relative_indexs)
        plt.show()

    def testShowWeights(self):
        # 展示训练数据的分段权重
        train_data= self._get_raw_training_data()
        training_xs = [row[0] for row in train_data]
        training_ys = [row[1] for row in train_data]
        weights = self._compute_weights()
        plt.subplot(121)
        plt.scatter(training_xs, training_ys, color='g')
        plt.subplot(122)
        plt.scatter(training_xs, weights, color='r')
        plt.show()

    def testShowPredictError(self):
        training_costs = self._train()
        plt.subplot(121)
        plt.plot(range(self._get_epochs()), training_costs)
        plt.subplot(122)
        prism_xs, prism_ys = parse_csv_cols(self._prism_result_path)
        plt.plot(prism_xs, prism_ys, color='g')
        plt.scatter(self._raw_train_xs, self._raw_train_ys, color='b')
        test_xs = interval(0, 1, 0.005)
        test_ys = self._predict(test_xs)
        plt.plot(test_xs, test_ys, color='r')
        plt.show()


