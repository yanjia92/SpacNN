# -*- coding:utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)
from collections import OrderedDict
import copy

# class represents a DTMC/CTMC module in PRISM

class Module(object):
    # name: module name
    def __init__(self, name):
        self.name = name
        # TODO change to commName and comms implemention because commands may
        # have same name
        self.commands = OrderedDict()
        self.variables = OrderedDict()
        self.constants = dict()
        self.modulesFile = None

    def addVariable(self, variable):
        self.variables[variable.name] = variable
        variable.module = self

    def removeVariable(self, varname):
        if not self.variables and varname not in self.variables.keys():
            return
        self.variables.pop(varname)

    def addCommand(self, command):
        self.commands[command.name] = command
        command.module = self

    def removeCommand(self, name):
        if not self.commands.has_key(name):
            # todo throws null pointer exception
            return
        return self.commands.pop(name)

    def getCommand(self, name):
        if name not in self.commands.keys():
            # todo throws null pointer exception
            return
        return self.commands.get(name)

    def allCommands(self):
        # return a OrderedDict with the command name as key and command as value
        return self.commands

    # a value is not needed when executing an do_expe over this constant
    # constant is no longer a primitive value, but a Constant typed instance
    def addConstant(self, constant):
        self.constants[constant.getName()] = constant

    def getConstant(self, name):
        if name in self.constants.keys():
            return self.constants[name]
        return None

    # exist for now in the case of do_expe
    def setConstant(self, constant):
        name = constant.getName()
        if name in self.constants.keys():
            v = self.constants[name]
            self.constants[name] = constant
            return v


    def getVariable(self, name):
        if name in self.variables:
            return self.variables[name]
        return None

    def __str__(self):
        return self.name


class CommandKind:
    FAILURE, REPAIR, NONE = range(3)


class Command(object):
    # name: name of the command
    # about guard and action in Command:
        # they are function objects both
        # they all take two dictionaries vs, cs(set of variables and constants)
        # as its parameter
    # module: Module instance which the command get attached to
    # kind: indicate the command is a failure/repair transition
    # according to the definition in p52-nakayama(1).pdf
    # is an instance of CommandKind
    # prob: represents probability/rate
    def __init__(
            self,
            name = "",
            guard = None,
            action = None,
            module = None,
            prob = None,
            kind=None,
            biasingRate=None):
        self.name = name
        self.guard = guard
        self.action = action
        self.prob = prob
        self.module = module
        self.kind = kind
        # biasing rate(probability of DTMC actually)
        # by failure biasing methods, such as SFB, BFB, ...
        # failure biasing doesn't change rate, it only changes
        # probability of the embedded DTMC
        self.biasingRate = biasingRate
        # print "Guard is None ? : " + str(self.guard is None)

    def evalGuard(self):
        return self.guard(self.vs, self.cs)
        # if 'cs' in dir(self) and 'vs' in dir(self):
        #     return self.guard(self.vs, self.cs)
        # else:
        #     logging.info('vs,cs not exist in Module %s' % self.module.name)

    def execAction(self):
        self.action(self.vs, self.cs)
        # if 'vs' in dir(self) and 'cs' in dir(self):
        #     self.action(self.vs, self.cs)
        # else:
        #     logging.info('vs,cs not exist in Module %s' % self.module.name)

    def __str__(self):
        return 'comm %s of module %s' % (self.name, self.module.name)

    def setGuard(self, guard):
        if not guard:
            # todo throws null pointer exception
            return
        self.guard = guard

    def setAction(self, action):
        if not action:
            # todo throws null pointer exception
            return
        self.action = action


class TypeError(object):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "TypeError: %s" % self.message


class Variable(object):
    def __init__(
            self,
            name='',
            initVal=None,
            valRange=None,
            valType=None,
            bounded=True):
        self.name = name
        self.initVal = initVal
        self.bounded = bounded
        self.valRange = valRange
        self.valType = valType
        self.value = initVal

    # check if value is within the domain
    # (bounded or unbounded) of the variable
    def validate(self, value):
        if self.bounded:
            return value in self.valRange
        else:
            return isinstance(value, self.valType)

    # __cmp__用于使用sort函数进行排序时调用
    def __cmp__(self, v):
        if isinstance(v, Variable) and self.valType == v.valType:
            return self.value.__cmp__(v.value)
        elif isinstance(v, self.valType):
            return self.value.__cmp__(v)

    def __str__(self):
        return "(Variable {} : {})".format(self.name, self.getValue())

    def setValue(self, v):
        if isinstance(v, self.valType):
            self.value = v
        elif isinstance(v, Variable) and self.valType == v.valType:
            self.value = v.value

    def getValue(self):
        return self.value

    def getName(self):
        return self.name

    # return list of Variable instance with all possible values
    def allVarsList(self):
        if not self.bounded:
            return TypeError("Variable is not bounded")

        l = list()
        for val in self.valRange:
            cp = copy.copy(self)
            cp.value = val
            l.append(cp)
        return l

    def __iadd__(self, other):
        if isinstance(other, Variable) and self.valType == other.valType:
            self.value += other.value
        elif isinstance(other, self.valType):
            self.value += other
        return self

    def __eq__(self, other):
        if type(self) == type(other) and self.valType == other.valType:
            return self.value == other.value
        elif type(other) == self.valType:
            return self.value == other
        else:
            raise Exception('type error in Variable.__eq__()')

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if type(self) == type(other) and self.valType == other.valType:
            return self.value < other.value
        elif self.valType == type(other):
            return self.value < other
        else:
            raise Exception('type error in Variable.__lt__()')

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)


class Constant(object):
    def __init__(self, name, constant=None):
        self.value = constant
        self.name = name

    def __str__(self):
        return "constant {0}: {1}".format(self.getName(), self.value)

    def __repr__(self):
        return self.__str__()

    def getName(self):
        return self.name

    def getValue(self):
        return self.value

    def update(self, constant):
        if self.getName() == constant.getName():
            self.value = constant.getValue()

    def __mul__(self, other):
        if isinstance(other, Constant):
            return self.value * other.getValue()
        elif isinstance(other,(int, float)):
            return self.value * other
        else:
            raise Exception("type error in Constant.__mul__")

    def __add__(self, other):
        if isinstance(other, Constant):
            return self.value + other.getValue()
        elif isinstance(other, (int, float)):
            return self.value + other
        else:
            raise Exception("type error in Constant.__mul__")

    def __sub__(self, other):
        if isinstance(other, Constant):
            return self.value - other.getValue()
        elif isinstance(other, (int, float)):
            return self.value - other
        else:
            raise Exception("type error in Constant.__mul__")

    def __div__(self, other):
        if isinstance(other, Constant):
            return self.value / other.getValue()
        elif isinstance(other, (int, float)):
            return self.value / other
        else:
            raise Exception("type error in Constant.__mul__")

    def __neg__(self):
        return Constant(self.getName(), -1 * self.getValue())

    def __lt__(self, other):
        if isinstance(other, Constant):
            return self.getValue() < other.getValue()
        elif isinstance(other, type(self.getValue())):
            return self.getValue() < other
        else:
            raise Exception('type error in Constant.__lt__: {0}'.format(type(other)))

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.getValue() == other.getValue()
        elif isinstance(other, type(self.getValue())):
            return self.getValue() == other
        else:
            raise Exception('type error in Constant.__eq__: {0}'.format(type(other)))

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)


