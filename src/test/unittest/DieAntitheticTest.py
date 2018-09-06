from CheckerTest import CheckerTestBase


class DieTest(CheckerTestBase):
    def setUp(self):
        CheckerTestBase.setUp(self)
        self._checker.antithetic = True

    def _get_model_name(self):
        return "die"

    def _get_samples(self):
        return 200

    def _get_ltl(self):
        return "true U<=10 result_4"

    def _get_duration(self):
        return 10

    def testCheckAntithetic(self):
        return self._checker.run_checker()
