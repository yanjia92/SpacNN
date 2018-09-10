from module.CheckerStepMixin import CheckerStepMixin
from module.AntitheticStepMixin import AntitheticStepMixin


class AnotherStep(CheckerStepMixin, AntitheticStepMixin):
    '''
    class represent a step which a random path consists of
    '''
    def __init__(self, apset, passed_time, holding_time, seed, command):
        '''
        constructor
        :param apset: set containing all ap(str)
        :param passed_time: time passed before arriving at current state
        :param holding_time: time before transition happen
        :param seed: the random number used to generate next state
        :param command: the choosen command to execute
        '''
        self._ap = apset
        self._t = passed_time
        self._d = holding_time
        self._s = seed
        self._c = command

    def get_holding_time(self):
        return self._d

    def get_passed_time(self):
        return self._t

    def get_ap_set(self):
        return self._ap

    def get_command(self):
        return self._c

    def get_seed(self):
        return self._s

    def execute(self):
        self._c.execute()
