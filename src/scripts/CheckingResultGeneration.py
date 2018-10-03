# -*- coding:utf-8 -*-
from test.unittest.CheckerTest import CheckerTestBase
from util.CsvFileHelper import *
from util.TypeTransformer import bool2int
from util.MathUtils import rel_index
import matplotlib.pyplot as plt
import thread

'''
分别产生checker在不使用对偶路径和使用对偶路径下的多个验证结果，
每次验证保存为一个文本文件，no_anti_i.txt anti_i.txt
'''

path_template = "../../data/cov/no_anti_{}.txt"
anti_path_template = "../../data/cov/anti_{}.txt"


class DataGeneration(CheckerTestBase):
    def _get_model_name(self):
        return "die"

    def _get_ltl(self):
        return "true U<=10 result_45"

    def _get_sample_size(self):
        return 400

    def testCheckCorrect(self):
        checker = self._get_checker()
        paths, results = checker.check_and_export(100)
        checker.rearrange(paths, results)
        checker.set_antithetic(True)
        print checker.run_smc()

    def _get_sample(self, sample_size, antithetic=False):
        '''
        返回sample_size条路径的验证结果
        :param sample_size: sample_size
        :param antithetic:
        :return: list of number(0/1)
        '''
        checker = self._get_checker()
        _, results = checker.check_and_export(sample_size, antithetic=antithetic)
        return map(lambda elem: [0, 1][elem], results)

    def testShowRelativeIndex(self):
        checker = self._get_checker()
        sample_size = 400
        sample_cnt = 100
        samples = [self._get_sample(sample_size) for _ in range(sample_cnt)]
        paths, results = checker.check_and_export(200)
        checker.rearrange(paths, results)
        anti_samples = [self._get_sample(sample_size, antithetic=True) for _ in range(sample_cnt)]
        # 相关系数
        indexs = [rel_index(sample[0::2], sample[1::2]) for sample in samples]
        anti_indexs = [rel_index(anti_sample[0::2], anti_sample[1::2]) for anti_sample in anti_samples]
        plt.subplot(121)
        plt.hist(indexs, 10)
        plt.subplot(122)
        plt.hist(anti_indexs, 10)
        plt.show()

    def testGenerate(self):
        checker = self._get_checker()
        i = 1
        anti_i = 1
        file_cnt = 100
        for _ in range(file_cnt):
            path = path_template.format(i)
            i += 1
            _, results = checker.check_and_export(self._get_sample_size())
            results = map(lambda elem: list([elem]), results)
            write_csv_rows(path, results, transformer=bool2int)

        paths, results = checker.check_and_export(1000)
        checker.rearrange(paths, results)
        checker.set_antithetic(True)
        for _ in range(file_cnt):
            anti_path = anti_path_template.format(anti_i)
            anti_i += 1
            _, results = checker.check_and_export(self._get_sample_size())
            results = map(lambda elem: list([elem]), results)
            write_csv_rows(anti_path, results, transformer=bool2int)

    def _compute_relative_index(self, path):
        rows = parse_csv_rows(path, types=int, has_headers=False)
        rows = [row[0] for row in rows]
        arr1 = rows[0::2]
        arr2 = rows[1::2]
        return rel_index(arr1, arr2)

    def testComputeRelativeIndex(self):
        '''
        计算data/cov下每个文件（样本）对应的相关系数
        :return:
        '''
        paths = [path_template.format(i) for i in range(1, 101)]
        anti_paths = [anti_path_template.format(i) for i in range(1, 101)]
        rel_indexes = [self._compute_relative_index(path) for path in paths]
        anti_rel_indexes = [self._compute_relative_index(path) for path in anti_paths]
        plt.subplot(121)
        plt.hist(rel_indexes, bins=20)
        plt.subplot(122)
        plt.hist(anti_rel_indexes, bins=20)
        plt.show()
