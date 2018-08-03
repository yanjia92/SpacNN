# -*- coding: utf-8 -*-
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from compiler.PRISMParser import ModelConstructor


def load_quad_data(cnt=20):
    np.random.seed(3)
    x = np.random.uniform(-4, 4, size=cnt)
    print type(x)
    y = x ** 2 + sqrt(2) * np.random.randn(cnt)
    xs = np.reshape(x, [cnt, 1])  # [cnt, 1] 和 [cnt, ]的区别是前者每一行是一个向量，后者是标量
    ys = np.reshape(y, [cnt, ])
    return xs, ys


def quad_regress():
    '''
    Regression test using MLPRegressor
    :return: null
    '''
    xs, ys = load_quad_data(cnt=100)
    regressor = MLPRegressor(alpha=0.001, hidden_layer_sizes=(10, ), max_iter=50000,
                             activation="logistic", verbose='True', learning_rate="adaptive")
    regressor.fit(xs, ys)
    x_ = np.linspace(-4, 4, 160)
    pred_x = np.reshape(x_, [160, 1])
    pred_y = regressor.predict(pred_x)
    fig = plt.figure()
    plt.plot(x_, x_**2, color='b')
    plt.plot(pred_x, pred_y, color='r')
    plt.plot(xs, ys, 's')
    plt.show()


def dpm_regress():
    '''
    证明回归分析的结果和prism的误差和SMC和prism的误差相差不大，
    即证明回归分析可以代替SMC
    :return: null
    '''
    from PathHelper import get_prism_model_dir
    from checker.Checker import Checker
    from compiler.LTLParser import LTLParser
    from util.util import interval
    from experiment.ExperimentWrapper import ExperimentWrapper

    base_dir = get_prism_model_dir()
    model = ModelConstructor(base_dir).get_model("smalltest")
    ltl = "true U<=180 failure"
    ltl_parser = LTLParser().build_parser()
    parsed_ltl = ltl_parser.parse_line(ltl)
    checker = Checker(model, parsed_ltl, duration=180)

    expe_executor = ExperimentWrapper(checker, samples_per_param=600)
    train_xs = interval(1, 10, 0.3)


    # fit training data to regressor

    # predict new y value at test xs using regressor

    # compare the prediction result with checker's



if __name__ == "__main__":
    quad_regress()

