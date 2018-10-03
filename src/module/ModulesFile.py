# -*- coding:utf-8 -*-
from copy import *
import itertools
import random
from collections import OrderedDict
from util.AnnotationHelper import *
import Queue
from threading import Thread
from random import random
from module.CommandFactory import CommandFactory
from util.MathUtils import expo_rnd
from module.AnotherStep import AnotherStep
from bisect import bisect
from util.AnnotationHelper import profileit

STEPS_QUEUE_MAX_SIZE = 73000
DEFAULT_STEP_Q_C_WAITING = 0.002
DEFAULT_STEP_Q_P_WAITING = 0.002


class RndProvider(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self._queue = queue
        self._generator = random

    def run(self):
        while True:
            rnd = self._generator()
            self._queue.put(rnd)


class ModelType(object):
    DTMC, CTMC = range(2)


class ModulesFile(object):

    STATES_KEY = "states"
    TRANSITIONS_KEY = "transitions"

    '''
    class representing a DTMC/CTMC model
    '''
    def __init__(self, model_type=ModelType.DTMC):
        self._modules = OrderedDict()
        # contain information concerning model init status
        self._init_vars = OrderedDict()
        self._vars = OrderedDict()
        self._labels = dict()
        self._constants = dict()
        self._commands = defaultdict(list)
        self._type = model_type
        self._status_commands_map = defaultdict(list)
        self._status_apset_map = OrderedDict()
        self._parsed = False
        self._duration = None # random path length in time units
        self._reachable = set()  # 可达状态
        self._apset_repo = []

        # queue containing random numbers [0, 1)
        self._queue = Queue.Queue(maxsize=100)
        self._rndprovider = RndProvider(self._queue)
        self._rndprovider.setDaemon(daemonic=True)
        self._rndprovider.start()

    def set_duration(self, duration):
        self._duration = duration

    def _join_commands(self, *comms_list):
        '''
        将多组同名commands进行同步
        即guard作并处理
        update做并处理
        prob相乘
        :param comms_list: list of list
        :return: joined command list
        '''
        return [self._join_command(*comms) for comms in itertools.product(*comms_list)]

    def _join_command(self, *commands):
        '''
        将多个同名Command实例进行联立
        即guard做并
        prob相乘
        update进行合并
        :param commands: commands with same name that need to be joined
        :return: joined Command instance
        '''
        if not commands or not len(commands):
            return
        name = commands[0].get_name()
        guards = [c.get_guard() for c in commands]

        def guard(vs, cs):
            results = [g(vs, cs) for g in guards]
            for result in results:
                if not result:
                    return False
            return True

        def prob():
            result = 1.0
            for p in [c.get_prob() for c in commands]:
                if callable(p):
                    result *= p()
                else:
                    result *= p
            return result
        update = dict()
        for c in commands:
            update.update(c.get_update())
        return CommandFactory.generate(name, guard, prob, update)

    def _fill_commands(self, commands):
        '''
        set vs and cs property of commands
        :param commands: list of Command instance
        :return: None
        '''
        if not commands or not len(commands):
            return
        for c in commands:
            c.set_variables(self._vars)
            c.set_constants(self._constants)

    def add_module(self, m):
        '''
        不join同名commands
        but compute on the fly
        :param m: Module instance
        :return: None
        '''
        if not m:
            return
        m.set_model(self)
        self._vars.update(m.get_variables())
        self._init_vars.update(deepcopy(m.get_variables()))
        self._constants.update(m.get_constants())
        self._modules[m.get_name()] = m
        for commands in m.get_commands().values():
            self._fill_commands(commands)

    def get_module(self, n):
        if n not in self._modules:
            raise Exception("Model contains no module named {}".format(n))
        return self._modules[n]

    def get_parameter(self, n):
        '''
        获取参数，同获取constant
        :param n: name
        :return: value (could be function)
        '''
        if n not in self._constants:
            raise Exception("Model contains no constant named {}".format(n))
        return self._constants[n].get_value()

    def get_constants(self):
        return self._constants

    def set_constant(self, k, v):
        '''
        set unsure parameter
        :param k: parameter name
        :param v: parameter value
        :return:
        '''
        obj = self._constants[k]
        if not obj:
            raise Exception("model contain no parameter named {}".format(k))
        obj.set_value(v)

    def get_variables(self):
        return self._vars.values()

    def get_commands(self, name=None):
        '''
        this method is mainly used for unittest
        :param name: command's name
        :return: list of [Command] instance
        '''
        if not name or name not in self._commands:
            return self._commands.values()
        return self._commands[name]

    def get_variable(self, n):
        if n not in self._vars:
            raise Exception("Model contains no variable named {}".format(n))
        return self._vars[n]

    def add_constant(self, c):
        '''
        供PRISMParser调用
        :param c: Constant instance
        :return: None
        '''
        self._constants[c.get_name()] = c

    def add_label(self, n, f):
        '''
        增加label
        :param n: label name
        :param f: function of signature f(vs, cs)
        :return: None
        '''
        if len(n) > 0 and n not in self._labels and f is not None:
            self._labels[n] = f
        else:
            raise Exception("Invalid parameter passed to add_label: n:{}, f:{}".format(n, f))

    def gen_path(self, init_state=None, seeds=None):
        '''
        产生随机路径
        if seeds is not null, this method is used to generate an antithetic path
        :param init_state: init state of type {name: value}
        :param seeds: a list of random number that is in [0, 1] used to generate next state
        :return: path typed of list of AnotherStep
        '''
        if not self._parsed:
            self._parse_model()
        if init_state is not None and len(init_state) > 0:
            for n, v in init_state.items():
                self._vars[n].set_value(v)
        path = []
        d = self._duration
        t = 0.0 # passed_time
        while t <= d:
            seed = None
            if seeds is not None and len(seeds) > 0:
                seed = seeds.pop(0)
            step = self._gen_next(t, seed=seed)
            path.append(step)
            if step.get_holding_time() + t > d:
                self._restore()
                return path
            step.execute()
            t += step.get_holding_time()
        self._restore()
        return path

    def rearrange(self, paths, results):
        '''
        根据批量路径的训练结果统计每个出边上的满足性质和不满足性质的路径的条数，并根据hit_cnt-miss_cnt重新对每个状态下的所有next-status进行重新排序
        :param paths: list of path
        :param results: list of boolean representing checking results
        :return: None
        '''
        for p, r in zip(paths, results):
            for step in p:
                if r:
                    step.get_command().incr_hit_cnt()
                else:
                    step.get_command().incr_miss_cnt()
        for _, commands in self._status_commands_map.items():
            commands.sort(key=lambda c: c.get_hit_cnt() - c.get_miss_cnt())

    def _restore_vars(self):
        for k, v in self._init_vars.items():
            self._vars[k].set_value(v.get_value())

    def _status_as_key(self):
        '''
        根据系统当前所处的状态产生具有唯一性的key
        :return: None
        '''
        return tuple([variable.get_value() for variable in self._vars.values()])

    def _key2status(self, key):
        '''
        根据key将系统中的变量设置为key中对应的值
        :param key: tuple
        :return:
        '''
        for value, variable in zip(key, self._vars.values()):
            variable.set_value(value)

    def _gen_next(self, time, seed=None):
        '''
        根据目前已经流逝的时间以及当前系统所处的状态产生AnotherStep实例
        :param time: passed time
        :param seed: random number used to generate next state, used if provided
        :return: AnotherStep instance
        '''
        key = self._status_as_key()
        apset = self._status_apset_map[key]
        passed_time = time
        enabled = self._status_commands_map[key]
        if seed is None:
            seed = self._queue.get()
        command = self._choose_next(enabled, seed)
        ps = [c.get_prob() for c in enabled]
        probs = []
        for p in ps:
            if callable(p):
                probs.append(p())
            else:
                probs.append(p)
        exit_rate = sum(probs)
        holding_time = 1
        if self._type == ModelType.CTMC:
            if exit_rate == 0:
                raise Exception("Exit rate can not be zero")
            holding_time = expo_rnd(exit_rate)
        return AnotherStep(apset, passed_time, holding_time, seed, command)

    def _choose_next(self, enabled, seed):
        '''
        choose the command to execute according to the seed
        :param enabled: all enabled command instance
        :param seed: the random number([0,1]) to use
        :return: chosen command
        '''
        if not enabled or len(enabled) == 0:
            return None
        ps = map(lambda c: c.get_prob(), enabled)
        probs = []
        for p in ps:
            if not callable(p):
                probs.append(p)
            else:
                probs.append(p())
        exit_rate = sum(probs)
        for i, p in enumerate(probs):
            probs[i] = p/exit_rate
        acc_arr = []
        acc = 0.0
        for p in probs:
            acc += p
            acc_arr.append(acc)
        index = bisect(acc_arr, seed)
        if index < 0 or index >= len(enabled):
            raise Exception("Index out of range: {}".format(index))
        return enabled[index]

    def _restore(self):
        self._restore_vars()

    def stat(self):
        '''
        返回模型的一些统计信息，即可达状态数与这些状态状态之间的状态数
        :return: dict
        '''
        if not self._parsed:
            self._parse_model()
        data = {}
        if len(self._status_commands_map) or len(self._status_apset_map):
            data[self.STATES_KEY] = len(self._status_commands_map)
        else:
            variables = self._vars.values()
            sizes = map(lambda v: v.possible_values_cnt(), variables)
            data[self.STATES_KEY] = reduce(lambda v1, v2: v1 * v2, sizes)
        transitions = 0
        for commands in self._status_commands_map.values():
            transitions += len(commands)
        data[self.TRANSITIONS_KEY] = transitions
        return data

    @profileit("parse_model")
    def _parse_model(self):
        '''
        得到模型中所有的可达状态
        每个可达状态下的使能command
        以及每个状态的对应的apset
        :return:
        '''
        try:
            queue = []
            key = self._status_as_key()
            queue.append(key)
            self._reachable.add(key)
            while len(queue):
                key = queue.pop(0)
                self._key2status(key)
                #  compute apsets for this state
                apset = set()
                for name, func in self._labels.items():
                    if func(self._vars, self._constants):
                        apset.add(name)
                for index, _apset in enumerate(self._apset_repo):
                    if _apset == apset:
                        apset = _apset
                self._status_apset_map[key] = apset
                # compute enabled commands on the fly
                # list of dict with each dict containing command only enabled at the current state
                comm_dict_list = []
                name_set = set()
                joined_comms = defaultdict(list)
                for comm_dict in [m.get_commands() for m in self._modules.values()]:
                    d = {}
                    for name, comms in comm_dict.items():
                        if name and len(name):
                            name_set.add(name)
                        d[name] = filter(lambda c: c.evaluate(), comms)
                    comm_dict_list.append(d)
                for name in name_set:
                    comms_list = [comm_dict[name] for comm_dict in comm_dict_list]
                    joined_comms[name] = self._join_commands(*comms_list)
                for commands in joined_comms.values():
                    for comm in commands:
                        # store reachable state
                        comm.execute()
                        next_key = self._status_as_key()
                        self._key2status(key)
                        if next_key not in self._reachable:
                            self._reachable.add(next_key)
                            queue.append(next_key)
                        # store enabled commands
                        self._status_commands_map[key].append(copy(comm))
        finally:
            self._parsed = True
            self._restore()