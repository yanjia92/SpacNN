# -*- coding:utf-8 -*-
import getopt
import itertools
import sys

from module.Module import Constant
from nn.NNRegressor import BPNeuralNetwork as BPNN
from test.testCheckingAlgo import *
from util.PlotHelper import plot_multi
import os
from module.ModulesFile import ModelType

try:
    import cPickle as pickle
except ImportError:
    import pickle
from compiler.LTLParser import LTLParser


class Manager(object):

    def __init__(self):
        self.manager_params = {
            "隐藏层神经元个数": 5, 
            "输出层神经元个数": 1, 
            "训练样本取样数": 6000,
            "学习速率": 0.05,
            "矫正率": 0.1
        }

        self._params_map = {
            "nh": "隐藏层神经元个数",
            "no": "输出层神经元个数",
            "samples": "训练样本取样数",
            "learning_rate": "学习速率",
            "correct_rate": "矫正率"
        }
        self.mdl_parser = ModelConstructor()
        self.model = None
        self.expr_params = list()  # [(name, val_list)]
        self.ltl = None
        self.checker = None
        self.regressor = BPNN()
        self.test_xs = []  # [(vals)]
        self.ltl_parser = LTLParser().build_parser()
        self.predict_xs = None
        self.predict_ys = None

    def set_manager_param(self, name, param):
        self.manager_params[name] = param

    def set_manager_param_simple(self, name, value):
        if name not in self._params_map.keys():
            # todo system-level logger
            pass
        self.manager_params[self._params_map[name]] = value

    def get_manager_param(self, name):
        if name not in self._params_map.keys():
            print "key not exist when get manager parameter: {}".format(name)
        return self.manager_params[self._params_map[name]]

    def set_random_path_duration(self, duration):
        self.set_manager_param("duration", duration)
        self.model.duration = duration

    def read_model_file(self, file_path):
        self.model = self.mdl_parser.parseModelFile(file_path)
        self.checker = Checker(model=self.model)

    def _set_constants(self, *constants):
        '''constants: ([constant_obj])'''
        while len(self.expr_params):
            self.expr_params.pop(0)
        self.expr_params.extend(constants)

    def set_train_constants(self, *constants):
        '''设置训练时需要的参数
        constant: (name, val_list)
        '''
        self.expr_params = constants

    def set_ltl(self, ltl):
        if self.checker:
            self.checker.ltl = ltl
            return ltl
        else:
            return

    def set_model_duration(self, duration):
        '''duration: str_valued duration'''
        if self.model.model_type == ModelType.DTMC:
            self.model.duration = int(duration)
        else:
            # CTMC case
            self.model.duration = float(duration)

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
        :param test_xs: [(param1_value, param2_val, ...)]
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
        self.checker.samples = self.get_manager_param("samples")
        for constant_list in itertools.product(*constant_objs):
            try:
                self._set_param(*constant_list)
                self.model.prepare_commands()
                train_y = self.checker.run_checker()
                train_x = [c_obj.get_value() for c_obj in constant_list]
                train_data_x.append(train_x)
                train_data_y.append(train_y)
            finally:
                self._clear_param(*constant_list)

        self.regressor.setup(len(self.expr_params),
                             int(self.get_manager_param("nh")),
                             int(self.get_manager_param("no")),
                             self.get_manager_param("learning_rate"),
                             self.get_manager_param("correct_rate"))

        print train_data_x
        print train_data_y
        self.regressor.train(train_data_x, train_data_y)

        # dump the network
        network_obj = self.regressor
        dump_file = "nn.txt"
        try:
            f = open(dump_file, "wb")
            pickle.dump(network_obj, f)
            f.close()
        except IOError:
            print "IOError when dumping network object. Please check your access permission"

    def compute_error(self, err_func, values1, values2):
        # param of red_func: val1, val2)计算val1和val2之间的误差，并将所有的误差相加
        errors = sum(map(err_func, [t for t in zip(values1, values2)])) 
        return errors

    def run_test(self):
        '''对给定测试参数运行神经网络进行预测'''
        # try loading dumped network

        if os.path.exists("nn.txt") and os.access("nn.txt", os.R_OK):
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
        print "Predict results: "
        for (x, y) in zip(test_xs, test_expr_ys):
            print "x={}, predict={}".format(x, y)
        return test_expr_ys

    def unsure_param_names(self):
        return self.mdl_parser.parser.constname_unsure()

    def plot_expr_datas(self, expr_xs, expr_ys, true_ys=None):
        if true_ys:
            plot_multi((expr_xs, expr_ys, "predict"), (expr_xs, true_ys, "prism"))
        else:
            param = (expr_xs, expr_ys, "predict")
            plot_multi(param)

    def save_predict_results(self, xs, ys):
        assert len(ys) == len(xs)
        self.predict_xs = xs
        self.predict_ys = ys


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
