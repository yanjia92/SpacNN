# -*- coding:utf-8 -*-
from test.unittest.RegressionTestBase import RegressionTestBase
from util.util import interval
import matplotlib.pyplot as plt
from util.CsvFileHelper import parse_csv_cols
from PathHelper import *
from util.MathUtils import almost_equal
from math import sqrt
from util.CsvFileHelper import write_csv_rows


class BroadcastRegressionTest(RegressionTestBase):
    def setUp(self):
        RegressionTestBase.setUp(self)
        self._parameter_name = 'psend'
        self._export_train_path = get_data_dir() + get_sep() + "broadcast_train.csv"

    def _get_model_name(self):
        return "broadcast"

    def _get_ltl(self):
        return "true U<=10 node3receive"

    def _get_sample_size(self):
        return 400

    def _get_rearrange_path_cnt(self):
        return 2000

    def _get_network_size(self):
        return [1, 30, 1]

    def _get_eta(self):
        return 0.05

    def _get_min_batch_size(self):
        return 10

    def _get_epochs(self):
        return 30

    def testCheckAntithetic(self):
        # self._set_parameter(self._parameter_name, 0.5)
        self._rearrange(params=[(self._parameter_name, interval(0, 1, 0.1))])
        self._set_parameter(self._parameter_name, 0.2)
        self._get_checker().set_antithetic(True)
        check_result = self._get_checker().run_checker()
        print check_result

    def _gen_training_data(self):
        checker = self._get_checker()
        # parameter value to be trained at
        xs = interval(0, 1, 0.01)
        ys = []
        self._rearrange(params=[(self._parameter_name, interval(0, 1, 0.1))])
        checker.set_antithetic(True)
        for x in xs:
            self._set_parameter(self._parameter_name, x)
            ys.append(checker.run_checker())
        return xs, ys

    def _get_weight_element_cnt(self):
        return 10

    def testExportTrainData(self):
        train_xs, train_ys = self._gen_training_data()
        write_csv_rows(self._export_train_path, [(x, y) for x, y in zip(train_xs, train_ys)])

    def testShowRegressionResult(self):
        train_xs, train_ys = self._gen_training_data()
        self._train(train_xs, train_ys)
        xs = interval(0, 1, 0.005)
        ys = self._predict(xs)
        plt.plot(xs, ys, color='r')
        prism_data_path = get_data_dir() + get_sep() + "broadcast.csv"
        prism_xs, prism_ys = parse_csv_cols(prism_data_path)
        # compute average error
        error = 0.0
        for x, y in zip(xs, ys):
            for prism_x, prism_y in zip(prism_xs, prism_ys):
                if almost_equal(x, prism_x, sig_fig=5):
                    error += (y - prism_y) ** 2
        print "average error: {}".format(sqrt(error / len(xs)))
        plt.plot(prism_xs, prism_ys, color='g')
        plt.scatter(train_xs, train_ys, color='b')
        plt.show()