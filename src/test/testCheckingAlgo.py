# -*- coding:utf-8 -*-
from model.ModelFactory import ModelFactory
from checker.Checker import Checker
from util.CsvFileHelper import parse_csv_cols
from math import fabs


DURATION = 5
c = 0.6
d = 0.02


def get_prism_checking_result(filepath):
    return parse_csv_cols(filepath)


def get_checker(model):
    # built = ModelFactory.get_built()
    ltl = ["U[1, {}]".format(int(DURATION)), "T", "failure"]
    checker = Checker(model=model, ltl=ltl, duration=DURATION, c=c, d=d)
    return checker


def t1(model):
    '''测试生成的随机路径要么长度达到最长(duration)，要么包含failure ap'''
    checker = get_checker(model)
    checker.model.duration = DURATION
    PATH_CNT = 3000
    # logger = get_logger()
    # logger.setLevel(logging.INFO)
    for _ in range(PATH_CNT):
        result, path = checker.gen_random_path()
        if len(path) < DURATION:
            pass
            # logger.info("Failed path found.")
        verified = checker.verify(path)
        if verified is False and len(path) != DURATION:
            # pass
            print "path:{}".format(str(path))
            print "path'len={}".format(len(path))


def t2(model=None):
    '''测试built模型运行checker的结果与PRISM中运行的一致'''
    prism_result_x, prism_result_y = get_prism_checking_result()  # (1, 5, 1)
    checker = get_checker(ModelFactory.get_built())
    samplesize = checker.get_sample_size()
    thickness = range(1, 6)
    probs = []
    # logger = get_logger()
    for t in thickness:
        ModelFactory.setParam("SCREEN_THICKNESS", t)
        checker.model.prepare_commands()
        probs.append(checker.run_checker())
    # logger.info("samples={},c={},d={}".format(samplesize, c, d))
    # logger.info(probs)
    for v1, v2 in zip(probs, prism_result_y[-(len(probs)):]):
        pass
        # logger.info("diff={}".format(fabs(v1 - v2)))


def set_param(name, value):
    '''用于对parsed model进行参数设置'''
    ModelFactory.model_constructor.parser.vcf_map[name].value = value


def t3(model, set_param_func, prism_data_file):
    '''测试parsed模型运行checker的结果与PRISM中运行的一致'''
    # logger = get_logger()3
    prism_result_x, prism_result_y = get_prism_checking_result(prism_data_file)
    checker = get_checker(model)
    samplesize = checker.get_sample_size()
    # logger.info("Sampling size = {}".format(samplesize))
    thickness = range(1, 11)
    probs = []
    for t in thickness:
        set_param_func("SCREEN_THICKNESS", t)
        checker.model.prepare_commands()
        probs.append(checker.run_checker())
    # logger.info("samples={},c={},d={}".format(samplesize, c, d))
    # logger.info(probs)
    for v1, v2 in zip(probs, prism_result_y[:len(probs)]):
        print "Diff = %.2f%%" % fabs((v1 - v2) / v2 * 100)


if __name__ == "__main__":
    # pass
    # t1()
    t2()
    # model_path = get_prism_model_dir() + get_sep() + "Queue.prism"
    # model_constructor = ModelConstructor()
    # model = model_constructor.parseModelFile(model_path)
    # model.prepare_commands()
    # ltl = LTLParser().build_parser().parse_line("true U<=5 failure")
    # checker = Checker(model, ltl, duration=5, c=0.5, d=0.01)
    # checker.samples = 6000
    # print checker.run_checker()
    # for _ in range(5000):
    #     _, path = checker.gen_random_path()
    #     last_step = path[-1]
    #     if (last_step.next_move.passed_time + last_step.next_move.holding_time) < DURATION and set(
    #             ["failure"]) not in last_step.ap_set.union(*[step.ap_set for step in path[:-1]]):
    #         print path
