# -*- coding:utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)
from collections import OrderedDict
import copy
from util.AnnotationHelper import *

# class represents a DTMC/CTMC module in PRISM

class Module(object):
    # name: module name
    def __init__(self, name):
        self.name = name
        self.commands = defaultdict(list)
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
        self.commands[command.name].append(command)
        command.module = self

    def get_commands_with_name(self, name):
        ''':return a list contains commands with same name'''
        if name not in self.commands.keys():
            return
        return self.commands[name]

    def allCommands(self):
        return self.commands

    # a value is not needed when executing an do_expe over this constant
    # constant is no longer a primitive value, but a Constant typed instance
    def addConstant(self, constant):
        self.constants[constant.get_name()] = constant

    def getConstant(self, name):
        if name in self.constants.keys():
            return self.constants[name]
        return None

    # exist for now in the case of do_expe
    def setConstant(self, constant):
        name = constant.get_name()
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

class Commands(object):

    @staticmethod
    def none_command():
        return Command()


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
            # [func(vs, cs)]
            guards = list(),
            action = None,
            module = None,
            prob = None,
            kind=None,
            biasing_rate=None):
        self.name = name
        self.guards = list()
        if isinstance(guards, list):
            self.guards.extend(guards)
        else:
            self.guards.append(guards)
        # change action type from function to dict
        # e.g. {var_name : var_new_value_func}
        self.action = action
        self.prob = prob
        self.module = module
        self.kind = kind
        # biasing rate(probability of DTMC actually)
        # by failure biasing methods, such as SFB, BFB, ...
        # failure biasing doesn't change rate, it only changes
        # probability of the embedded DTMC
        self.biasing_rate = biasing_rate
        # print "Guard is None ? : " + str(self.guard is None)

    def evaluate(self):
        result = True
        for guard in self.guards:
            result = guard(self.vs, self.cs)
            if not result:
                return False
        return result

    def execute(self):
        for var, update_func in self.action.items():
            var.value = update_func()

    def __str__(self):
        return 'comm %s of module %s' % (self.name, self.module.name)

    def __repr__(self):
        return "cmd {} of module {}".format(self.name, self.module.name)

    def add_guards(self, guards):
        assert isinstance(guards, list)
        self.guards.extend(guards)

    def get_guards(self):
        return self.guards

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
        self.init_val = initVal
        self.bounded = bounded
        self.range = valRange
        self.type = valType
        self.value = initVal

    # check if value is within the domain
    # (bounded or unbounded) of the variable
    def validate(self, value):
        if self.bounded:
            return value in self.range
        else:
            return isinstance(value, self.type)

    # __cmp__用于使用sort函数进行排序时调用
    def __cmp__(self, v):
        if isinstance(v, Variable) and self.type == v.type:
            return self.value.__cmp__(v.value)
        elif isinstance(v, self.type):
            return self.value.__cmp__(v)

    def __str__(self):
        return "(Variable {} : {})".format(self.name, self.get_value())

    def set_value(self, v):
        if isinstance(v, self.type):
            self.value = v
        else:
            self.value = v.get_value()

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name

    # return list of Variable instance with all possible values
    def allVarsList(self):
        if not self.bounded:
            return TypeError("Variable is not bounded")

        l = list()
        for val in self.range:
            cp = copy.copy(self)
            cp.value = val
            l.append(cp)
        return l

    def incr(self):
        self.value += 1

    def __iadd__(self, other):
        if isinstance(other, Variable) and self.type == other.type:
            self.value += other.value
        elif isinstance(other, self.type):
            self.value += other
        return self

    def __eq__(self, other):
        if type(self) == type(other) and self.type == other.valType:
            return self.value == other.value
        elif type(other) == self.type:
            return self.value == other
        else:
            raise Exception('type error in Variable.__eq__()')

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if type(self) == type(other) and self.type == other.valType:
            return self.value < other.value
        elif self.type == type(other):
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
        return "constant {0}: {1}".format(self.get_name(), self.value)

    def __repr__(self):
        return self.__str__()

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def set_value(self, value):
        if isinstance(value, Constant) and self.name == value.name:
            self.value = value.value
        else:
            self.value = value

    def update(self, constant):
        if self.get_name() == constant.get_name():
            self.value = constant.get_value()

    def __mul__(self, other):
        if isinstance(other, Constant):
            return self.value * other.get_value()
        elif isinstance(other,(int, float)):
            return self.value * other
        else:
            raise Exception("type error in Constant.__mul__")

    def __add__(self, other):
        if isinstance(other, Constant):
            return self.value + other.get_value()
        elif isinstance(other, (int, float)):
            return self.value + other
        else:
            raise Exception("type error in Constant.__mul__")

    def __sub__(self, other):
        if isinstance(other, Constant):
            return self.value - other.get_value()
        elif isinstance(other, (int, float)):
            return self.value - other
        else:
            raise Exception("type error in Constant.__mul__")

    def __div__(self, other):
        if isinstance(other, Constant):
            return self.value / other.get_value()
        elif isinstance(other, (int, float)):
            return self.value / other
        else:
            raise Exception("type error in Constant.__mul__")

    def __neg__(self):
        return Constant(self.get_name(), -1 * self.get_value())

    def __lt__(self, other):
        if isinstance(other, Constant):
            return self.get_value() < other.get_value()
        elif isinstance(other, type(self.get_value())):
            return self.get_value() < other
        else:
            raise Exception('type error in Constant.__lt__: {0}'.format(type(other)))

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.get_value() == other.get_value()
        elif isinstance(other, type(self.get_value())):
            return self.get_value() == other
        else:
            raise Exception('type error in Constant.__eq__: {0}'.format(type(other)))

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)


