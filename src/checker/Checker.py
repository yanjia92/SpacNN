# -*- coding:utf-8 -*-

from util.AnnotationHelper import *
from UnsureModelChecker import UnsureModelChecker
from LTLChecker import LTLChecker
from util.MathUtils import rel_index


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

    def check_and_export(self, path_cnt, antithetic=False):
        '''
        产生path_cnt条随机路径进行验证，并将验证结果返回
        :param path_cnt: int
        :return: [path], [bool]
        '''
        if not antithetic:
            paths = [self.gen_random_path() for _ in range(path_cnt)]
            results = map(lambda path: self._check(path), paths)
            return paths, results
        paths = []
        if path_cnt & 1:
            path_cnt += 1
        for _ in range(path_cnt / 2):
            paths.append(self.gen_random_path())
            anti_path = self.antithetic_path_of(paths[-1])
            paths.append(anti_path)
        results = map(lambda path: self._check(path), paths)
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

    def antithetic_path_of(self, path):
        seeds = [1 - step.get_seed() for step in path]
        return self.gen_random_path(seeds=seeds)

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
            apsets = map(lambda step: step.get_ap_set(), path)
            apset = reduce(lambda s1, s2: s1.union(s2), apsets)
            if generated_cnt % self._log_path_interval == 0:
                clock = time.time()
                print "Generating {} path causing {}s.".format(generated_cnt, clock - begin)
            result = self._check(path)
            if (len(apset) > 0) != result:
                print "check error"
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
        # results = map(lambda elem: [0, 1][elem], results)
        # print "index: {}".format(rel_index(results[0::2], results[1::2]))
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