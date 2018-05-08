# -*- coding:utf-8 -*-
from checker.Checker import Checker
from compiler.PRISMParser import ModelConstructor
from module.ModulesFile import StepGenThrd
from PathHelper import *
import time
from module.ModulesFile import ModulesFile
from model.ModelFactory import ModelFactory
import logging
import sys
import random

def get_logger(level=logging.INFO):
    logger = logging.getLogger("Manager log")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(level)
    return logger

class Manager(object):
    def __init__(self):
        self.mdl_parser = ModelConstructor()
        self.model = None

    def _setup_model(self, duration=None, stop_condition=None):
        self.model.duration = duration
        self.model.init_queue()
        self.model.stopCondition = stop_condition

    def set_model(self, model):
        self.model = model
        self.model.init_queue()

    def input_file(self, file_path):
        # self.file_path = file_path # async
        self.model = self.mdl_parser.parseModelFile(file_path)
        self._setup_model(duration=ModulesFile.DEFAULT_DURATION)
        self.model.prepare_commands() # todo change prepare_commands to async call
        self.async_gen_steps()

    def async_gen_steps(self):
        thrd = StepGenThrd(model=self.model)
        # thrd.setDaemon(True)
        thrd.start()


def main():
    logger = get_logger()
    manager = Manager()
    built_model = ModelFactory.get_built()
    built_model.duration = 730
    built_model.prepare_commands()
    manager.set_model(model=built_model)
    manager.async_gen_steps()
    # manager.input_file(get_prism_model_dir() + get_sep() + "smalltest.prism")
    time.sleep(random.random()) # 模拟用户操作
    path = manager.model.get_random_path_V2()
    logger.info("path's len={}".format(len(path)))



if __name__ == "__main__":
    main()