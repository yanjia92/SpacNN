# -*- coding: utf-8 -*-
from test.unittest.CheckerTest import CheckerTestBase
from PathHelper import get_prism_model_dir

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

    def _get_model_root_path(self):
        return get_prism_model_dir()

    def _get_model_name(self):
        return "ToyDTMCModel"

    def testModelCorrect(self):
        pass

    def _get_ltl(self):
        return "true U<=2 ieq1"

    def _get_samples(self):
        return 100

    def _get_duration(self):
        return 2

    def testComputeVar(self):
        '''
        计算SMC算法的方差
        步骤
            1. 每个样本包含500条随机路径
            2. 取20个样本，计算这20个样本的方差
        :return: void
        '''
        results = []
        for _ in range(20):
            results.append(self._checker.run_checker())
        expect = sum(results) / len(results)
        var = sum(map(lambda x: (x - expect) ** 2, results)) / (len(results) - 1)
        print var

