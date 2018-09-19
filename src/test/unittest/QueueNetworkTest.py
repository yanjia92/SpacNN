# -*- coding:utf-8 -*-

from CheckerTest import CheckerTestBase


class QueueNetworkTest(CheckerTestBase):
    '''
    测试工具对于queue_network.prism模型的正确性
    '''

    def setUp(self):
        CheckerTestBase.setUp(self)
        self._checker.antithetic = True

    def _get_model_name(self):
        return "queue_network"

    def _get_sample_cnt(self):
        return 300

    def _get_ltl(self):
        return "true U<=10 full"

    def testCheckCorrect(self):
        '''
        验证检验结果正确
        :return:
        '''
        prism_answer = 0.086023 # result for duration = 50
        delta = 0.02
        check_answer = self._checker.run_checker()
        self.assertAlmostEqual(prism_answer, check_answer, delta=delta)

    def _compute_var(self, sample_cnt):
        '''
        计算sample_cnt个样本的方差
        :param sample_cnt: 样本的个数（而非路径的条数）
        :return: variance
        '''
        check_results = [self._checker.run_checker() for _ in range(sample_cnt)]
        average = sum(check_results) / len(check_results)
        return sum([(result - average) ** 2 for result in check_results]) / len(check_results)

    def testVarReduction(self):
        sample_cnt = 5
        vars1 = [self._compute_var(sample_cnt) for _ in range(10)]

        # generate training path and check results to rearrange next-state order
        paths, results = self._checker.check_and_export(1000)
        self._model.rearrange(paths, results)
        self._checker.set_antithetic(True)

        vars2 = [self._compute_var(sample_cnt) for _ in range(10)]

        print "var1: {}, var2: {}".format(sum(vars1) / len(vars1), sum(vars2) / len(vars2))