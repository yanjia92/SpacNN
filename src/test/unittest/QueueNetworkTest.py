# -*- coding:utf-8 -*-

from CheckerTest import CheckerTestBase


class QueueNetworkTest(CheckerTestBase):
    '''
    测试工具对于queue_network.prism模型的正确性
    '''

    def setUp(self):
        CheckerTestBase.setUp(self)

    def _get_model_name(self):
        return "queue_network"

    def _get_samples(self):
        return 500

    def _get_ltl(self):
        self.duration = 50
        return "true U<={} full".format(self.duration)

    def _get_duration(self):
        return self.duration

    def testCheckCorrect(self):
        # c = 5  # queue capacity
        # self._model.set_constant_name_value("c", c)
        prism_answer = 0.086023
        delta = 0.01
        check_answer = self._checker.run_checker()
        self.assertAlmostEqual(prism_answer, check_answer, delta=delta)

