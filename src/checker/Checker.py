# -*- coding:utf-8 -*-

from util.AnnotationHelper import *
from UnsureModelChecker import UnsureModelChecker
from LTLChecker import LTLChecker
from util.CsvFileHelper import write_csv_rows
from util.TypeTransformer import bool2int


class Checker(UnsureModelChecker):

    def __init__(self, model, ltl, duration, sample_cnt):
        self._model = model
        self._ltl = ltl
        self._sample_cnt = sample_cnt
        self._duration = duration
        self._model.set_duration(duration)
        self._antithetic = False
        self._ltl_checker = LTLChecker()
        self._log_path_interval = 16

    def check_and_export(self, path_cnt):
        '''
        产生path_cnt条随机路径进行验证，并将验证结果返回
        :param path_cnt: int
        :return: [path], [bool]
        '''
        paths = [self.gen_random_path() for _ in range(path_cnt)]
        formula = self._ltl
        results = map(lambda path: self._ltl_checker.check(path, formula), paths)
        return paths, results

    def rearrange(self, paths, results):
        self._model.rearrange(paths, results)

    def get_sample_size(self):
        return self._sample_cnt

    def set_sample_size(self, size):
        self._sample_cnt = size

    def gen_random_path(self, init_state=None, seeds=None):
        '''
        返回一条随机路径
        :return: path, list of AnotherStep instance
        '''
        return self._model.gen_path(init_state=init_state, seeds=seeds)

    def _check(self, path):
        '''
        convinent method used by run_checker
        :param path: list of AnotherStep instance
        :return: bool
        '''
        return self._ltl_checker.check(path, self._ltl)

    def run_checker(self):
        samples = self.get_sample_size()
        generated_cnt = 0.0
        hit_cnt = 0  # satisfied path cnt
        begin = time.time()
        diff_cnt = 0 # 统计对偶路径验证结果不同的次数
        results = []
        while generated_cnt < samples:
            path = self.gen_random_path()
            generated_cnt += 1
            if generated_cnt % self._log_path_interval == 0:
                clock = time.time()
                print "Generating {} path causing {}s.".format(generated_cnt, clock - begin)
            result = self._check(path)
            results.append(result)
            if result:
                hit_cnt += 1
            if self._antithetic:
                seeds = map(lambda step: 1 - step.get_seed(), path)
                antithetic_path = self.gen_random_path(seeds=seeds)
                anti_result = self._check(antithetic_path)
                results.append(anti_result)
                if result != anti_result:
                    diff_cnt += 1
                generated_cnt += 1
                if result:
                    hit_cnt += 1
        print "diff_cnt percentage = {}%".format(float(diff_cnt) / samples * 2 * 100)
        results = [list([elem]) for elem in results]
        write_csv_rows("anti.txt", results, transformer=bool2int)
        return hit_cnt/generated_cnt

    def set_param(self, name, value):
        result = self._model.set_constant_name_value(name, value)
        self._model.set_prepared(False)
        return result

    def set_antithetic(self, antithetic):
        '''
        setter
        :param antithetic:
        :return:
        '''
        if isinstance(antithetic, bool):
            self._antithetic = antithetic