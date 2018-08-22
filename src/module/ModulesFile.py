# -*- coding:utf-8 -*-
import copy
import itertools
import logging
import math
import random
import threading
from collections import OrderedDict
from functools import reduce
import Module
import util.MathUtils as MathUtils
from Module import Constant, Variable
from State import State
from Step import Step
from util.AnnotationHelper import *
from module.NextMove import NextMove
from PathHelper import *
import Queue
from threading import Thread
from random import random

allUpCnt = 0
failureCnt = 0


class ModelType:
    DTMC, CTMC = range(2)


STEPS_QUEUE_MAX_SIZE = 73000
DEFAULT_STEP_Q_C_WAITING = 0.002
DEFAULT_STEP_Q_P_WAITING = 0.002


class StepGenThd(threading.Thread):
    def __init__(self, model=None):
        threading.Thread.__init__(self)
        self.model = model
        # self.logger = logging.getLogger("StepGenThrd's log")
        # self.logger.addHandler(logging.StreamHandler(sys.stdout))
        # self.logger.setLevel(logging.ERROR)

    def run(self):
        model = self.model

        while True:
            step_gen = model.gen_next_step(passed_time=0.0)  # generate a new step_generator
            queue = model.steps_queue
            passed_time = 0.0
            while True:
                # generate step until a failure state met or duration is reached
                step = next(step_gen)
                if step:
                    queue.put(step)
                    passed_time += step.next_move.holding_time
                    # self.logger.info("one step added, qsize={}".format(queue.qsize()))
                else:
                    pass
                    # self.logger.error("None step generated")
                if int(step.next_move.holding_time) == 0 or int(step.next_move.passed_time) + \
                        int(step.next_move.holding_time) == model.duration:
                    # ModulesFile generate a step without move
                    break
                if step.next_move.cmd:
                    step.next_move.cmd.execute()

            model.restore_system()


class RndProvider(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self._queue = queue
        self._generator = random

    def run(self):
        while True:
            rnd = self._generator()
            self._queue.put(rnd)


# class represents a DTMC/CTMC model
class ModulesFile(object):
    # id used for generating State object when generating random path
    # should be added 1 whenever before self.nextState get called.
    # _stateId = 0
    INIT_STATE_ID = 0
    DEFAULT_DURATION = 730

    def __init__(
            self,
            modeltype=ModelType.DTMC,
            failureCondition=None,
            stopCondition=None,
            initCondition=None,
            modules=None,
            labels=None,
            fb=False,
            duration=0.0):
        self.modules = OrderedDict()
        self.initLocalVars = OrderedDict()
        self.localVars = OrderedDict()
        self.labels = dict()
        self.constants = dict()
        self.model_type = modeltype
        self.scDict = defaultdict(lambda: list())
        self.commPrepared = False
        self.stopCondition = stopCondition
        self.failureCondition = failureCondition
        self.initCondition = initCondition
        self.stateInited = False
        # system's failure states
        self._F = set()
        # system's operational states
        self._U = set()
        # system's initial states, e.g. the 1 state
        self._I = set()
        self.forcing = False
        self.init(modules, labels)
        # todo set this value to be 1.0 for now
        # todo actually it's math.exp(-b0, rarityParameter)
        self.durationThreshold = 1.0
        # failure biasing is enabled or not
        self.fb = fb
        self.sset_set_map = dict()  # s: prefix for string type
        self.tstate_apset_map = dict()  # t: prefix for tuple type
        self.apset_list = []
        self.localVarsList = self.localVars.values()  # used to accelerate speeds
        self.state_id = self.INIT_STATE_ID
        self.duration = 0.0
        # self.duration = duration # time duration to generate random path
        # self.steps_queue = Queue.Queue(maxsize=self.duration * STEPS_QUEUE_FACTOR)
        # self.logger = logging.getLogger("ModulesFile's log")
        # self.logger.addHandler(logging.StreamHandler(sys.stdout))
        # self.logger.setLevel(logging.INFO)
        # self.steps_queue = list()
        self.steps_queue = Queue.Queue(maxsize=STEPS_QUEUE_MAX_SIZE)
        self.STEPS_QUEUE_MAX_SIZE = STEPS_QUEUE_MAX_SIZE
        self.command_synced = False

        # queue containing random numbers [0, 1)
        self._queue = Queue.Queue(maxsize=20)
        self._rndprovider = RndProvider(self._queue)
        self._rndprovider.setDaemon(daemonic=True)
        self._rndprovider.start()

    def get_variables(self):
        return self.localVars.items()

    def get_init_variables(self):
        return self.initLocalVars.values()

    def prepared(self):
        return self.commPrepared

    def type(self):
        return self.model_type

    def init_queue(self):
        # why here using list is thread-safe?
        # first, there's only consumer and producer.
        # second, operations on list is atomic because of GIL
        # self.steps_queue = BlockingQueue()
        # self.steps_queue = Queue.Queue(maxsize=self.duration * STEPS_QUEUE_FACTOR)
        pass

    def init(self, modules, labels):
        if modules:
            for module in modules:
                self.add_module(module)
        if labels:
            for name, label in labels.items():
                self.addLabel(name, label)
            self._fillInStates()

    def _sync_two_commands(self, cmds1, cmds2):
        # cmds1, cmds2是两个同名commands 两个列表
        # sync操作需要将少的commands中的cmd的action和guard合并到多的list中去
        # 假设cmds1的长度小于cmds2
        # 更新guard action prob
        assert len(cmds1) == 1 and len(cmds2) >= 1
        cmd1 = cmds1[0]
        for cmd in cmds2:
            cmd.add_guards(cmd1.get_guards())
            cmd.action.update(cmd1.action)
            assert callable(cmd.prob)
            copied_prob = copy.copy(cmd.prob)
            def prob():
                return copied_prob() * cmd1.prob()
            cmd.prob = prob

    # module: module instance
    def add_module(self, added_mod):
        if added_mod is None:
            return

        # add variables
        for k, v in added_mod.variables.items():
            self.localVars[k] = v
            if hasattr(
                    self, "localVarsList") and v not in set(
                    self.localVarsList):
                self.localVarsList.append(v)
        for k, v in added_mod.variables.items():
            self.initLocalVars[k] = copy.copy(v)

        # add constants
        self.constants.update(added_mod.constants)
        added_mod.modulesFile = self

        # add vs,cs to cmds
        for _, cmds in added_mod.allCommands().items():
            if not isinstance(cmds, list):
                # todo add system-level logger
                print "command stored in module must be list"
            for comm in cmds:
                comm.vs = self.localVars
                comm.cs = self.constants

        if len(self.modules) == 0:
            self.modules[added_mod.name] = added_mod
            return
        for added_cmds in added_mod.allCommands().values():
            name = added_cmds[0].name
            # Don't synchronize over empty-cmd-name commands
            if len(name) == 0:
                continue
            for mod in self.modules.values():
                if name not in mod.allCommands().keys():
                    continue
                cmds = mod.allCommands()[name]
                if len(added_cmds) == 1 and len(cmds) >= 1:
                    # handle both-size-eq-one situation
                    self._sync_two_commands(added_cmds, cmds)
                    # can not pop added_mod's commands because of three-mods-have-same-name-command situation
                    added_mod.allCommands()[name] = mod.allCommands().pop(name)
                elif len(cmds) == 1 and len(added_cmds) > 1:
                    self._sync_two_commands(cmds, added_cmds)
                    mod.allCommands().pop(name)

        self.modules[added_mod.name] = added_mod

    def getModuleByName(self, name):
        if name in self.modules.keys():
            return self.modules[name]
        return None

    # get module's local variables
    # if the variable cannot be found, return None
    # For now, let's assume there are no variables with same name in
    # different modules
    def getLocalVar(self, varName='', moduleName=''):
        var = self.localVars[varName]
        return var

    # For now, let's assume there are no constant with same name in
    # different modules
    def getConstant(self, name='', moduleName=''):
        return self.constants[name]

    # added when trying to write the compiler for the PRISM language
    # store the constant value in ModulesFile unitedly
    def setConstant(self, name, val_or_obj):
        if not isinstance(val_or_obj, Constant):
            self.constants.update({name: Constant(name, val_or_obj)})
            return
        self.constants.update({name: val_or_obj})

    def set_constant(self, obj):
        if isinstance(obj, Constant):
            name = obj.get_name()
            if name in self.constants:
                self.constants[name].set_value(obj.get_value())
                return True
        return False

    def set_constant_name_value(self, name, value):
        if name not in self.constants:
            return False
        else:
            obj = self.constants[name]
            obj.set_value(value)

    def setVariable(self, name, val_or_obj):
        if not self.localVars[name]:
            return
        if not isinstance(val_or_obj, Variable):
            self.localVars[name].set_value(val_or_obj)
        else:
            self.localVars[name].set_value(val_or_obj.get_value())

    # label: a function represents ap
    # label is implemented as a function object that receive
    # ModulesFile instance as the parameter
    def addLabel(self, name, label):
        self.labels[name] = label

    # update self.curState's and self.prevState's apset and stateId
    # according to the system's current state
    def _updateCurAndPrevState(self):
        self.prevState.ap_set = self.curState.ap_set
        self.prevState.state_id = self.curState.state_id
        # key = self._get_key_of_vars()
        key = tuple([v.value for v in self.localVarsList])
        self.curState.ap_set = self.tstate_apset_map[key]
        self.curState.state_id += 1
        return key

    @deprecated("Since State is deprecated.")
    def _initStateAPSetAndStateId(self):
        pass
        # self.curState.state_id = 0
        # key = self._get_key_of_vars()
        # self.curState.ap_set = self.tstate_apset_map[key]
        # key = tuple([v.value for v in self.localVarsList])
        # self.curState = State(self.INIT_STATE_ID,
        #                       self.tstate_apset_map[key])

    # 获取当前代表当前所有变量值的key
    def _get_key_of_vars(self):
        return self._localvars_tuple()
        # return self._localvars_tuple1()

    def _localvars_tuple1(self):
        return tuple(self.localVars.values())

    def _localvars_tuple(self):
        return tuple([v.value for v in self.localVarsList])

    # store new state's info in self.curState
    # (e.g. the transition already happened)
    # store original state's info(localVars) in self.prevState
    # return (transitionname, holdingtime)
    # cmd_probs: [(cmd, cmd_prob)]
    # duration: the time duration before which the transition must occur
    # in initial state, it equals to the Checker.duration(5 years for example)
    # in other allUp state(not initial states), it equals to
    # duration-passedTime.
    @deprecated
    def nextState(self, cmd_probs, duration=0.0):
        # if not self.stateInited:
        #     self.stateInited = True
        #     self._initStateAPSetAndStateId()

        # failure biasing并没有改变一个状态的exit rate
        # exit rate依旧是每个command下的prob(在CTMC模型中,prob表示rate)之和

        exitRate = 0.0
        probs = [t[1] for t in cmd_probs]
        cmds = [t[0] for t in cmd_probs]
        exitRate = sum(probs)
        if self.fb:
            biasingExitRate = sum(
                [command.biasingRate for command in cmds])
            probs = [
                command.biasingRate /
                float(biasingExitRate) for command in cmds]
        else:
            biasingExitRate = None
            probs = [p / float(exitRate) for p in probs]

        rnd = random.random()  # random number in [0,1)
        probSum = 0.0
        for index, prob in enumerate(probs):
            probSum += prob
            if probSum >= rnd:
                if self.forcing and self.curState.state_id == 0:
                    holdingTime = MathUtils.randomExpo(
                        exitRate, t=duration)
                else:
                    if self.model_type == ModelType.CTMC:
                        holdingTime = MathUtils.randomExpo(exitRate)
                    else:
                        holdingTime = 1
                enabledCommand = cmds[index]
                enabledCommand.execute()
                key = self._updateCurAndPrevState()
                return (
                    enabledCommand.name,
                    holdingTime,
                    enabledCommand.prob,
                    enabledCommand.biasing_rate,
                    exitRate,
                    biasingExitRate,
                    key)

    def current_key(self):
        # return self._localvars_tuple()
        return tuple([v.value for v in self.localVarsList])

    def step_without_move(self, key, passed_time):
        '''construct a step instance according to system current state'''
        # state = self.current_state(key)
        ap_set = self.tstate_apset_map[key]
        return Step(ap_set, NextMove(passed_time))

    @deprecated
    def current_state(self, key):
        apset = self.tstate_apset_map[key]
        state_id = self.next_state_id()
        return State(state_id, apset)

    def gen_holding_time(self, exit_rate, duration, first_move):
        if self.forcing and first_move:
            holding_time = MathUtils.randomExpo(
                exit_rate, t=duration)
        else:
            if self.model_type == ModelType.CTMC:
                holding_time = MathUtils.randomExpo(exit_rate)
            else:
                holding_time = 1
        return holding_time

    @deprecated
    def _sync_commmands(self, cmd_probs):
        '''将同名的commands进行合并,并将rates相乘'''
        cmd_map = defaultdict(list)
        for cmd, prob in cmd_probs:
            copied_cmd = copy.copy(cmd)
            copied_cmd.action = copy.copy(cmd.action)
            cmd_map[copied_cmd.name].append((copied_cmd, prob))

        def f(v1, v2):
            cmd1, prob1 = v1
            cmd2, prob2 = v2
            cmd1.action.update(cmd2.action)
            prob1 *= prob2
            return (tuple([cmd1, prob1]))

        # reduce
        for name, cmd_prob_list in cmd_map.items():
            cmd_prob = reduce(f, cmd_prob_list)
            cmd_map[name] = cmd_prob
        return cmd_map.values()

    # @profileit(get_log_dir() + get_sep() + "next_move")
    def next_move(self, cmd_probs, time_passed, rnd=None):
        # cmd_probs: [(cmd, sync_prob)]
        # 所有的cmds的guard均满足,故无需判断
        if not rnd:
            rnd = random()
        prob_sum = 0

        cmd_list = [v[0] for v in cmd_probs] # list of list
        probs = [v[1] for v in cmd_probs]
        exit_rate = sum(probs)
        actual_probs = [p/exit_rate for p in probs]
        # if int(exit_rate) == 0:
        #     print str(cmds)
        biasing_exit_rate = None
        if self.fb:
            # todo add failure biasing logic
            pass

        for i, p in enumerate(actual_probs):
            prob_sum += p
            if prob_sum >= rnd:
                chosen_cmd = cmd_list[i]
                holding_time = self.gen_holding_time(
                    exit_rate, self.duration - time_passed, int(time_passed) == 0)
                return NextMove(
                    passed_time=time_passed,
                    holding_time=holding_time,
                    cmd=chosen_cmd,
                    exit_rate=exit_rate,
                    biasing_exit_rate=biasing_exit_rate)

    def restore_system(self):
        self.restore_vars()
        self.state_id = self.INIT_STATE_ID

    def next_state_id(self):
        previous = self.state_id
        self.state_id += 1
        return previous

    def gen_next_step(self, passed_time=0.0):
        # the stop-generate-step logic should be taken care of by the caller of this function
        # duration = self.duration
        # passed_time = 0.0
        # while passed_time < duration:
        #     step = self.next_step(passed_time)
        #     yield step
        #     passed_time += step.next_move.holding_time
        while True:
            step = self.next_step(passed_time)
            yield step
            passed_time += step.next_move.holding_time

    def next_step(self, passed_time, rnd=None):
        duration = self.duration
        key = tuple([v.value for v in self.localVarsList])
        cmd_probs = self.scDict[key]
        if len(cmd_probs) == 0:
            return self.step_without_move(key, passed_time)
        next_move = self.next_move(cmd_probs, passed_time, rnd=rnd)
        ap_set = self.tstate_apset_map[key]

        # if first move is not possible
        if abs(passed_time) < 1e-8 and next_move.holding_time > duration:
            return self.step_without_move(key, passed_time)

        # trim next_move.holding_time
        # if passed_time + next_move.holding_time > duration:
        #     next_move.holding_time -= (passed_time +
        #                                next_move.holding_time - duration)
        return Step(ap_set, next_move)

    def get_random_path_V2(self):
        ''':return [Step]'''
        if not self.commPrepared:
            self.prepare()
        path = []
        passed_time = 0.0
        duration = self.duration
        while passed_time < duration:
            step = self.next_step(passed_time)
            path.append(step)
            # considering CTMC case
            if abs(step.next_move.holding_time) <= 1e-8:
                last_step = path[-1]
                # if last_step.holding_time + last_step.passed_time <= self.duration:
                #     pass
                # this step is the end step
                self.restore_system()
                return path
            step.next_move.cmd.execute()
            passed_time += step.next_move.holding_time
        self.restore_system()
        return path

    def get_random_path_V3(self):
        '''
        generate path and its antithetic path together.
        :param rnds: list of random number in [0, 1)
        :return: list of Step instance
        '''
        if not self.commPrepared:
            self.prepare()
        paths = []
        rnds = []
        path = []
        passed_time = 0.0
        while passed_time < self.duration:
            rnd = self._queue.get()
            rnds.append(rnd)
            step = self.next_step(passed_time, rnd=rnd)
            path.append(step)
            # considering CTMC case
            if abs(step.next_move.holding_time) <= 1e-8:
                last_step = path[-1]
                # if last_step.holding_time + last_step.passed_time <= self.duration:
                #     pass
                # this step is the end step
                self.restore_system()
                paths.append(path)
                break
            step.next_move.cmd.execute()
            passed_time += step.next_move.holding_time
        self.restore_system()
        if len(paths) == 0:
            paths.append(path)

        # generate the antithetic path
        path = []
        passed_time = 0.0
        while passed_time < self.duration:
            step = self.next_step(passed_time, rnd=1 - rnds.pop(0))
            path.append(step)
            # considering CTMC case
            if abs(step.next_move.holding_time) <= 1e-8:
                last_step = path[-1]
                # if last_step.holding_time + last_step.passed_time <= self.duration:
                #     pass
                # this step is the end step
                self.restore_system()
                paths.append(path)
                break
            step.next_move.cmd.execute()
            passed_time += step.next_move.holding_time
        self.restore_system()
        if len(paths) < 2:
            paths.append(path)
        return paths

    # return list of Step instance whose path duration is duration
    # duration: path duration
    # cachedPrefixes: dict type object to store previous checking result for each prefix
    # stopCondition: function that takes variables and constants as parameters to decide when the simulation
    # can be stopped.
    # return (None, path) if cache is not hit
    # else return satisfied(of bool type), path
    @profileit(get_log_dir() + get_sep() + "pathgenV1")
    def gen_random_path(self, cachedPrefixes=None):
        # Since when initilize a module, all its local variables
        # have been initilized
        random.seed()
        duration = self.duration
        # if not self.commPrepared:
        #     self.prepare_commands()
        #     self.commPrepared = True
        path = list()
        timeSum = 0.0
        passedTime = 0.0
        key = self._get_key_of_vars()
        while timeSum < duration:
            # get enabled commands list
            if len(self.scDict) == 0:
                # 由于存在unbounded变量,无法提前判断所有的变量组合的enabled commands
                # 因此需要手工判断
                cmd_probs = []
                for _, module in self.modules.items():
                    for _, comm in module.allCommands().items():
                        if comm.guard(self.localVars, self.constants):
                            cmd_probs.append((comm, comm.prob()))
            else:
                cmd_probs = self.scDict[key]
            if len(cmd_probs) == 0:
                path.append(self.step_of_current(passedTime=passedTime))
                self.restoreSystem()
                return None, path
            if not self.stateInited:
                self.stateInited = True
                self._initStateAPSetAndStateId()
            transition, holdingTime, rate, biasingRate, exitRate, biasingExitRate, key = self.nextState(
                cmd_probs, duration=duration - timeSum)
            timeSum += holdingTime
            if len(path) == 0 and holdingTime > duration:
                # The first transition is not possible to happen within the given duration
                # In this situation, we think that the transition not made.
                # return the path: [Step(initState, emptyTransition)]
                # self._updateCurAndPrevState()
                step = self.step_of_current()
                path.append(step)
                self.restoreSystem()
                return (None, path)
            if timeSum > duration:
                holdingTime -= (timeSum - duration)
            step = Step(
                state_id=self.prevState.state_id,
                ap_set=self.prevState.ap_set,
                holding_time=holdingTime,
                passed_time=passedTime,
                transition=transition,
                rate=rate,
                biasing_rate=biasingRate,
                exit_rate=exitRate,
                biasing_exit_rate=biasingExitRate)
            path.append(step)
            passedTime += holdingTime

            # 去掉对于stopCondition的判断:因为如果进入failure state,
            # 会在对scdict进行查询时,就进入if逻辑,然后将系统当前状态append到path中去
            # if len(path) >= 1 and self.stopCondition and self.stopCondition(
            #         self.localVars, self.constants):
            #     # add this empty step (with no transition made)
            #     # to represent the state the system currently is in.
            #     path.append(self.step_of_current(passedTime=passedTime))
            #     self.restoreSystem()
            #     return (None, path)

        # MUST be executed before the function returns
        # to prepare generating next random path.
        self.restoreSystem()
        return None, path

    @deprecated
    def step_of_current(self, passedtime=None, holdingTime=0.0):
        self._updateCurAndPrevState()
        return Step(
            self.curState.state_id,
            self.curState.ap_set,
            passedTime=passedtime,
            holdingTime=holdingTime
        )

    def getCurrentState(self):
        return self.curState

    @deprecated
    def getModelInitState(self):
        return State(0, self.initLocalVars, self)

    def restore_vars(self):
        for k, v in self.initLocalVars.items():
            self.localVars[k].set_value(v.get_value())

    @deprecated
    def restoreStates(self):
        self._stateId = 0
        # self.curState.state_id = 0
        # self.prevState.state_id = 0
        self.curState = State(self.INIT_STATE_ID, set())
        self.prevState = State(self.INIT_STATE_ID, set())
        # self.curState.clearAPSet()
        # self.prevState.clearAPSet()
        self.stateInited = False

    def restoreSystem(self):
        self.restore_vars()
        self.restoreStates()

    # return the probability a path is generated under
    # the original distribution
    # if biasing is set, return the probability under the biased
    # distribution
    # path: list of Step instance
    # biasing: boolean variable to specify whether any FB method is used.
    # duration: used to compute the likelihood ratio of the transition from allUp state
    # when forcing is used.
    def probForPath(self, path, biasing=False, duration=None):
        # the probability density function of exponential distribution with
        # parameter lamda
        def pdf(lamda, x):
            return lamda * math.exp(-1 * lamda * x)

        # the probability density function f(x) of exponential distribution with
        # the parameter lamda on condition that x is less than duration
        # e.g. the pdf of the first transition when forcing is applied.
        # lamda: the exitRate of step instance
        # x: the holdingTime of step instance
        # duration: the time before which the first transition must happen
        def forcingPDF(lamda, x, duration):
            if duration:
                return (lamda * math.exp(-1 * lamda * x)) / \
                    (1 - math.exp(-1 * lamda * duration))

        if biasing:
            prob = 1.0
            for step in path:
                # step.biasingExitRate is the sum of probability not the rate
                lamda = step.exitRate
                x = step.holdingTime
                if self.forcing and step.isInitState("ALL UP LABEL"):
                    prob *= step.biasingRate / step.biasingExitRate * \
                        forcingPDF(lamda, x, duration)
                else:
                    prob *= step.biasingRate / \
                        step.biasingExitRate * pdf(lamda, x)
            return prob
        else:
            return reduce(lambda x, y: x *
                          y, map(lambda step: step.rate /
                                 step.exitRate *
                                 pdf(step.exitRate, step.holdingTime), path))

        # if biasing and self.forcing and :
        #     # BFB plus forcing
        #     prob = 1.0
        #     initStep = path[0]
        #     # compute the probability of the first transition
        #     # happening within time
        #     prob *= initStep.biasingRate * forcingPDF(
        #         initStep.exitRate,
        #         initStep.holdingTime,
        #         3.0 / initStep.exitRate) / initStep.biasingExitRate
        #     # Since the last step generated by self.gen_random_path() is an empty Step
        #     # e.g. it contains no transition information, since the simulation stop
        #     # when it reaches a failure state, and no transition made ever since.
        #     # So emit last step when calculating the likelihood of the path.
        #     return prob * reduce(lambda x, y: x *
        #                          y, map(lambda step: step.biasingRate /
        #                                 step.biasingExitRate *
        #                                 pdf(step.biasingExitRate, step.holdingTime), path[1:-
        #                                                                                   1]))
        # else:
        #     # original distribution
        #     return reduce(lambda x, y: x *
        #                   y, map(lambda step: step.rate /
        #                          step.exitRate *
        #                          pdf(step.exitRate, step.holdingTime), path[:-
        # 1]))

    # generate enabled commands for each state of the model beforehand
    # to accelerate the speed of generating random path
    # ATTENTION: when running experiment, constant value must be set before calling this method
    def prepare(self):
        '''generate enabled commands and probs for each state'''

        # none of the variables can be unbounded.
        if sum(map(int,
                   map(lambda __var: not __var[1].bounded,
                       self.localVars.items()))):
            return
        for vsList in itertools.product(
                *[v.allVarsList() for _, v in self.localVars.items()]):
            for v in vsList:
                self.localVars[v.get_name()].set_value(v.get_value())
            cmd_probs = list()
            for _, module in self.modules.items():
                for _, commands in module.commands.items():
                    for command in commands:
                        if command.evaluate():
                            # make a copy of Command instance
                            # in failure biasing situation when command's rate
                            # needs to be modified.
                            p = None
                            if callable(command.prob):
                                p = command.prob()
                            if p is None:
                                # todo call system-level logger
                                print "prob must be a function, cmd: {}".format(command)

                            cmd_probs.append((copy.copy(command), p))
            key = tuple([v.value for v in self.localVarsList])
            # sort cmd_probs by prob desc to accerate speed of
            # ModulesFile@nextState
            # cmd_probs.sort(key=lambda t: t[1], reverse=True)

            self.scDict[key] = cmd_probs

            vs = self.localVars
            cs = self.constants
            apset = set()
            for name, func in self.labels.items():
                if func(vs, cs):
                    apset.add(name)
            if apset not in self.apset_list:
                self.apset_list.append(apset)
            sset = str(apset)
            if sset not in self.sset_set_map.keys():
                self.sset_set_map[sset] = apset
            self.tstate_apset_map[key] = apset
        self.restoreSystem()
        self.commPrepared = True

    def exportPathTo(self, path, filename):
        f = file(filename, 'w')
        f.write('stateId, apSet, passedTime, holdingTime, transition\n')
        for step in path:
            f.write(
                '%d, %s, %ss, %ss, %s\n' %
                (step.stateId, str(
                    step.apSet), step.passedTime, step.holdingTime, step.transition))
        f.close()

    # fill in system failure and operational states in self._F and self._U
    # for example, '000' is a failure state representation
    # '111' is a operational state representation
    def _fillInStates(self):
        # first check whether there's a variable of system that is unbounded
        # in that case, prepare_commands can not be executed.
        if sum(map(int,
                   map(lambda __var1: not __var1[1].bounded,
                       self.localVars.items()))):
            return
        for vars in itertools.product(
                *[var.allVarsList() for _, var in self.localVars.items()]):
            dictVars = OrderedDict()
            for var in vars:
                dictVars[var.name] = var
            if self.initCondition and self.initCondition(
                    dictVars, self.constants):
                self._I.add(''.join([str(var.get_value()) for var in vars]))
            elif self.failureCondition and self.failureCondition(dictVars, self.constants):
                self._F.add(''.join([str(var.get_value()) for var in vars]))
            else:
                self._U.add(''.join([str(var.get_value()) for var in vars]))

    # change failure and repair rate according to SFB(simple failure biasing)
    # mentioned in p52-nakayama(1).pdf
    def SFB(self, delta):
        # if not self.scDict or len(self.scDict) == 0:
        #     self.prepare_commands()
        #     self.commPrepared = True
        # iterate through states of model
        # make list of all failure and repair transition
        # update the transition probability in proportion
        for varList in itertools.product(
                *[var.allVarsList() for _, var in self.localVars.items()]):
            key = ''.join([str(v.get_value()) for v in varList])
            commands = self.scDict[key]
            if key in self._I or key in self._F:
                for comm1 in commands:
                    comm1.biasingRate = comm1.prob
            else:
                failureCommands = [
                    comm for comm in commands if comm.kind == Module.CommandKind.FAILURE]
                repairCommands = [
                    comm for comm in commands if comm.kind == Module.CommandKind.REPAIR]
                if len(failureCommands) == 0 or len(repairCommands) == 0:
                    logging.error("prepare commands error since in SFB")
                sumF = sum([comm.prob for comm in failureCommands])
                if sumF > 0:
                    for comm in failureCommands:
                        comm.biasingRate = delta * comm.prob / sumF
                else:
                    logging.error('sumOfRate is 0')
                    logging.error('%s' % str(
                        [(comm.name, comm.prob) for comm in failureCommands]))
                sumR = sum([comm.prob for comm in repairCommands])
                for comm in repairCommands:
                    comm.biasingRate = comm.prob * ((1 - delta) / sumR)

    # balanced failure biasing method according to 00717132.pdf
    def BFB(self, delta):
        # if not self.commPrepared:
        #     self.prepare_commands()
        #     self.commPrepared = True

        for varList in itertools.product(
                *[var.allVarsList() for _, var in self.localVars.items()]):
            key = ''.join([str(var.get_value()) for var in varList])
            enabledComms = self.scDict[key]
            if key in self._I:
                # initial state, no repair transition
                for comm in enabledComms:
                    comm.biasingRate = 1.0 / len(enabledComms)
            elif key in self._F:
                # failure states
                for comm in enabledComms:
                    comm.biasingRate = comm.prob
            else:
                # U\{1} states
                # number of failure transitions
                numF = len(
                    [comm1 for comm1 in enabledComms if comm1.kind == Module.CommandKind.FAILURE])
                # list of repair transitions
                repairComms = [
                    comm2 for comm2 in enabledComms if comm2.kind == Module.CommandKind.REPAIR]
                # sum of rate of repair transitions
                sumR = sum([rc.prob for rc in repairComms])
                for fc in [
                        comm3 for comm3 in enabledComms if comm3.kind == Module.CommandKind.FAILURE]:
                    fc.biasingRate = delta / numF
                for rc in repairComms:
                    rc.biasingRate = (1 - delta) * rc.prob / sumR
                # NONE type commands
                for command in enabledComms:
                    if command.kind == Module.CommandKind.NONE:
                        command.biasingRate = command.prob

    # the exit rate of allUp state
    def q1(self):
        # if not self.commPrepared:
        #     self.prepare_commands()
        #     self.commPrepared = True
        key = ''.join([str(var.get_value())
                       for var in self.initLocalVars.values()])
        comms = self.scDict[key]
        return sum(map(lambda comm: comm.prob, comms))

    @deprecated
    def updateconstant(self):
        # 当self.constants进行更新时,更新每个command中的constants
        for _, module in self.modules.items():
            for _, comm in module.allCommands().items():
                pass
