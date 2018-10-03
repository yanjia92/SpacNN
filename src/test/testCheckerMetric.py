from compiler.modeltest.testChecker import get_built_model, get_checker, ltl
from util.MetricHelper import timeit


def testMetric():
    model = get_built_model()
    checker = get_checker(model, ltl, 365*2)
    timeit(checker.run_smc)


if __name__ == "__main__":
    testMetric()