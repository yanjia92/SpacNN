# -*- coding:utf-8 -*-
from model.ModelFactory import ModelFactory
from experiment.ExperimentWrapper import ExperimentWrapper
from checker.Checker import Checker
from module.Module import Constant
from nn.NNRegressor import BPNeuralNetwork as BPNN
from util.PlotHelper import plot_multi
from PathHelper import get_prism_model_dir, get_sep, get_log_dir
import logging

logger = logging.getLogger("test parsed regressor log")
logger.addHandler(logging.FileHandler(get_log_dir() + get_sep() + "testparsedregre.log", "w"))
logger.setLevel(logging.INFO)


def get_expr_result_prism():
    '''
    获取prism中进行experiment的数据
    返回：test_x, test_y
    '''
    filename = "YEAR1_T_1_5_1"
    x = []
    y = []
    with open(get_prism_model_dir() + get_sep() + filename, "r") as f:
        is_line1 = True
        for l in f:
            if is_line1:
                is_line1 = False
                continue
            values = map(lambda token: float(token.strip()), l.split(','))
            x.append(values[0])
            y.append(values[1])
    return (x, y)


TIME_LIMIT_IN_DAYS = 365
ltl = ["U[1, {}]".format(int(TIME_LIMIT_IN_DAYS * 2)), "T", "failure"]
TEST_DATA_X, TEST_DATA_Y = get_expr_result_prism()
thickness_cnsts = map(lambda v: Constant("SCREEN_THICKNESS", v), TEST_DATA_X)
<<<<<<< HEAD
samples_per_param = 100
=======
SAMPLES_PER_PARAM = 400
>>>>>>> 254cfcda20350d247a16857bd3a6d203e67e3872


def do_expr_built():
    model = ModelFactory.get_built()
    checker = Checker(model=model, ltl=ltl, duration=TIME_LIMIT_IN_DAYS*2)
    # wrapper = ExperimentWrapper(checker, samples_per_param=SAMPLES_PER_PARAM)
    wrapper = ExperimentWrapper(checker)
    wrapper.setconstants([thickness_cnsts,])
    logger.info("Built model expr began.")
    result = wrapper.do_expe()
    logger.info("Built model expr end.")
    return result


def do_expr_parsed():
    model = ModelFactory.get_parsed()
    checker = Checker(model=model, ltl=ltl, duration=TIME_LIMIT_IN_DAYS*2)
    # wrapper = ExperimentWrapper(checker, samples_per_param=SAMPLES_PER_PARAM)
    wrapper = ExperimentWrapper(checker)
    wrapper.setconstants([thickness_cnsts,])
    logger.info("Parsed model expr began.")
    result = wrapper.do_expe()
    logger.info("Parsed model expr end.")
    return result


def get_network(tx, ty):
    '''根据train data获取已经训练好的神经网络实例'''
    network = BPNN()
    network.setup(1, 5, 1)
    network.train(tx, ty)
    return network


def test():
    '''生成built and parsed model
       对两个模型进行回归分析，拟合出曲线，绘制在同一幅图中
       并在同一幅图中绘制出真实的由model checker绘制出的曲线,并返回误差'''
    result1 = do_expr_built()
    tx1 = []
    ty1 = []
    for x,y in result1:
        tx1.append(x)
        ty1.append(y)
    network1 = get_network(tx1, ty1)
    pred_y1 = map(lambda test_x: network1.predict(test_x), TEST_DATA_X)

    result2 = do_expr_parsed()
    tx2 = []
    ty2 = []
    for x,y in result2:
        tx2.append(x)
        ty2.append(y)
    network2 = get_network(tx2, ty2)
    pred_y2 = map(lambda test_x: network2.predict(test_x), TEST_DATA_X)

    logger.info("built")
    logger.info("x={}".format(TEST_DATA_X))
    logger.info("y={}".format(pred_y1))
    logger.info("parsed")
    logger.info("y={}".format(pred_y2))
    logger.info("prism")
    logger.info("y={}".format(TEST_DATA_Y))

    line_datas = [
        (TEST_DATA_X, pred_y1, "built"),
        (TEST_DATA_X, pred_y2, "parsed"),
        (TEST_DATA_X, TEST_DATA_Y, "prism")
    ]

    plot_multi(*line_datas)


if __name__ == "__main__":
    test()

