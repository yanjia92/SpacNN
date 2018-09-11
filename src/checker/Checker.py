# -*- coding:utf-8 -*-

from util.AnnotationHelper import *
from UnsureModelChecker import UnsureModelChecker
from LTLChecker import LTLChecker


class Checker(UnsureModelChecker):

    def __init__(self, model, ltl, duration, sample_cnt):
        self._model = model
        self._ltl = ltl
        self._sample_cnt = sample_cnt
        self._model.set_duration(duration)
        self._antithetic = False
        self._ltl_checker = LTLChecker()
        self._log_path_interval = 16

    def get_sample_size(self):
        return self._sample_cnt

    def set_sample_size(self, size):
        self._sample_cnt = size

    def gen_random_path(self):
        '''
        返回一条随机路径
        :return: path, list of AnotherStep instance
        '''
        return self._model.gen_path()

    def run_checker(self):
        samples = self.get_sample_size()
        generated_cnt = 0
        hit_cnt = 0  # satisfied path cnt
        begin = time.time()
        diff_cnt = 0 # 统计对偶路径验证结果不同的次数
        while generated_cnt < samples:
            path = self.gen_random_path()
            generated_cnt += 1
            if generated_cnt % self._log_path_interval == 0:
                clock = time.time()
                print "Generating {} path causing {} s".format(generated_cnt, clock - begin)
            check_ans = self._ltl_checker.check(path, self._ltl)
            if check_ans:
                hit_cnt += 1
        return hit_cnt/generated_cnt

    def set_param(self, name, value):
        result = self._model.set_constant_name_value(name, value)
        self._model.set_prepared(False)
        return result
