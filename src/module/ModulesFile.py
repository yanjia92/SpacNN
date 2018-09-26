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
from PathHelper import *
from os.path import *

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
        self._status_commands_map = defaultdict(lambda: list())
        self._status_apset_map = OrderedDict()
        self._prepared = False
        self._duration = None # random path length in time units
        # dump file path used to store self._status_command_map and _status_apset_map
        self._preparation_dump_path = get_data_dir() + get_sep() + "modulesfile_dump.pkl"

        # queue containing random numbers [0, 1)
        self._queue = Queue.Queue(maxsize=100)
        self._rndprovider = RndProvider(self._queue)
        self._rndprovider.setDaemon(daemonic=True)
        self._rndprovider.start()

    def set_prepared(self, prepared):
        '''
        setter of boolean prepared
        :param prepared: boolean
        :return: None
        '''
        self._prepared = prepared

    def set_duration(self, duration):
        self._duration = duration

    # module: module instance
    def add_module(self, m):
        '''
        add module to the model
        :param m: Module instance
        :return: None
        '''
        if m is None:
            return

        # add variables into model
        self._vars.update(m.get_variables())
        self._init_vars.update(deepcopy(m.get_variables()))

        # add constant into model
        self._constants.update(m.get_constants())
        m.set_model(self)

        if len(self._modules) == 0:
            self._modules[m.get_name()] = m
            for name, commands in m.get_commands().items():
                self._commands[name] = commands
                self._fill_commands(commands)
            return

        # join same-name commands
        for added_cmds in m.get_commands().values():
            if not len(added_cmds):
                continue
            name = added_cmds[0].get_name()
            if len(name) != 0 and len(self._commands[name]) > 0:
                joined_commands = self._join_commands(added_cmds, self._commands[name])
                self._fill_commands(joined_commands)
                self._commands[name] = joined_commands
            else:
                self._fill_commands(added_cmds)
                self._commands[name].extend(added_cmds)

        # add the module itself
        self._modules[m.get_name()] = m

    def _join_commands(self, commands1, commands2):
        '''
        将两组同名commands进行同步
        即guard作并处理
        update做并处理
        prob相乘
        :param commands1: list of Command instance with same name
        :param commands2: list of Command instance with same name
        :return: joined command list
        '''
        return [self._join_command(c1, c2) for c1, c2 in itertools.product(commands1, commands2)]

    def _join_command(self, c1, c2):
        '''
        将两个同名Command实例进行联立
        即guard做并
        prob相乘
        update进行合并
        :param c1: Command instance
        :param c2: Command instance
        :return: joined Command instance
        '''
        name = c1.get_name()
        guard1 = c1.get_guard()
        guard2 = c2.get_guard()

        def guard(vs, cs):
            return guard1(vs, cs) and guard2(vs, cs)

        def prob():
            p1 = c1.get_prob()
            p2 = c2.get_prob()
            if callable(p1) and callable(p2):
                return p1() * p2()
            raise Exception("Command's prob property must be a function.")
        update = dict()
        update.update(c1.get_update())
        update.update(c2.get_update())
        return CommandFactory.generate(name, guard, prob, update)

    def _fill_commands(self, commands):
        '''
        set vs and cs property of commands
        :param commands: list of Command instance
        :return: None
        '''
        for c in commands:
            c.set_variables(self._vars)
            c.set_constants(self._constants)

    def get_module(self, n):
        if n not in self._modules:
            raise Exception("Model contains no module named {}".format(n))
        return self._modules[n]

    def get_constant(self, n):
        if n not in self._constants:
            raise Exception("Model contains no constant named {}".format(n))
        return self._constants[n]

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
        if not self._prepared:
            self.prepare()
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

    def prepare(self):
        '''
        generate enabled commands and probability for each state
        all unsure constants must be set before calling this method.
        :return: None
        '''
        # check for unsure parameters
        print "Preparation began."
        for constant in self._constants.values():
            if constant.get_value() is None:
                raise Exception("Set unsure parameter before run ModulesFile's prepare method")
        for values in itertools.product(*[variable.possible_values() for variable in self._vars.values()]):
            for name, value in values:
                self._vars[name].set_value(value)
            enabled = []
            key = self._status_as_key()
            for commands in self._commands.values():
                for c in commands:
                    # p = c.get_prob()
                    # if callable(p):
                    #     c.set_prob(p())
                    if c.evaluate():
                        enabled.append(copy(c))
            self._status_commands_map[key] = enabled
            apset = set()
            for n, f in self._labels.items():
                if f(self._vars, self._constants):
                    apset.add(n)
            if apset in self._status_apset_map.values():
                index = self._status_apset_map.values().index(apset)
                apset = self._status_apset_map.values()[index]
            self._status_apset_map[key] = apset
        self._restore()
        self._prepared = True
        print "Preparation finished."

    def _restore(self):
        self._restore_vars()