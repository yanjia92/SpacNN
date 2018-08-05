# -*- coding:utf-8 -*-
from ParserTest import ParserTest
from sklearn.neural_network import MLPRegressor
from util.util import interval
import numpy as np
from util.MathUtils import format_float
from math import fabs
from util.CsvFileHelper import write_csv_rows, parse_csv_rows
import matplotlib.pyplot as plt


class MLPRegressorTest(ParserTest):
    def setUp(self):
        ParserTest.setUp(self)
        self.mlp_regressor = MLPRegressor(alpha=0.0001, hidden_layer_sizes=(15, ), max_iter=40000,
                             activation="logistic", verbose='True', learning_rate="adaptive", solver="sgd", tol=1e-9)
        self.train_data_rows = parse_csv_rows("/Users/bitbook/Documents/SpacNN/data/smalltest_smc_1_10_01.csv")

    def testMLPRegress(self):
        '''
        验证smc算法和mlp回归的结果误差相差无几
        :return:
        '''
        train_data_x = interval(5.0, 10.0, 0.1)  # 14
        train_data_x = [format_float(v, 1) for v in train_data_x]
        train_data_y = [y for (x, y) in self.train_data_rows if x in train_data_x]
        xs, ys = self.transform_data(train_data_x, train_data_y)
        self.mlp_regressor.fit(xs, ys)
        test_data_x = np.linspace(5.0, 10.0, 50)  # step: 0.1
        test_data_x = np.array([format_float(v, 1) for v in test_data_x])
        test_data_y = self.mlp_regressor.predict(test_data_x.reshape([50, 1]))
        prism_data_y = [self.prism_data_map[k] for k in test_data_x]
        smc_data_y = [y for (x, y) in self.train_data_rows if x in test_data_x]
        error_smc_map = {}
        error_mlp_map = {}
        for x, smc_y, mlp_y, prism_y in zip(test_data_x, smc_data_y, test_data_y, prism_data_y):
            error_smc_map[x] = fabs(smc_y - prism_y)
            error_mlp_map[x] = fabs(mlp_y - prism_y)
        self.logger.info("smc average error is %f", sum(error_smc_map.values()) / len(error_smc_map))
        self.logger.info("mlp average error is %f", sum(error_mlp_map.values()) / len(error_mlp_map))

        fig = plt.figure()
        plt.plot(test_data_x, prism_data_y, color='g')
        plt.plot(test_data_x, smc_data_y, color='r')
        fig1 = plt.figure()
        plt.plot(test_data_x, test_data_y, color='b')
        plt.plot(test_data_x, prism_data_y, color='g')
        plt.show()

    def transform_data(self, xs, ys):
        '''
        将xs, ys转化为np.array
        :param xs: features array
        :param ys: label array
        :return: np.array instances
        '''
        nparray_xs = np.array(xs)
        nparray_ys = np.array(ys)
        if len(xs) > 0:
            if isinstance(xs[0], list):
                nparray_xs = np.reshape(nparray_xs, [len(xs), len(xs[0])])
            else:
                nparray_xs = np.reshape(nparray_xs, [len(xs), 1])
        else:
            nparray_xs = np.reshape(nparray_xs, [0, 0])
        if len(ys) > 0:
            nparray_ys = np.reshape(nparray_ys, [len(ys), ])
        else:
            nparray_ys = np.reshape(nparray_ys, [0, ])
        return nparray_xs, nparray_ys

    def testGenTrainData(self):
        '''
        对于smalltest.prism，产生其在[1, 10, 0.1]上的所有的模型检验结果
        samples: 6433
        :return: 写入csv文件
        '''
        filepath = "/Users/bitbook/Documents/SpacNN/data/smalltest_smc_1_10_01.csv"
        xs = interval(1, 10, 0.1)
        xs = [format_float(v, 1) for v in xs]
        ys = []
        for x in xs:
            self.model.set_constant_name_value(self.PARAM_NAME, x)
            self.model.commPrepared = False
            ys.append(self.checker.run_checker())
        rows = [[x, y] for (x, y) in zip(xs, ys)]
        write_csv_rows(filepath, rows, headers=["SCREEN_THICKNESS", "result"])


