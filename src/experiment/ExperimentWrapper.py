# -*- coding: utf-8 -*-
from itertools import product
import logging
import sys
from checker import Checker
from collections import OrderedDict
from model.ModelFactory import ModelFactory
from util.AnnotationHelper import deprecated

# logger = logging.getLogger("ExperimentWrapper logging")
# file_handler = logging.FileHandler("../log/expe.log", "w")
# logger.addHandler(file_handler)
# logger.setLevel(logging.INFO)

# 使用simulation的方法对模型进行experiment
# 为模型中的未定参数设定一组值,并进行simulation验证实验,返回多次simulation的期望值(平均值)


@deprecated
class ExperimentWrapper(object):
    def __init__(self, checker, params):
        '''
        :param checker:
        :param params: map contain unknown parameters: {param_name: value_list}
        '''
        self.checker = checker
        self.params = params

    # 根据wrapper设置的多组参数进行实验
    # 返回每组参数的验证结果
    # return: [(paramvalues, prob)]
    def do_expe(self):
        cnstnames = []
        cnstvalueslist = []
        for name, values in self._constants.items():
            cnstnames.append(name)
            cnstvalueslist.append(values)

        results = []  # 记录每组参数值的性质验证结果
        for params in product(*cnstvalueslist):
            paramsdict = OrderedDict()
            for name, value in zip(cnstnames, params):
                paramsdict[name] = value
            for name, param in paramsdict.items():
                self.checker.model.constants[name].value = param.value
                ModelFactory.module_factory.config.setParam(name, param)

            # self.checker.model.constants.update(paramsdict)
            # logger.info(self.checker.model.constants.items())

            # 根据当前设置的参数值进行samples_per_param次取样,并验证ltl公式
            count = 0  # 成功计数
            for i in range(self.samples_per_param):
                # 获取随机路径
                _, path = self.checker.gen_random_path()
                # logger.info("path: {}".format(str(path)))
                # 验证ltl公式
                success = self.checker.verify(path)
                # logger.info("verification: {}".format(str(success)))
                count += int(success)
                # logger.info("==============")

            prob = float(count) / self.samples_per_param
            # logger.info('{}: {}/{} paths satisfy ltl'.format(paramsdict, count, self.samples_per_param))
            lparamvalues = paramsdict.values() # the 'l' prefix indicate it's a list type
            lparamvalues = map(lambda constant: constant.get_value(), lparamvalues)
            results.append((lparamvalues, prob))

        return results

    # 对给定的参数值进行model checking
    # 调用Checker的验证方法
    # return []
    def modelcheck(self):
        # logger.info("run_checker ExpeWrapper's model checking.")
        paramslist = self._constants.values() # list of list
        # logger.info(paramslist)
        results = []
        for params in product(*paramslist):
            for constant in params:
                self.checker.model.constants[constant.get_name()].value =  constant.get_value()
            low, high = self.checker.mc2()
            results.append((params, (low+high)/2.0))
            # logger.info("params: {0}, prob: {1}".format(str(params), (low+high)/2.0))
        return results


def main():
    from test.PoissionProcess import poission_model
    from util.util import interval
    from module.Module import Constant
    model = poission_model()
    ltl = ['!', 'U[0,1]', None, 'T', 'nge4', None, None]  # 一秒之内n<4
    checker = Checker.Checker(model, ltl)
    wrapper = ExperimentWrapper(checker)
    constants = []
    for value in interval(0.5, 5, 0.1):
        constants.append(Constant('r', value))
    wrapper.setconstants([constants])
    results = wrapper.do_expe()
    wrapper.modelcheck()


# 根据给定的参数值进行实验
# params: [[constant1s], ...[constantns]] e.g. list of list of constant instance
# return [(paramvalues,prob)]
def executepoissionexpe(params):
    from test.PoissionProcess import poission_model
    model = poission_model()
    ltl = ['!', 'U[0,1]', None, 'T', 'nge4', None, None]  # 一秒之内n<4
    checker = Checker.Checker(model, ltl)
    wrapper = ExperimentWrapper(checker)
    wrapper.setconstants(params)
    results = wrapper.do_expe()
    return results


# 根据给定的参数进行模型检验
# params: [[constant1s], ...[constantns]] e.g. list of list of constant instance
# return [(paramvalues,  prob)]
def executemodelchecking(params):
    from test.PoissionProcess import poission_model
    model = poission_model()
    ltl = ['!', 'U[0,1]', None, 'T', 'nge4', None, None]  # 一秒之内n<4
    checker = Checker.Checker(model, ltl)
    wrapper = ExperimentWrapper(checker)
    wrapper.setconstants(params)
    results = wrapper.modelcheck()
    return results


if __name__ == "__main__":
    main()
