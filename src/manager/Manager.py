# -*- coding:utf-8 -*-
from compiler.PRISMParser import ModelConstructor
from module.ModulesFile import StepGenThd
from module.ModulesFile import ModulesFile
from test.testCheckingAlgo import *
from module.Module import Constant
import itertools
from nn.NNRegressor import BPNeuralNetwork as BPNN
from util.CsvFileHelper import parse_csv
# from util.PlotHelper import plot_multi
from util.AnnotationHelper import deprecated
import sys
import getopt


# def get_logger(level=logging.INFO):
#     logger = logging.getLogger("Manager log")
#     logger.addHandler(logging.StreamHandler(sys.stdout))
#     logger.setLevel(level)
#     return logger


class Manager(object):
    def __init__(self):
        self.manager_params = {"nh": 5, "no": 1}
        self.mdl_parser = ModelConstructor()
        self.model = None
        self.expr_params = list()  # [(name, val_list)]
        self.ltl = None
        self.checker = None
        self.regressor = BPNN()
        self.test_xs = []  # [(name, val_list)]

    def set_manager_param(self, name, param):
        self.manager_params[name] = param

    def get_manager_param(self, name):
        return self.expr_params[name]

    def set_random_path_duration(self, duration):
        self.set_manager_param("duration", duration)
        self.model.duration = duration

    def _setup_model(self, duration=None):
        self.model.duration = duration

    @deprecated
    def set_model(self, model):
        self.model = model

    def read_model_file(self, file_path):
        self.model = self.mdl_parser.parseModelFile(file_path)
        self._setup_model(duration=ModulesFile.DEFAULT_DURATION)
        self.checker = Checker(model=self.model)

    @deprecated
    def async_gen_steps(self):
        thd = StepGenThd(model=self.model)
        thd.setDaemon(True)
        thd.start()

    def _set_constants(self, *constants):
        '''constants: ([constant_obj])'''
        while len(self.expr_params):
            self.expr_params.pop(0)
        self.expr_params.extend(constants)

    def set_train_constants(self, *constants):
        '''设置训练时需要的参数
        constant: [(name, val_list)]
        '''
        # const_objs = []
        # for name, val_list in constants:
        #     constants_temp = []
        #     for val in val_list:
        #         constants_temp.append(Constant(name, val))
        #     const_objs.append(constants_temp)
        # self._set_constants(*const_objs)
        self.expr_params = constants

    def set_ltl(self, ltl):
        if self.checker:
            self.checker.ltl = ltl

    def _set_param(self, *constants):
        '''
        将参数设置到parser中
        :param constants: [constant_obj]
        :return: None
        '''
        for constant_obj in constants:
            self.mdl_parser.parser.vcf_map[constant_obj.get_name()].set_value(constant_obj.get_value())

    def set_test_x(self, test_xs):
        '''
        设置回归分析时参数的值
        :param test_xs: [(vals)]
        :return: None
        '''
        self.test_xs = test_xs

    def _to_constant_objs(self):
        '''
        将self.expr_params转化为[[constant_obj]]
        :return: [[constant_obj]]
        '''
        result = []
        for n, vl in self.expr_params:
            objs = []
            for v in vl:
                objs.append(Constant(n, v))
            result.append(objs)
        return result

    def do_regression(self):
        # get constants and set it to the vcf_map
        # prepare commands
        # do_expr and return train data (x, y)
        # train the BP network
        # get_test_x
        # compute the y in terms of test_x
        # paint
        train_data_x = []
        train_data_y = []
        if len(self.expr_params) == 0:
            pass  # todo suggest user to set the parameter to run the regressor
        constant_objs = self._to_constant_objs()
        for constant_list in itertools.product(*constant_objs):
            self._set_param(*constant_list)
            self.model.prepare_commands()
            train_y = self.checker.run_checker()
            train_x = [c_obj.get_value() for c_obj in constant_list]
            train_data_x.append(train_x)
            train_data_y.append(train_y)

        self.regressor.setup(len(self.expr_params), self.get_manager_param("nh"), self.get_manager_param("no"))
        self.regressor.train(train_data_x, train_data_y)

        test_xs = self.test_xs  # [(vals)]
        test_expr_ys = []
        for test_x in test_xs:
            results = self.regressor.predict(list(test_x))
            # results is of length 1
            test_expr_ys.append(results[0])

        # get true value returned from PRISM
        _, test_prism_ys = parse_csv("YEAR1_T_1_10_1")

        # plot_multi((test_xs, test_expr_ys, "experiment"), (test_xs, test_prism_ys, "prism"))


def main():
    def set_param_func(name, value):
        manager.mdl_parser.parser.vcf_map[name].value = value

    manager = Manager()
    short_opts = "h"
    long_opts = ["prism_data=", "model_file="]
    opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    prism_data = None
    for opt, value in opts:
        if opt == "--model_file":
            manager.read_model_file(value)
        if opt == "--prism_data":
            prism_data = value
    if prism_data:
        t3(manager.model, set_param_func, prism_data)


if __name__ == "__main__":
    main()
