from CheckerTest import CheckerTestBase


class DieTest(CheckerTestBase):
    def setUp(self):
        CheckerTestBase.setUp(self)
        self._checker.antithetic = True

    def _get_model_name(self):
        return "die"

    def _get_samples(self):
        return 400

    def _get_ltl(self):
        return "true U<=10 result_4"

    def _get_duration(self):
        return 10

    def testCheckAntithetic(self):
        return self._checker.run_checker()

    def testVarReduction(self):
        samples = 50
        check_results = [self._checker.run_checker() for _ in range(samples)]
        average = sum(check_results) / len(check_results)
        variance = sum([(check_result - average) ** 2 for check_result in check_results])

        self._checker.antithetic = True
        check_results = [self._checker.run_checker() for _ in range(samples)]
        average = sum(check_results) / len(check_results)
        variance1 = sum([(check_result - average) ** 2 for check_result in check_results])

        print variance
        print variance1
