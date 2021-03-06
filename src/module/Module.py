# -*- coding:utf-8 -*-
from collections import OrderedDict
from collections import defaultdict


class Module(object):
    '''
    class represents a DTMC/CTMC module in PRISM
    '''
    def __init__(self, name):
        self._name = name
        # the reason why use defaultdict to store the commands is
        # in ModulesFile commands with same name need to be joined
        self._commands = defaultdict(list)
        self._variables = OrderedDict()
        self._constants = dict()
        self._model = None

    def set_model(self, model):
        self._model = model

    def get_name(self):
        return self._name

    def add_variable(self, variable):
        self._variables[variable.get_name()] = variable

    def get_variable(self, key):
        if key in self._variables:
            return self._variables.get(key)
        raise Exception('variable {} not exist in module {}'.format(key, self._name))

    def get_variables(self):
        return self._variables

    def add_command(self, c):
        self._commands[c.get_name()].append(c)

    def get_commands(self):
        return self._commands

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
        self._mod_name = ""
        self._vs = None  # variables map
        self._cs = None  # constants map
        self._hit_cnt = 0 # when a path satisfy the LTL, each command in the path increments its _hit_cnt
        self._miss_cnt = 0 # when a path doesn't satisfy the LTL, each command in the path increments its _miss_cnt

    def incr_hit_cnt(self):
        self._hit_cnt += 1

    def incr_miss_cnt(self):
        self._miss_cnt += 1

    def evaluate(self):
        if not callable(self._guard):
            raise Exception("Command's guard must be callable")
        return self._guard(self._vs, self._cs)

    def execute(self):
        #  fix bug here
        #  can not update variables one by one
        #  must update all at one turn
        new_value_map = {}
        for var, update_func in self._update.items():
            if not callable(update_func):
                raise Exception("Command's update's value must be callable")
            new_value_map[var] = update_func()
        for var, value in new_value_map.items():
            var.set_value(value)

    def __str__(self):
        return "Comm {} of module {}".format(self._name, self._mod_name)

    def __repr__(self):
        return self.__str__()

    def set_mod_name(self, mod_name):
        if not isinstance(mod_name, str) or len(mod_name) <= 0:
            raise Exception("Invalid module name {}".format(mod_name))
        self._mod_name = mod_name

    def add_guards(self, *guards):
        '''
        adds guards
        :param guards: list of functions
        :return:
        '''
        self._guard.extend(guards)

    def add_actions(self, actions):
        if isinstance(actions, dict):
            self._update.update(actions)

    def get_update(self):
        return self._update

    def get_guard(self):
        return self._guard

    def get_prob(self):
        return self._prob

    def set_prob(self, p):
        self._prob = p

    def set_module(self, m):
        self._module = m

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

    def possible_values_cnt(self):
        '''
        返回该变量可能取值的个数
        :return: int
        '''
        _min = self.get_min()
        _max = self.get_max()
        return _max - _min + 1


class Constant(TypeVariable):

    def __str__(self):
        return "Constant {0}: {1}".format(self.get_name(), self.get_value())