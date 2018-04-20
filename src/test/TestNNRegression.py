# -*- coding:utf-8 -*-
import logging
import matplotlib.pyplot as plt
from checker.Checker import Checker
from config import SPSConfig
from experiment.ExperimentWrapper import ExperimentWrapper
from model.ModelFactory import ModelFactory
from model.ModuleFactory import ModuleFactory
from nn.NNRegressor import BPNeuralNetwork

logger = logging.getLogger("TestNNTRegression logging")

# 文件日志
file_handler = logging.FileHandler("../log/nnregr.log")
# 为logger添加日志处理器
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)


def testrunexpe():
    from experiment.ExperimentWrapper import executepoissionexpe, executemodelchecking
    from util.util import interval
    from module.Module import Constant
    params = []
    for i in interval(0.5, 5, 0.1):
        params.append(Constant('r', i))
    result = executepoissionexpe([params]) # {paramsdict: prob}
    cases = map(lambda tuple: tuple[0], result)
    labels = map(lambda tuple: tuple[1], result)

    regressor = BPNeuralNetwork()
    regressor.setup(1, 5, 1)
    regressor.train(cases, labels)

    test_cases = map(lambda v: Constant('r', v), interval(0.5, 5, 0.05))
    test_labels = [regressor.predict(test_case) for test_case in test_cases]

    # 对多组参数进行模型验证
    mcresult = executemodelchecking([test_cases])
    # mc_labels = map(lambda tuple: tuple[1], mcresult)

    plt.plot(map(lambda const: const.getValue(), test_cases), test_labels, label='predict')
    # plt.plot(map(lambda const: const.getValue(), test_cases), mc_labels, label='mc')
    plt.show()

def testSPS():
    from util.util import interval
    from module.Module import Constant
    config = SPSConfig.SPSConfig()
    moduleFactory = ModuleFactory(config)
    modelfactory = ModelFactory(moduleFactory)
    model = modelfactory.spsmodel()
    ltl = ['U[1, {0}]'.format(730), 'T', 'failure'] # 一年之内系统失效
    checker = Checker(model, ltl, duration=730, fb=False)
    wrapper = ExperimentWrapper(checker, samples_per_param=100)
    trainx = interval(1, 10, 0.5)
    testx = interval(1, 10, 0.1)
    thickness_params = [Constant('SCREEN_THICKNESS', st) for st in trainx]
    wrapper.setconstants([thickness_params])
    result = wrapper.experiment()
    cases = map(lambda tuple: tuple[0], result)
    labels = map(lambda tuple: tuple[1], result)

    regressor = BPNeuralNetwork()
    regressor.setup(1, 5, 1)
    regressor.train(cases, labels)

    test_cases = map(lambda c: Constant('SCREEN_THICKNESS', c), testx)
    test_labels = [regressor.predict(test_case) for test_case in testx]
    # 对多组参数进行模型验证
    # logger.info("mc begin")
    #
    wrapper.setconstants([test_cases])
    # mcresult = wrapper.modelcheck()
    # mc_labels = map(lambda tuple: tuple[1], mcresult)

    plt.plot(testx, [i[0] for i in test_labels], label='predict')
    # plt.plot(map(lambda const: const.getValue(), test_cases), mc_labels, label='mc')
    plt.show()

def main():
    testSPS()

if __name__ == '__main__':
    main()
