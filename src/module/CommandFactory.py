# -*- coding:utf-8 -*-
from module.Module import Command


class CommandFactory(object):

    @staticmethod
    def generate(name, guard, prob, updates):
        '''
        factory method
        :param name: command's name
        :param guards: list of function with each represent a unit boolean expression
        :param prob: a function which return the probability/rate that the updates occur
        :param updates: a dictionary of type Map<Variable_instance, func> with function of type func(vs, cs) to perform the update
        :return:
        '''
        return Command(name, guard, prob, updates)
