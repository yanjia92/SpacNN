# -*- coding:utf-8 -*-
from test.unittest.RegressionTestBase import RegressionTestBase
from util.util import interval
import matplotlib.pyplot as plt
from util.CsvFileHelper import parse_csv_cols
from PathHelper import *
from util.MathUtils import almost_equal
from math import sqrt
from util.CsvFileHelper import write_csv_rows
from copy import deepcopy


class BroadcastRegressionTest(RegressionTestBase):
    def setUp(self):
        RegressionTestBase.setUp(self)
        self._parameter_name = 'psend'
        self._export_train_path = get_data_dir() + get_sep() + "broadcast_train.csv"

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
        return 0.05

    def _get_min_batch_size(self):
        return 10

    def _get_epochs(self):
        return 30

    def testCheck(self):
        '''
        验证检验结果的正确性
        :return:
        '''
        self.assertAlmostEqual(self._get_checker().run_checker(), 0.475329, delta=0.1)

    def testCheckAntithetic(self):
        self._rearrange(params=[(self._parameter_name, interval(0, 1, 0.1))])
        self._get_checker().set_antithetic(True)
        check_result = self._get_checker().run_checker()
        self.assertAlmostEqual(check_result, 0.475329, delta=0.1)

    def _gen_training_data(self):
        checker = self._get_checker()
        # parameter value to be trained at
        xs = interval(0, 1, 0.05)
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

    def testShowModelStat(self):
        model = self.get_model()
        for k, v in model.stat().items():
            print "{}: {}".format(k, v)

    def testVariableCopy(self):
        '''
        test whether variable is copyable
        :return:
        '''
        model = self.get_model()
        variables = model.get_variables()  # list of variable
        var = variables[0]
        copy_var = deepcopy(var)
        var.set_value(2)
        print var.get_value()
        print copy_var.get_value()

    def testCommandCopy(self):
        '''
        test whether command is copyable
        :return:
        '''
        model = self.get_model()
        commands = model.get_commands()  # list of list
        copy_commands = deepcopy(commands)
        print len(copy_commands)