# -*- coding: utf-8 -*-
from test.unittest.CheckerTest import CheckerTestBase


'''
测试antithetic variable方法是否可以减小smc算法的方差
'''

'''
model
=====

dtmc

module
    i: [0, 2] init 0;
    [] i == 0 -> 0.3 : (i'=1) + 0.7 : (i'=2);
endmodule

label ieq1 = i == 1;
label ieq2 = i == 2;
'''


class VarBenchmark(CheckerTestBase):

    def _get_model_name(self):
        return "die"

    def testModelCorrect(self):
        pass

    def _get_ltl(self):
        return "true U<=20 result_4"

    def _get_samples(self):
        return 100

    def _get_duration(self):
        return 20

    def setUp(self):
        CheckerTestBase.setUp(self)
        self._checker.antithetic = True

    def testComputeVar(self):
        '''
        计算SMC算法的方差
        步骤
            1. 每个样本包含500条随机路径
            2. 取20个样本，计算这20个样本的方差
        :return: void
        '''
        #
        # 0.000422302631579
        results = []
        for _ in range(20):
            results.append(self._checker.run_checker())
        # 期望
        expect = sum(results) / len(results)
        print "expect: {}".format(expect)
        # 方差
        var = sum(map(lambda x: (x - expect) ** 2, results)) / (len(results) - 1)
        print "var: {}".format(var)
