# -*- coding:utf-8 -*-
import copy
import itertools
import logging
import math
import random
from collections import OrderedDict
from functools import reduce
import Module
import util.MathUtils as MathUtils
from Module import Constant, Variable
from State import State
from Step import Step
from util.AnnotationHelper import *
from module.NextMove import NextMove

import traceback

logger = logging.getLogger("ModulesFile logging")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

allUpCnt = 0
failureCnt = 0


class ModelType:
    DTMC, CTMC = range(2)


# class represents a DTMC/CTMC model
class ModulesFile(object):
    # id used for generating State object when generating random path
    # should be added 1 whenever before self.nextState get called.
    # _stateId = 0
    INIT_STATE_ID = 0

    def __init__(
            self,
            modeltype=ModelType.DTMC,
            failureCondition=None,
            stopCondition=None,
            initCondition=None,
            modules=None,
            labels=None,
            fb=False):
        self.modules = OrderedDict()
        self.initLocalVars = OrderedDict()
        self.localVars = OrderedDict()
        self.labels = dict()
        self.constants = dict()
        self.modelType = modeltype
        self.scDict = OrderedDict()  # {sstate: [(comm, prob)]}
        self.curState = State(self.INIT_STATE_ID, set())
        self.prevState = State(self.INIT_STATE_ID, set())
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
        self.localVarsList = self.localVars.values()  # used to accelerate speed
        self.state_id = self.INIT_STATE_ID

    def init(self, modules, labels):
        if modules:
            for module in modules:
                self.addModule(module)
        if labels:
            for name, label in labels.items():
                self.addLabel(name, label)
            self._fillInStates()

    # module: module instance
    def addModule(self, module):
        if module is None:
            raise Exception("module cannot be None")
        self.modules[module.name] = module
        # add variables
        for k, v in module.variables.items():
            self.localVars[k] = v
        for k, v in module.variables.items():
            self.initLocalVars[k] = copy.copy(v)
        # add constants
        self.constants.update(module.constants)
        module.modulesFile = self
        for _,comm in module.allCommands().items():
            comm.vs = self.localVars
            comm.cs = self.constants

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

    def setVariable(self, name, val_or_obj):
        if not self.localVars[name]:
            return
        if not isinstance(val_or_obj, Variable):
            self.localVars[name].setValue(val_or_obj)
        else:
            self.localVars[name].setValue(val_or_obj.getValue())

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
        key = self._get_key_of_vars()
        self.curState.ap_set = self.tstate_apset_map[key]
        self.curState.state_id += 1
        return key

    def _initStateAPSetAndStateId(self):
        # self.curState.stateId = self._stateId
        self.curState.state_id = 0
        key = self._get_key_of_vars()
        self.curState.ap_set = self.tstate_apset_map[key]

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
            probs = [p/float(exitRate) for p in probs]

        rnd = random.random()  # random number in [0,1)
        probSum = 0.0
        for index, prob in enumerate(probs):
            probSum += prob
            if probSum >= rnd:
                if self.forcing and self.curState.state_id == 0:
                    holdingTime = MathUtils.randomExpo(
                        exitRate, t=duration)
                else:
                    if self.modelType == ModelType.CTMC:
                        holdingTime = MathUtils.randomExpo(exitRate)
                    else:
                        holdingTime = 1
                enabledCommand = cmds[index]
                enabledCommand.execAction()
                key = self._updateCurAndPrevState()
                return (
                    enabledCommand.name,
                    holdingTime,
                    enabledCommand.prob,
                    enabledCommand.biasingRate,
                    exitRate,
                    biasingExitRate,
                    key)

    def current_key(self):
        return self._get_key_of_vars()

    def step_without_move(self, state_id):
        '''construct a step instance according to system current state'''
        state = self.current_state()
        return Step(state)

    def current_state(self):
        key = self.current_key()
        apset = self.tstate_apset_map[key]
        state_id = self.next_state_id()
        return State(state_id, apset)

    def gen_holding_time(self, exit_rate, duration, first_move):
        if self.forcing and first_move:
            holding_time = MathUtils.randomExpo(
                exit_rate, t=duration)
        else:
            if self.modelType == ModelType.CTMC:
                holding_time = MathUtils.randomExpo(exit_rate)
            else:
                holding_time = 1
        return holding_time

    def gen_next_move(self, cmd_probs, time_passed, duration):
        rnd_num = random.random()
        prob_sum = 0

        cmds = [v[0] for v in cmd_probs]
        probs = [v[1] for v in cmd_probs]
        exit_rate = sum(probs)
        actual_probs = [p/exit_rate for p in probs]
        biasing_exit_rate = None
        if self.fb:
            # todo add failure biasing logic
            pass

        for i, p in enumerate(actual_probs):
            prob_sum += p
            if prob_sum >= rnd_num:
                chosen_cmd = cmds[i]
                holding_time = self.gen_holding_time(exit_rate, duration-time_passed, int(time_passed) == 0)
                return NextMove(chosen_cmd, holding_time, time_passed, exit_rate, biasing_exit_rate)


    def restore_system(self):
        self.restore_vars()
        self.state_id = self.INIT_STATE_ID

    def next_state_id(self):
        previous = self.state_id
        self.state_id += 1
        return previous

    def gen_random_path_V2(self, duration):
        '''return path: [Step]'''
        # 思路：
        # get key of current local vars as key
        # loop until duration met:
        #     get enabled commands
        #     if no enabled commands found:
        #          append empty step to path and restore_system
        #          return path
        #     generate next move info
        #     generate cur state info
        #     construct the step instance
        #     if first move is not possible(holding_time > duration):
        #           add empty step to path and restore_system and return
        #     timesum += holdingtime
        #     if timesum > duration:
        #           trim holdingtime to (duration - timesum)
        #     path.append(step)
        path = []
        if not self.commPrepared:
            self.prepareCommands()
            self.commPrepared = True
        if len(self.scDict) == 0:
            logger.error("Unbounded variables not supported!")
            return None
        time_passed = 0.0
        while time_passed < duration:
            key = self.current_key()
            cmd_probs = self.scDict[key]
            if len(cmd_probs) == 0:
                path.append(self.step_without_move(self.next_state_id()))
                return path
            next_move = self.gen_next_move(cmd_probs, time_passed, duration)
            cur_state = self.current_state()
            # if first move is not possible
            if len(path) == 0 and next_move.holding_time > duration:
                path.append(self.step_without_move(self.next_state_id()))
                self.restore_system()
                return path
            time_passed += next_move.holding_time
            if time_passed > duration:
                next_move.holding_time = duration - time_passed
            # construct step instance
            step = Step(cur_state, next_move)
            path.append(step)

        self.restore_system()
        return path


    # return list of Step instance whose path duration is duration
    # duration: path duration
    # cachedPrefixes: dict type object to store previous checking result for each prefix
    # stopCondition: function that takes variables and constants as parameters to decide when the simulation
    # can be stopped.
    # return (None, path) if cache is not hit
    # else return satisfied(of bool type), path
    def gen_random_path(self, duration, cachedPrefixes=None):
        # Since when initilize a module, all its local variables
        # have been initilized
        random.seed()
        if not self.commPrepared:
            self.prepareCommands()
            self.commPrepared = True
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
                for _,module in self.modules.items():
                    for _,comm in module.allCommands().items():
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
                self.prevState.state_id,
                self.prevState.ap_set,
                holdingTime,
                passedTime,
                transition,
                rate,
                biasingRate,
                exitRate,
                biasingExitRate)
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

    def step_of_current(self, passedTime=None, holdingTime=0.0):
        self._updateCurAndPrevState()
        return Step(
            self.curState.state_id,
            self.curState.ap_set,
            passedTime=passedTime,
            holdingTime=holdingTime
        )

    def getCurrentState(self):
        return self.curState

    def getModelInitState(self):
        return State(0, self.initLocalVars, self)

    def restore_vars(self):
        for k, v in self.initLocalVars.items():
            self.localVars[k].setValue(v.getValue())

    def restoreStates(self):
        self._stateId = 0
        self.curState.state_id = 0
        self.prevState.state_id = 0
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
                if self.forcing and step.isInitState():
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
    def prepareCommands(self):
        # first check whether there's a variable of system that is unbounded
        # in that case, prepareCommands can not be executed.
        if sum(map(int, map(lambda (_,var): not var.bounded, self.localVars.items()))):
            return
        for vsList in itertools.product(
                *[v.allVarsList() for _, v in self.localVars.items()]):
            for v in vsList:
                self.localVars[v.getName()].setValue(v.getValue())
            cmd_probs = list() # [(cmd, prob)]
            for _, module in self.modules.items():
                for _, command in module.commands.items():
                    if command.evalGuard():
                        # make a copy of Command instance
                        # in failure biasing situation when command's rate
                        # needs to be modified.
                        p = None
                        if callable(command.prob):
                            p = command.prob()
                        if p is None:
                            msg = traceback.format_exc()
                            logger.error("command's prob must be callable")
                            logger.error(msg)
                        cmd_probs.append((copy.copy(command), p))
            key = self._get_key_of_vars()
            # sort cmd_probs by prob desc to accerate speed of ModulesFile@nextState
            cmd_probs.sort(key=lambda t: t[1], reverse=True)
            self.scDict[key] = cmd_probs

            vs = self.localVars
            cs = self.constants
            apset = set()
            for name, func in self.labels.items():
                if func(vs, cs):
                    apset.add(name)
            if apset not in self.apset_list:
                self.apset_list.append(apset)
            # sset = str(apset)
            # if sset not in self.sset_set_map.keys():
            #     self.sset_set_map[sset] = apset
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
        # in that case, prepareCommands can not be executed.
        if sum(map(int, map(lambda (_, var): not var.bounded, self.localVars.items()))):
            return
        for vars in itertools.product(
                *[var.allVarsList() for _, var in self.localVars.items()]):
            dictVars = OrderedDict()
            for var in vars:
                dictVars[var.name] = var
            if self.initCondition and self.initCondition(dictVars, self.constants):
                self._I.add(''.join([str(var.getValue()) for var in vars]))
            elif self.failureCondition and self.failureCondition(dictVars, self.constants):
                self._F.add(''.join([str(var.getValue()) for var in vars]))
            else:
                self._U.add(''.join([str(var.getValue()) for var in vars]))

    # change failure and repair rate according to SFB(simple failure biasing)
    # mentioned in p52-nakayama(1).pdf
    def SFB(self, delta):
        if not self.scDict or len(self.scDict) == 0:
            self.prepareCommands()
            self.commPrepared = True
        # iterate through states of model
        # make list of all failure and repair transition
        # update the transition probability in proportion
        for varList in itertools.product(
                *[var.allVarsList() for _, var in self.localVars.items()]):
            key = ''.join([str(v.getValue()) for v in varList])
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
        if not self.commPrepared:
            self.prepareCommands()
            self.commPrepared = True

        for varList in itertools.product(
                *[var.allVarsList() for _, var in self.localVars.items()]):
            key = ''.join([str(var.getValue()) for var in varList])
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
        if not self.commPrepared:
            self.prepareCommands()
            self.commPrepared = True
        key = ''.join([str(var.getValue())
                       for var in self.initLocalVars.values()])
        comms = self.scDict[key]
        return sum(map(lambda comm: comm.prob, comms))

    def updateconstant(self):
        # 当self.constants进行更新时,更新每个command中的constants
        for _, module in self.modules.items():
            for _,comm in module.allCommands().items():
                pass

