# -*- coding:utf-8 -*-
from copy import deepcopy


class Simulator(object):

    def __init__(self, spec):
        '''
        构造函数
        :param spec: dict containing constructive data
        '''
        self._vars = spec["vars"]  # list of variables
        self._commands = spec["commands"]  # list of commands
        self._state_as_key = spec["state_as_key"]

    def get_reachable(self):
        '''
        返回可达状态集合
        :return: [tuple] every tuple represents a state
        '''
        results = set()  # list containing all reachable states in tuple
        variables = deepcopy(self._vars)
        results.add(self._state_as_key(variables))

        return results
