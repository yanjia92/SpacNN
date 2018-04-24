from model.ModelFactory import ModelFactory
from checker.Checker import *
from util.AnnotationHelper import *
import unittest

YEAR = 1
DURATION = int(365 * YEAR * 2)


class TestParsingChecker(unittest.TestCase):
    def setUp(self):
        self.parsed = ModelFactory.get_parsed()
        self.ltl = ["[1, {}]".format(DURATION), "T", "failure"]
        self.checker = Checker(self.parsed, ltl=self.ltl, duration=DURATION)

    @timeit
    def test_check(self):
        self.checker.run()


if __name__ == "__main__":
    unittest.main()
