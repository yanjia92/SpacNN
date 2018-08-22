from NextMove import NextMove
from module.Module import Command
from test.unittest.ModelTestBase import ModelTestBase
from module.PathGenerator import PathGenerator
from random import random
from module.Step import Step


class TestPathGenerator(ModelTestBase):

    def setUp(self):
        ModelTestBase.setUp(self)
        rands = [random() for _ in range(10000)]
        self._generator = PathGenerator(self._model, rands)

    def _get_model_name(self):
        return "die"

    def test_get_random_path(self):
        self.fail()

    def test__next_move(self):
        self.fail()

    def test__next_step(self):
        self.fail()

    def test__step_without_action(self):
        move = NextMove(1, 1, Command(""), 1.0, 1.0)
        step = Step(set([]), move)
        move_without_action = NextMove(1.0)
        step_without_action = Step(set([]), move_without_action)
        self.assertTrue(self._generator._step_without_action(step_without_action))
        self.assertFalse(self._generator._step_without_action(step))