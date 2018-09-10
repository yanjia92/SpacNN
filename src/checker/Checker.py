# -*- coding:utf-8 -*-

from util.AnnotationHelper import *
from UnsureModelChecker import UnsureModelChecker
from util.FormatUtil import str2num
from LTLChecker import LTLChecker


class BoundedInterval:
    '''
    class represent a bounded time interval for both DTMC / CTMC
    with -1 for the end to represent unbound interval
    '''
    def __init__(self, begin, end):
        if isinstance(begin, str):
            begin = str2num(begin)
        if isinstance(end, str):
            end = str2num(end)
        if end < begin:
            raise Exception("Invalid parameters ({}, {}) to construct a Interval instance")
        self._begin = begin
        self._end = end

    def __getitem__(self, n):
        if n == 0 or n == 1:
            return [self._begin, self._end][n == 1]
        raise Exception("Invalid index({}) to access the Interval".format(n))

    def overlap_with(self, binterval):
        '''
        return whether two intervals overlap
        :param binterval: bounded interval
        :return: boolean
        '''
        return (binterval[0] >= self[1]) != (binterval[1] >= self[0])

    def contains(self, moment):
        '''
        判断该时间范围内是否包含该时刻moment
        :param moment: time moment
        :return: boolean
        '''
        return self._begin <= moment < self._end

    @staticmethod
    def parse_literal(literal):
        '''
        从区间字符串解析，返回实例
        :param literal: [0,1]
        :return: BoundedInstance
        '''
        lb = literal.find('[')
        rb = literal.find(']')
        comma = literal.find(',')
        num1 = literal[lb+1:comma].strip()
        num2 = literal[comma+1:rb]
        try:
            num1 = str2num(num1)
            num2 = str2num(num2)
        except Exception,e:
            raise e
        return BoundedInterval(str2num(num1), str2num(num2))


class Checker(UnsureModelChecker):

    def __init__(self, model, ltl, duration, sample_cnt):
        self._model = model
        self.ltl = ltl
        self.lower = 0.0
        self.upper = 0.0
        self._sample_cnt = sample_cnt
        self._model.set_duration(duration)
        self.antithetic = False
        self.ltl_checker = LTLChecker()

    @setresult(521)
    def get_sample_size(self):
        return self._sample_cnt

    def set_sample_size(self, size):
        self._sample_cnt = size

    # returned (result, path e.g. list of Step instance)
    # using cachedPrefixes to check the path's checking result beforehand
    def gen_random_path(self):
        if self.antithetic:
            return self._model.get_random_path_V3()
        else:
            path = self._model.get_random_path_V2()
            return None, path

    def run_checker(self):
        samples = self.get_sample_size()
        generated_cnt = 0
        hit_cnt = 0  # satisfied path cnt
        begin = time.time()
        diff_cnt = 0 # 统计对偶路径验证结果不同的次数
        while generated_cnt < samples:
            satisfied, path = self.gen_random_path()
            if isinstance(satisfied, list):
                # generate 2 antithetic path
                generated_cnt += 2
                path1, path2 = satisfied, path
                result1 = self.ltl_checker.check(path1, self.ltl)
                result2 = self.ltl_checker.check(path2, self.ltl)
                if result1:
                    hit_cnt+=1
                if result2:
                    hit_cnt+=1
                if result1 != result2:
                    diff_cnt += 1
                if generated_cnt & 15 == 0:
                    t2 = time.time()
                    print "Verifying %d paths, causing %.2fs" % (generated_cnt, t2 - begin)
            else:
                if self.ltl_checker.check(path, self.ltl):
                    hit_cnt += 1
                generated_cnt += 1
                if generated_cnt & 15 == 0:
                    t2 = time.time()
                    print "Verifying %d paths, causing %.2fs" % (generated_cnt, t2 - begin)
        print "diff_cnt: {}".format(diff_cnt)
        return hit_cnt/generated_cnt

    def set_param(self, name, value):
        result = self._model.set_constant_name_value(name, value)
        self._model.set_prepared(False)
        return result
