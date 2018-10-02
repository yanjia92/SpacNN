# -*- coding:utf-8 -*-
from test.unittest.RegressionTestBase import RegressionTestBase
from util.util import interval
import matplotlib.pyplot as plt
from util.CsvFileHelper import *
from PathHelper import *
from util.CsvFileHelper import write_csv_rows
from math import fabs
from util.MathUtils import averageDistanceToLine
import os
from util.MathUtils import z


class BroadcastRegressionTest(RegressionTestBase):
    def setUp(self):
        RegressionTestBase.setUp(self)
        self._parameter_name = 'psend'
        self._export_train_path = get_data_dir() + get_sep() + "broadcast9_train.csv"
        self._prism_data_path = get_data_dir() + get_sep() + "broadcast9_prism_data.csv"
        self._export_test_path = get_data_dir() + get_sep() + "broadcast9_test.csv"
        self._export_weight_test_path = get_data_dir() + get_sep() + \
            "broadcast9_weight_test.csv"
        self._export_aver_error_path = get_data_dir() + get_sep() + \
            "broadcast9_aver_error.csv"
        self._export_weight_aver_error_path = get_data_dir() + get_sep() + \
            "broadcast9_weight_aver_error.csv"
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
        write_csv_rows(
            self._export_train_path, [
                (x, y) for x, y in zip(
                    train_xs, train_ys)])

    def _errors(self, nums1, nums2):
        '''
        计算两个数组之间的平均偏差
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
        else:
            raise Exception("arrays len not equal or zero")
        return errors

    def _compute_weight(self, xs, ys):
        '''
        计算一群点的可靠性权重
        使用点到直线的平均距离的倒数作为衡量
        需要考虑到平均偏差和ys的均值的比例关系
        :param xs: [float]
        :param ys: [float]
        :return: [float]
        '''
        # 定义平均偏差的最小值，使得权重不至于过大
        min_distance = 0.01
        aver_y = sum(ys) / len(ys)
        if len(xs) == len(ys) and len(xs):
            dist = averageDistanceToLine(xs, ys)
            if dist < min_distance:
                dist = min_distance
            dist /= aver_y
            return [1.0 / (dist**2) for _ in xs]

    def _compute_weights(self, train_data, default=True):
        '''
        分段计算样本点可靠性权重
        使用平均到拟合直线的距离来衡量可靠性权重
        :param train_data: [(x,y)]
        :param default: no using weight?
        :return: [int] -> weights
        '''
        if default:
            return [1.0 for _ in train_data]
        weights = []
        n = len(train_data)
        # 每10个点作为一段
        weight_interval_size = 10
        for i in range(0, n, weight_interval_size):
            interval_data = train_data[i:i + weight_interval_size]
            xs = [row[0] for row in interval_data]
            ys = [row[1] for row in interval_data]
            weights.extend(self._compute_weight(xs, ys))
        # make all weight in [0, 1]
        weights = map(lambda w: fabs(w), weights)
        s = sum(weights)
        # 归一化使得sum(weights) = len(weights)
        return map(lambda w: w * n / s, weights)

    def _trainTestExportError(self, path, train_times=100):
        '''
        训练train_times次，统计每次的估计的平局偏差，最终将误差数据导出到path
        :return:
        '''
        if os.path.isfile(path):
            os.remove(path)
        train_data = parse_csv_rows(self._export_train_path, has_headers=False)
        weights = self._compute_weights(train_data, default=True)
        # 扩大y的量纲
        for row in train_data:
            row[-1] *= 100
        train_data = self._reshape_train_data(train_data)
        for _ in range(train_times):
            self._train(train_data, weights)
            test_ys = self._predict(self._test_xs)
            test_ys = map(lambda y: y / 100, test_ys)
            write_csv_rows(
                path, [
                    (x, y) for x, y in zip(
                        self._test_xs, test_ys)], mode='a')
            self._reinitialize_network()

    def _showErrorHist(self, path, error_path, subplot=None):
        '''
        展示误差直方图
        :param path: 测试数据文件路径
        :param error_path: 导出偏差数据文件路径
        :return:
        '''
        aver_errors = []
        test_data = parse_csv_rows(path, has_headers=False)
        prism_data = parse_csv_rows(self._prism_data_path, has_headers=False)
        prism_ys = [row[-1] for row in prism_data]
        n = len(prism_data)
        for i in range(0, len(test_data), n):
            test_data_batch = test_data[i:i + n]
            test_ys = [row[-1] for row in test_data_batch]
            aver_errors.append(self._errors(prism_ys, test_ys))
        write_csv_rows(error_path, aver_errors)
        if subplot:
            plt.subplot(subplot)
        plt.hist(aver_errors)

    def testTrainTestShowError(self):
        choices = [True, False]
        subplot = "12{}"
        p = 1
        for choice in choices:
            default_weight = choice
            path = [self._export_weight_test_path,
                    self._export_test_path][default_weight]
            error_path = [self._export_weight_aver_error_path, self._export_aver_error_path][default_weight]
            self._trainTestExportError(path)
            self._showErrorHist(path, error_path, subplot=subplot.format(p))
            p += 1
        plt.show()

    def testAnalysisError(self):
        '''
        分析使用加权和不使用加权两种方式的偏差分布的不同
        通过计算z分位数
        :return:
        '''
        percentages = [0.25, 0.5, 0.75, 0.9]
        default_errors = parse_csv_rows(self._export_aver_error_path, has_headers=False)
        no_default_errors = parse_csv_rows(self._export_weight_aver_error_path, has_headers=False)
        default_zs = [z(default_errors, p) for p in percentages]
        no_default_zs = [z(no_default_errors, p) for p in percentages]
        print default_zs
        print no_default_zs

