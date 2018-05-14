# -*- coding:utf-8 -*-
from compiler.PRISMParser import ModelConstructor
from module.ModulesFile import StepGenThd
from module.ModulesFile import ModulesFile
from test.testCheckingAlgo import *
from module.Module import Constant
import itertools
from nn.NNRegressor import BPNeuralNetwork as BPNN
from util.CsvFileHelper import parse_csv
from util.PlotHelper import plot_multi
from util.AnnotationHelper import deprecated
import sys
import getopt
try:
    import cPickle as pickle
except ImportError:
    import pickle


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
        self.test_xs = []  # [(vals)]

    def set_manager_param(self, name, param):
        self.manager_params[name] = param

    def get_manager_param(self, name):
        return self.manager_params[name]

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
            return ltl
        else:
            return

    def _set_param(self, *constants):
        '''
        将参数设置到parser中
        :param constants: [constant_obj]
        :return: None
        '''
        for constant_obj in constants:
            self.mdl_parser.parser.vcf_map[constant_obj.get_name()].set_value(
                constant_obj.get_value())

    def _clear_param(self, *constants):
        for constant_obj in constants:
            self.mdl_parser.parser.vcf_map[constant_obj.get_name()].set_value(None)

    def set_test_xs(self, test_xs):
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

    def train_network(self):
        '''给定参数，先在checker中跑，得到训练参数上的ltl公式验证结果(train_y)，然后用这些数据对神经网络进行训练'''
        train_data_x = []
        train_data_y = []
        constant_objs = self._to_constant_objs()
        for constant_list in itertools.product(*constant_objs):
            self._set_param(*constant_list)
            self.model.prepare_commands()
            train_y = self.checker.run_checker()
            train_x = [c_obj.get_value() for c_obj in constant_list]
            train_data_x.append(train_x)
            train_data_y.append(train_y)

            self._clear_param(*constant_list)

        self.regressor.setup(len(self.expr_params),
                             self.get_manager_param("nh"),
                             self.get_manager_param("no"))
        print train_data_x
        print train_data_y
        self.regressor.train(train_data_x, train_data_y)

        network_obj = self.regressor
        dump_file = "nn.txt"
        f = open(dump_file, "wb")
        pickle.dump(network_obj, f)
        f.close()


    def run_test(self, prism_data=None):
        '''对给定测试参数运行神经网络进行预测'''
        # try loading dumped network
        f = open("nn.txt", "rb")
        network_obj = pickle.load(f)
        if network_obj:
            self.regressor = network_obj
        f.close()

        test_xs = self.test_xs  # [(vals)]
        test_expr_ys = []
        for test_x in test_xs:
            results = self.regressor.predict(list(test_x))
            # results is of length 1
            test_expr_ys.append(results[0])
        print "test_expr_x: {}".format(str(test_xs))
        print "test_expr_y: {}".format(str(test_expr_ys))

        # get true value returned from PRISM
        if prism_data:
            _, test_prism_ys = parse_csv(prism_data)
            plot_multi((test_xs, test_expr_ys, "experiment"), (test_xs, test_prism_ys, "prism"))
        else:
            plot_multi((test_xs, test_expr_ys, "experiment"))

    def unsure_param_names(self):
        return self.mdl_parser.parser.constname_unsure()


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
