# -*- coding:utf-8 -*-
from collections import OrderedDict
from collections import defaultdict


class Module(object):
    '''
    class represents a DTMC/CTMC module in PRISM
    '''
    def __init__(self, name):
        self._name = name
        self._commands = defaultdict(list) # 默认使用list存储同名commands
        self._variables = OrderedDict()
        self._constants = dict()
        self._model = None

    def set_model(self, model):
        '''
        assoicate self with the model
        :param model: ModulesFile instance
        :return: None
        '''
        self._model = model

    def get_name(self):
        return self._name

    def add_variable(self, variable):
        '''
        add variable to this module
        :param variable: BoundedIntegerVariable instance
        :return: None
        '''
        self._variables[variable.get_name()] = variable

    def get_variable(self, key):
        '''
        get the variable instance for the key
        :param key: variable name
        :return: BoundedIntegerVariable instance
        '''
        if key in self._variables:
            return self._variables.get(key)
        raise Exception('variable {} not exist in module {}'.format(key, self._name))

    def get_variables(self):
        return self._variables

    def add_command(self, command):
        self._commands[command.get_name()].append(command)
        command.module = self

    def get_commands_with_name(self, name):
        ''':return a list contains commands with same name'''
        if name not in self._commands.keys():
            return
        return self._commands[name]

    def get_commands(self):
        return self._commands

    # a value is not needed when executing an do_expe over this constant
    # constant is no longer a primitive value, but a Constant typed instance
    def add_constant(self, constant):
        self._constants[constant.get_name()] = constant

    def getConstant(self, name):
        if name in self._constants.keys():
            return self._constants[name]
        raise Exception("Module {} does not contain constant {}".format(self._name, name))

    def get_constants(self):
        return self._constants

    def __str__(self):
        return "Module {}".format(self._name)


class Command(object):
    def __init__(
            self,
            name,
            guard,
            prob,
            update):
        '''
        Command constructor
        :param name: command name
        :param guard: function that returns bool
        :param update: {variable_instance: update_function}
        :param prob: float or function
        '''
        self._name = name
        self._guard = guard
        self._update = update
        self._prob = prob
        self._module = None
        self._vs = None  # variables map
        self._cs = None  # constants map
        self._hit_cnt = 0
        self._miss_cnt = 0

    def get_update(self):
        return self._update

    def get_guard(self):
        return self._guard

    def get_prob(self):
        return self._prob

    def set_prob(self, p):
        self._prob = p

    def get_name(self):
        return self._name

    def get_hit_cnt(self):
        return self._hit_cnt

    def get_miss_cnt(self):
        return self._miss_cnt

    def set_variables(self, vs):
        '''
        设置command执行evaluate, execute所需的variables
        :param vs: dict
        :return: None
        '''
        self._vs = vs

    def set_constants(self, cs):
        '''
        设置command执行evaluate, execute所需的constants
        :param cs: dict
        :return: None
        '''
        self._cs = cs

    def set_name(self, name):
        self._name = name

    def incr_hit_cnt(self):
        self._hit_cnt += 1

    def incr_miss_cnt(self):
        self._miss_cnt += 1

    def evaluate(self):
        if not callable(self._guard):
            raise Exception("Command's guard must be callable")
        return self._guard(self._vs, self._cs)

    def execute(self):
        for var, update_func in self._update.items():
            if not callable(update_func):
                raise Exception("Command's update's value must be callable")
            var.set_value(update_func())

    def __str__(self):
        if self._module is not None:
            return 'Command {} of module {}'.format(self._name, self._module.get_name())
        return 'Command {}'.format(self._name)

    def __repr__(self):
        return self.__str__()

    def add_guards(self, *guards):
        '''
        adds guards
        :param guards: list of functions
        :return:
        '''
        self._guards.extend(guards)

    def add_actions(self, actions):
        if isinstance(actions, dict):
            self._updates.update(actions)


class TypeVariable(object):
    def __init__(self, n, v, t):
        '''
        constructor
        :param n: name
        :param v: value of the variable, could be None, primitive value or function that return a value
        :param t: type of the value int, float or bool
        '''
        self._name = n
        self._init_value = v
        self._value = v
        self._type = t

    def set_value(self, v):
        '''
        value setter method
        :param v: could be int, float or function
        :return: None
        '''
        self._value = v

    def get_value(self):
        if not callable(self._type):
            raise Exception("Variable type must be callable")
        if callable(self._value):
            return self._type(self._value())
        else:
            return self._type(self._value)

    def get_init(self):
        ans = self._init_value
        if callable(ans):
            ans = ans()
        return ans

    def get_name(self):
        return self._name

    def __str__(self):
        return "(TypeVariable {} : {})".format(self._name, self._value)


class BoundedIntegerVariable(TypeVariable):
    def __init__(self, n, v, r):
        '''
        constructor
        :param n: name
        :param v: value, could be function
        :param r: range(inclusive), a tuple of type (min, max), min, max could be None, value or function
        '''
        TypeVariable.__init__(self, n, v, int)
        self._min_value = r[0]
        self._max_value = r[1]

    def get_min(self):
        ans = self._min_value
        if callable(ans):
            ans = ans()
        return ans

    def get_max(self):
        ans = self._max_value
        if callable(ans):
            ans = ans()
        return ans

    def possible_values(self):
        '''
        返回该变量所有可能的取值
        :return: list of type [(name, value)]
        '''
        min_value = self._min_value
        if callable(min_value):
            min_value = min_value()
        max_value = self._max_value
        if callable(max_value):
            max_value = max_value()
        if min_value > max_value:
            raise Exception("Invalid Variable range parameter: ({}, {})".format(min_value, max_value))
        return [tuple([self._name, value]) for value in range(min_value, max_value+1)]


class Constant(TypeVariable):

    def __str__(self):
        return "Constant {0}: {1}".format(self.get_name(), self.get_value())