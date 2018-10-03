from model.ModelFactory import ModelFactory
from checker.Checker import *
from util.AnnotationHelper import *
import unittest

YEAR = 1
DURATION = int(365 * YEAR * 2)


class TestParsingChecker(unittest.TestCase):
    def setUp(self):
        self.parsed = ModelFactory.get_parsed()
        self.ltl = ["U[1, {}]".format(DURATION), "T", "failure"]
        self.checker = Checker(self.parsed, ltl=self.ltl, duration=DURATION)

    def test_check(self):
        self.checker.run_smc()


if __name__ == "__main__":
    unittest.main()
