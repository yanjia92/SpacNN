# -*- coding:utf-8 -*-
from test.unittest.CheckerTest import CheckerTestBase
from util.MathUtils import *
import matplotlib.pyplot as plt
from PathHelper import *
from util.CsvFileHelper import write_csv_rows
from itertools import product
from math import ceil
from util.AnnotationHelper import profileit


class AntitheticTestCase(CheckerTestBase):
    def setUp(self):
        CheckerTestBase.setUp(self)

    def _get_sample(self, size, antithetic=False):
        '''
        返回一个大小为size的样本，验证结果为[0/1]
        :param size: sample size
        :param antithetic: bool
        :return:
        '''
        _, results = self._get_checker().check_and_export(size, antithetic=antithetic)
        return map(lambda result: [0, 1][result], results)

    @profileit("rearrange")
    def _rearrange(self, params=None):
        '''
        called before getting antithetic result
        因为模型参数影响到取到target路径的概率，所以，在单个参数点进行取路径验证rearrange不合理
        这里的做法是在每个参数点均匀取样，在每种可能性下取等样的路径进行验证
        :param params: values for unsure parameter [(name, [values])]
        :return:
        '''
        checker = self._get_checker()
        path_cnt = self._get_rearrange_path_cnt()
        if not params or not len(params):
            paths, results = checker.check_and_export(path_cnt)
            checker.rearrange(paths, results)
            return
        paths = []
        results = []
        names = [param[0] for param in params]
        values = [param[1] for param in params]
        path_per_params = int(ceil(float(path_cnt) / reduce(lambda s1, s2: s1*s2, map(lambda l: len(l), values))))
        original = {}
        for name, constant in self.get_model().get_constants().items():
            original[name] = constant.get_value()
        for param_values in product(*values):
            for (k, v) in zip(names, param_values):
                self._set_parameter(k, v)
            ps, rs = checker.check_and_export(path_per_params)
            paths.extend(ps)
            results.extend(rs)
        checker.rearrange(paths, results)
        # restore model parameters
        for name, value in original.items():
            self._set_parameter(name, value)

    def _get_rearrange_path_cnt(self):
        pass

    def _get_check_result(self):
        return self._get_checker().run_smc()

    def _get_antithetic_check_result(self):
        checker = self._get_checker()
        self._rearrange()
        checker.set_antithetic(True)
        return checker.run_smc()

    def _get_sample_cnt(self):
        '''
        返回展示相关系数所需的样本个数
        :return:
        '''
        return 100

    def _showRelativeIndex(self):
        '''
        展示使用对偶路径和不使用对偶路径的样本内部相关系数的分布
        :return:
        '''
        checker = self._get_checker()
        sample_cnt = self._get_sample_cnt()
        if not sample_cnt:
            print "_get_sample_cnt() not implemented."
        sample_size = self._get_sample_size()
        if not sample_size:
            print "_get_sample_size() not implemented."
        samples = [self._get_sample(sample_size) for _ in range(sample_cnt)]
        #  rearrange
        path_cnt = self._get_rearrange_path_cnt()
        if not path_cnt:
            print "_get_rearrange_path_cnt() not implemented."
        paths, results = checker.check_and_export(self._get_rearrange_path_cnt())
        checker.rearrange(paths, results)
        anti_samples = [self._get_sample(sample_size, antithetic=True) for _ in range(sample_cnt)]
        indexs = [rel_index(sample[0::2], sample[1::2]) for sample in samples]
        anti_indexs = [rel_index(anti_sample[0::2], anti_sample[1::2]) for anti_sample in anti_samples]
        plt.subplot(121)
        plt.hist(indexs, 10)
        plt.subplot(122)
        plt.hist(anti_indexs, 10)
        plt.show()

    def _get_variance_cnt(self):
        '''
        返回统计估计值方差的次数
        :return:
        '''
        return 100

    def _get_variance_size(self):
        '''
        返回为了求估计值的方差需要进行的模型检验的次数
        :return:
        '''
        return 10

    def _showVariance(self, dump=True):
        '''
        展示使用对偶路径和不使用对偶路径的样本的方差（而非样本方差）的分布
        :param dump: whether saving variances and anti_variances data to file
        :return:
        '''
        variance_cnt = self._get_variance_cnt()
        if not variance_cnt:
            print "_get_variance_cnt not implemented,"
        variance_size = self._get_variance_size()
        if not variance_size:
            print "_get_variance_size not implemented."
        sample_size = self._get_sample_size()
        if not sample_size:
            print "_get_sample_size not implemented."
        variances = []
        for _ in range(variance_cnt):
            samples = [self._get_sample(sample_size) for _ in range(variance_size)]
            check_results = map(lambda sample: sum(sample) / float(len(sample)), samples)
            variances.append(variance(check_results))

        checker = self._get_checker()
        path_cnt = self._get_rearrange_path_cnt()
        if not path_cnt:
            print "_get_rearrange_path_cnt not implemented."
        paths, results = checker.check_and_export(path_cnt)
        checker.rearrange(paths, results)
        anti_variances = []
        for _ in range(variance_cnt):
            samples = [self._get_sample(sample_size, antithetic=True) for _ in range(variance_size)]
            check_results = map(lambda sample: sum(sample) / float(len(sample)), samples)
            anti_variances.append(variance(check_results))
        if dump:
            variances_path = get_results_dir() + get_sep() + "variances.txt"
            anti_variances_path = get_results_dir() + get_sep() + "anti_variances.txt"
            write_csv_rows(variances_path, variances)
            write_csv_rows(anti_variances_path, anti_variances)
        plt.subplot(121)
        plt.hist(variances, bins=20)
        plt.subplot(122)
        plt.hist(anti_variances, bins=20)
        plt.show()


