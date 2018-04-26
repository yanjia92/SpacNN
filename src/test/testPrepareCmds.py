# -*- coding: utf-8 -*-
import time
from model.ModelFactory import ModelFactory
from config.SPSConfig import SPSConfig
from model.ModuleFactory import ModuleFactory


def getParsedModel():
    return ModelFactory.get_parsed()


def getBuiltModel():
    return ModelFactory.get_built()


def timeit(func, *args, **kwargs):
    begin = time.time()
    func(*args, **kwargs)
    end = time.time()
    print "Running {} caused: {}".format(func.__name__, end-begin)


def test():
    # model = getBuiltModel()
    model = getParsedModel()
    timeit(model.prepareCommands)


if __name__ == '__main__':
    test()