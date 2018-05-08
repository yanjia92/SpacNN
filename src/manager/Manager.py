# -*- coding:utf-8 -*-
from compiler.PRISMParser import ModelConstructor
from module.ModulesFile import StepGenThd
import time
from module.ModulesFile import ModulesFile
import sys
from test.testCheckingAlgo import *


def get_logger(level=logging.INFO):
    logger = logging.getLogger("Manager log")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(level)
    return logger


class Manager(object):
    def __init__(self):
        self.mdl_parser = ModelConstructor()
        self.model = None

    def _setup_model(self, duration=None):
        self.model.duration = duration

    def set_model(self, model):
        self.model = model

    def input_file(self, file_path):
        self.model = self.mdl_parser.parseModelFile(file_path)
        self._setup_model(duration=ModulesFile.DEFAULT_DURATION)
        self.model.prepare_commands()  # todo change prepare_commands to async call

    def async_gen_steps(self):
        thd = StepGenThd(model=self.model)
        thd.setDaemon(True)
        thd.start()


def main():
    manager = Manager()
    manager.input_file(get_prism_model_dir() + get_sep() + "smalltest.prism")
    manager.async_gen_steps()
    time.sleep(random.random())  # 模拟用户操作
    # t1(manager.model)

    def set_param_func(name, value):
        manager.mdl_parser.parser.vcf_map[name].value = value

    t3(manager.model, set_param_func)


if __name__ == "__main__":
    main()
