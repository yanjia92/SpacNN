from ModelTestBase import ModelTestBase
from checker.Checker import Checker


class CheckerTestBase(ModelTestBase):
    def setUp(self):
        ModelTestBase.setUp(self)
        self._parsed_ltl = self.ltl_parser.parse_line(self._get_ltl())
        self._checker = Checker(model=self._model, ltl=self._parsed_ltl, samples=self._get_samples(), duration=self._get_duration())

    def _get_ltl(self):
        pass

    def _get_samples(self):
        pass

    def _get_duration(self):
        pass