# -*- coding:utf-8 -*-
from functools import reduce
import logging
from State import State
from Step import Step
import Module
from collections import OrderedDict
import copy
import random
import itertools
import math
import util.MathUtils as MathUtils
import sys

logger = logging.getLogger("ModulesFile logging")

# 文件日志
file_handler = logging.FileHandler("../log/model.log")
# 为logger添加日志处理器
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


allUpCnt = 0
failureCnt = 0


class ModelType:
    DTMC, CTMC = range(2)

# class represents a DTMC/CTMC model
class ModulesFile(object):
    # id used for generating State object when generating random path
    # should be added 1 whenever before self.nextState get called.
    _stateId = 0

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
        # store all enabled commands for each state
        self.scDict = OrderedDict()
        self.curState = State(self._stateId, set())
        self.prevState = State(self._stateId, set())
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
        if module == None:
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
        return self.localVars[varName]

    # For now, let's assume there are no constant with same name in
    # different modules
    def getConstant(self, name='', moduleName=''):
        return self.constants[name]

    # used for experiments with different constants like PRISM
    def setConstant(self, name, value, module):
        module = self.getModuleByName(module)
        if module:
            return module.setConstant(name, value)

    # added when trying to write the compiler for the PRISM language
    # store the constant value in ModulesFile unitedly
    def addConstant(self, name, value):
        self.constants.update({name : value})

    # label: a function represents ap
    # label is implemented as a function object that receive
    # ModulesFile instance as the parameter
    def addLabel(self, name, label):
        self.labels[name] = label

    # update self.curState's and self.prevState's apset and stateId
    # according to the system's current state
    def _updateCurAndPrevState(self):
        self.prevState.apSet = self.curState.apSet.copy()
        self.prevState.stateId = self.curState.stateId
        self.curState.updateAPs(self.localVars, self.constants, self.labels)
        self._stateId += 1
        self.curState.stateId = self._stateId

    def _initStateAPSetAndStateId(self):
        self.curState.stateId = self._stateId
        self.curState.updateAPs(
            self.initLocalVars,
            self.constants,
            self.labels)

    # store new state's info in self.curState
    # (e.g. the transition already happened)
    # store original state's info(localVars) in self.prevState
    # return (transitionname, holdingtime)
    # enabledCommands: the enabled commands of current state
    # duration: the time duration before which the transition must occur
    # in initial state, it equals to the Checker.duration(5 years for example)
    # in other allUp state(not initial states), it equals to
    # duration-passedTime.
    def nextState(self, enabledCommands, duration=0.0):
        if not self.stateInited:
            self.stateInited = True
            self._initStateAPSetAndStateId()

        # failure biasing并没有改变一个状态的exit rate
        # exit rate依旧是每个command下的prob(在CTMC模型中,prob表示rate)之和

        exitRate = 0.0
        for comm in enabledCommands:
            if hasattr(comm.prob, '__call__'):
                exitRate += comm.prob()
            else:
                exitRate += comm.prob
        if self.fb:
            biasingExitRate = sum(
            [command.biasingRate for command in enabledCommands])
            probs = [
                command.biasingRate /
                float(biasingExitRate) for command in enabledCommands]
        else:
            biasingExitRate = None
            probs = []
            for comm in enabledCommands:
                if hasattr(comm.prob, '__call__'):
                    probs.append(comm.prob()/exitRate)
                else:
                    probs.append(comm.prob/exitRate)

        rnd = random.random()  # random number in [0,1)
        probSum = 0.0
        for index, prob in enumerate(probs):
            probSum += prob
            if probSum >= rnd:
                if self.initCondition and self.initCondition(self.localVars, self.constants):
                    holdingTime = MathUtils.randomExpo(
                        exitRate, t=duration, forcing=self.forcing)
                else:
                    holdingTime = MathUtils.randomExpo(exitRate)
                holdingTime = [1, holdingTime][self.modelType]
                enabledCommand = enabledCommands[index]
                enabledCommand.execAction()
                self._updateCurAndPrevState()
                return (
                    enabledCommand.name,
                    holdingTime,
                    enabledCommand.prob,
                    enabledCommand.biasingRate,
                    exitRate,
                    biasingExitRate)

    # return list of Step instance whose path duration is duration
    # duration: path duration
    # cachedPrefixes: dict type object to store previous checking result for each prefix
    # stopCondition: function that takes variables and constants as parameters to decide when the simulation
    # can be stopped.
    # return (None, path) if cache is not hit
    # else return satisfied(of bool type), path
    def genRandomPath(self, duration, cachedPrefixes=None):
        # Since when initilize a module, all its local variables
        # have been initilized
        if not self.commPrepared:
            self.prepareCommands()
            self.commPrepared = True
        path = list()
        timeSum = 0.0
        passedTime = 0.0
        strPath = ''
        while timeSum < duration:
            # get enabled commands list
            variables = [var.getValue() for _, var in self.localVars.items()]
            varsStr = ''.join([str(v) for v in variables])
            if len(self.scDict) == 0:
                # 由于存在unbounded变量,无法提前判断所有的变量组合的enabled commands
                # 因此需要手工判断
                enabledCommands = []
                for _,module in self.modules.items():
                    for _,comm in module.allCommands().items():
                        if (comm.guard(self.localVars, self.constants)):
                            enabledCommands.append(comm)
            else:
                enabledCommands = self.scDict[varsStr]
            if len(enabledCommands) == 0:
                break
            transition, holdingTime, rate, biasingRate, exitRate, biasingExitRate = self.nextState(
                enabledCommands, duration=duration - timeSum)
            timeSum += holdingTime
            if len(path) == 0 and holdingTime > duration:
                # The first transition is not possible to happen within the given duration
                # In this situation, we think that the transition not made.
                # return the path: [Step(initState, emptyTransition)]
                # self._updateCurAndPrevState()
                step = Step(
                    self.prevState.stateId,
                    self.prevState.apSet.copy(),
                    0.0,
                    0.0,
                    "empty transition",
                    rate,
                    biasingRate,
                    exitRate,
                    biasingExitRate)
                path.append(step)
                self.restoreSystem()
                return (None, path)
            if timeSum > duration:
                holdingTime -= (timeSum - duration)
            step = Step(
                self.prevState.stateId,
                self.prevState.apSet.copy(),
                holdingTime,
                passedTime,
                transition,
                rate,
                biasingRate,
                exitRate,
                biasingExitRate)
            path.append(step)
            passedTime += holdingTime
            if len(strPath):
                strPath += ','
            strPath += step.asKey()

            if len(path) >= 1 and self.stopCondition and self.stopCondition(
                    self.localVars, self.constants):
                # add this empty step (with no transition made)
                # to represent the state the system currently is in.
                self._updateCurAndPrevState()
                step = Step(
                    self.curState.stateId,
                    self.curState.apSet.copy(),
                    0,
                    passedTime,
                    "No transition",
                    1,
                    1,
                    1,
                    1)
                path.append(step)
                self.restoreSystem()
                return (None, path)

        # MUST be executed before the function returns
        # to prepare generating next random path.
        self.restoreSystem()

        return None, path

    def getCurrentState(self):
        return self.curState

    def getModelInitState(self):
        return State(0, self.initLocalVars, self)

    def restoreVars(self):
        for k, v in self.initLocalVars.items():
            self.localVars[k].setValue(v.getValue())

    def restoreStates(self):
        self._stateId = 0
        self.curState.stateId = 0
        self.prevState.stateId = 0
        self.curState.clearAPSet()
        self.prevState.clearAPSet()
        self.stateInited = False

    def restoreSystem(self):
        self.restoreVars()
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
        #     # Since the last step generated by self.genRandomPath() is an empty Step
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
            enabledCommands = list()
            for _, module in self.modules.items():
                for _, command in module.commands.items():
                    if command.evalGuard():
                        # make a copy of Command instance
                        # in failure biasing situation when command's rate
                        # needs to be modified.
                        enabledCommands.append(copy.copy(command))
            varTuple = tuple([item[1].getValue() for item in self.localVars.items()])
            varsStr = ''.join([str(v) for v in varTuple])
            self.scDict[varsStr] = enabledCommands
        logger.info(str(self.scDict.keys()))
        self.restoreSystem()

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

