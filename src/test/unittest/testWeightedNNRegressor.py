# -*- coding: utf-8 -*-
from CheckerTest import CheckerTestBase
from util.MathUtils import uniform
from util.MathUtils import standDiv
import matplotlib.pyplot as plt
from nn.MyNNRegressor import MyNNRegressor
from nn.MyNNRegressor import WeightedQuadriticRegressCost
from util.util import interval
import numpy as np
from util.CsvFileHelper import *
from PathHelper import *


class Test(CheckerTestBase):
    def _get_model_name(self):
        return "ToyDTMCModel"

    def _get_ltl(self):
        return "true U<=5 ieq1"

    def _get_duration(self):
        return 5

    def _get_sample_size(self):
        return 100

    def setUp(self):
        CheckerTestBase.setUp(self)
        self._checker.antithetic = True

    def _gen_train_data_with_weights(self):
        '''
        将[0,1]分成10个区间，每个区间取10个样本点，计算每个样本点的可靠性权重
        :return: 返回100个样本点连同权重
        '''
        step = 0.1
        intervals = []
        for left in range(10):
            intervals.append([left * step, (left + 1) * step])
        samples = []
        weights = []
        for interval in intervals:
            # 每个interval取10个样本点
            xs = uniform(interval[0], interval[1], samples=10)
            ys = []
            for param in xs:
                self._checker.set_param("theta", param)
                ys.append(self._checker.run_checker())
            # compute weights for each (x, y)
            average_distance = standDiv(xs, ys)
            weight = 1.0 / (average_distance ** 2)

            samples.extend([(x, y) for x, y in zip(xs, ys)])
            weights.extend([weight for _ in xs])
        return samples, weights

    def testGenTrainData(self):
        samples, weights = self._gen_train_data_with_weights()
        for sample, weight in zip(samples, weights):
            print "sample: {}, weight: {}".format(sample, weight)
        xs = [sample[0] for sample in samples]
        ys = [sample[1] for sample in samples]
        # plt.scatter(xs, ys, marker="*", c="#000000")
        # plt.show()
        # return [(x, y, w) for x,y,w in zip(xs, ys, weights)]
        weightssum = sum(weights)
        weights = [weight / weightssum * len(weights) for weight in weights]
        distinct = []
        for weight in weights:
            if weight not in distinct:
                distinct.append(weight)
        print "distinct:{}".format(distinct)
        return [(np.reshape(x, [1, 1]), np.reshape(y, [1, 1]), w) for x, y, w in zip(xs, ys, weights)]

    def _average_error(self, xs, ys, prism_data_path):
        datas = parse_csv_rows(prism_data_path)
        datas = [data for data in datas if data[0] in xs]
        return sum([(y - data[1]) ** 2 for y, data in zip(ys, datas)]) / len(xs)

    def testWeightedRegress(self):
        '''
        使用加权回归神经网络模型拟合数据
        :return:
        '''
        regressor = MyNNRegressor([1, 10, 1], cost=WeightedQuadriticRegressCost)
        training_data = self.testGenTrainData()
        regressor.SGD(training_data, 30, 10, 0.3)
        test_x = interval(0, 1, 0.01)
        test_x = [np.reshape(x, [1, 1]) for x in test_x]
        test_y = [regressor.feedforward(x) for x in test_x]
        test_y = [y[0][0] for y in test_y]
        test_x = [x[0][0] for x in test_x]
        plt.plot(test_x, test_y, c="b")

        # load data from prism
        path = get_prism_model_dir() + get_sep() + "toy_theta_0_1_001"

        error = self._average_error(test_x, test_y, path)
        print "error:{}".format(error)
        cols = parse_csv_cols(path)
        prism_xs, prism_ys = cols
        plt.plot(prism_xs, prism_ys, c="r")
        plt.show()

    def testRegress(self):
        pass
