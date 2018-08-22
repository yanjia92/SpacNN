# -*- coding: utf-8 -*-
from copy import deepcopy
from module.ModulesFile import ModelType
from util.MathUtils import randomExpo
from module.NextMove import NextMove
from Step import Step


class PathGenerator(object):
    def __init__(self, model, rands):
        '''
        constructor
        :param model:
        :param rands:
        '''
        self._vars = model.get_variables()
        # self._init_vars = deepcopy(self._vars)
        if not model.prepared():
            model.prepare()
        self._state_cmd_map = model.scDict
        self._rands = rands
        self._type = model.type()
        self._state_ap_map = model.tstate_apset_map

    def get_random_path(self, duration, count=1):
        '''
        generate a duration-length random path from the specified model
        :param duration:
        :param count:
        :return:list of step instance
        '''
        path = []
        self._before_generate_path()
        passedtime = 0.0
        while passedtime < duration:
            step = self._next_step(passedtime, duration)
            path.append(step)
            if self._step_without_action(step):
                self._after_generate_path()
                return path
            step.execute()
            self._after_state_changed()
            passedtime += step.holding_time
        self._after_generate_path()
        return path

    def _next_move(self, passedtime, enabled_cmds):
        if not enabled_cmds or len(enabled_cmds) < 1:
            return NextMove(passedtime)
        probsum = sum([t[1] for t in enabled_cmds])
        enabled_cmds = map(lambda t: tuple([t[0], t[1] / probsum]), enabled_cmds)
        random = self._rands.pop(0)
        accumulated = 0.0
        for idx, _tuple in enumerate(enabled_cmds):
            accumulated += _tuple[1]
            if accumulated >= random:
                holding_time = 1
                if self._type == ModelType.CTMC:
                    holding_time = randomExpo(probsum)
                return NextMove(passedtime, holding_time, _tuple[0], probsum, 0.0)

    def _next_step(self, passedtime, duration):
        key = tuple([lambda v: v.get_value() for v in self._vars])
        enabled_cmds = self._state_cmd_map[key]
        next_move = self._next_move(passedtime, enabled_cmds)
        if passedtime + next_move.holding_time > duration:
            next_move = NextMove(passedtime)
        apset = self._state_ap_map[key]
        return Step(apset, next_move)

    def _after_state_changed(self):
        pass

    def _after_generate_path(self):
        pass

    def _before_generate_path(self):
        pass

    def _step_without_action(self, step):
        return step.next_move.cmd is None