# -*- coding: utf-8 -*-
import logging
import sys
from math import fabs

from config.SPSConfig import SPSConfig
from module.Module import Module, Constant, Variable, Command, CommandKind
from util.MathUtils import *
from util.util import *

logger = logging.getLogger("test fail prob sb.py")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("../log/testsbfail.log", "w"))
logger.setLevel(logging.DEBUG)
from compiler.PRISMParser import ModelConstructor

YEAR = 5

# timer module of the system
timer = Module('timer_module')
timer.addConstant(Constant('TIME_LIMIT', YEAR * 365))  # 2 years
day = Variable(
    'day',
    1,
    range(timer.getConstant('TIME_LIMIT').get_value() + 1),
    int,
    True
)
timer_turn = Variable(
    'timer_turn',
    True,
    set([True, False]),
    bool,
    True
)
timer.addVariable(day)
timer.addVariable(timer_turn)

def incdayaction(vs, cs):
    vs['day'].set_value(vs['day'].get_value() + 1)
    vs['timer_turn'].set_value(False)

inc_day = Command(
    'inc day',
    lambda vs,
    cs: vs['timer_turn'] == True and vs['day'] <= timer.getConstant('TIME_LIMIT').get_value(),
    incdayaction,
    timer,
    1.0)
timer.addCommand(inc_day)

config = SPSConfig()

# solar battery module of the system
sb = Module("solar battery module")

# set initial value None to denote uncertainty
screenthick = Constant('SCREEN_THICKNESS', None)
sb.addConstant(screenthick)
# the dose of one year: dose = K_SB * thickness
sb.addConstant(config.getParam("SB_K"))
sb.addConstant(config.getParam("SB_B"))
sb.addConstant(config.getParam("SB_P_THRESHOLD"))
sb.addConstant(config.getParam("SB_A_MU"))
sb.addConstant(config.getParam("SB_A_SIGMA"))

# variables
sb_status = Variable('sb_status', 1, range(2), int,
                     True)
sb.addVariable(sb_status)

def failaction(vs, cs):
    vs['sb_status'].set_value(0)
    vs['timer_turn'].set_value(True)

# use closure to delay the computation of fail rate
def f1(day_var):
    def failprobsb():
        # return the failure probability of solar battery after day-dose
        niel_dose = sb.getConstant('SB_K').get_value() * sb.getConstant('SCREEN_THICKNESS').get_value() * (day_var.get_value() / 365.0)
        x = (1 - sb.getConstant('SB_P_THRESHOLD').get_value()) / \
            log(1 + niel_dose * sb.getConstant('SB_B').get_value())
        std_x = (
            x -
            sb.getConstant('SB_A_MU').get_value() /
            sb.getConstant('SB_A_SIGMA').get_value())
        return 1 - pcf(std_x)
    return failprobsb

def f1n(day_var):
    def normalprobsb():
        niel_dose = sb.getConstant('SB_K').get_value() * sb.getConstant('SCREEN_THICKNESS').get_value() * (
            day_var.get_value() / 365.0)
        x = (1 - sb.getConstant('SB_P_THRESHOLD').get_value()) / \
            log(1 + niel_dose * sb.getConstant('SB_B').get_value())
        std_x = (
            x -
            sb.getConstant('SB_A_MU').get_value() /
            sb.getConstant('SB_A_SIGMA').get_value())
        return pcf(std_x)
    return normalprobsb

comm_fail = Command(
    'solar battery failure command',
    lambda vs, cs: vs['sb_status'] == 1 and vs['timer_turn'] == False,
    failaction,
    sb,
    f1(timer.getVariable('day')),
    kind=CommandKind.FAILURE
)
sb.addCommand(comm_fail)

comm_normal = Command(
    'solar battery stay-normal command',
    lambda vs, cs: vs['sb_status'] == 1 and vs['timer_turn'] == False,
    lambda vs, cs: vs['timer_turn'].set_value(True),
    sb,
    f1n(timer.getVariable('day'))
)
sb.addCommand(comm_normal)


def test():
    results = []
    logger.info("===============built===============")
    for t in range(4, 5):
        sb.setConstant(Constant('SCREEN_THICKNESS', t))
        ps = []
        doses = []
        std_xs = []
        for v in [Variable('day', i) for i in interval(1, 365*YEAR, 1)]:
            dose = v.get_value() / 365.0 * sb.getConstant("SB_K").get_value() * sb.getConstant("SCREEN_THICKNESS").get_value()
            doses.append(dose)
            x = (1 - sb.getConstant("SB_P_THRESHOLD").get_value()) / (log(1 + sb.getConstant("SB_B").get_value() * dose))
            std_x = (x - sb.getConstant("SB_A_MU").get_value()) / sb.getConstant("SB_A_SIGMA").get_value()
            p = 1 - pcf(std_x)
            ps.append(p)
            std_xs.append(std_x)
        results.append(ps)
        logger.info("thickness={}, p_max={}".format(t, ps[-1]))
    return results


def get_parsed():
    constructor = ModelConstructor()
    model = constructor._parseModelFile("../../prism_model/smalltest.prism")
    return model


# 测试同样的数据for parsed model
def test_parsed():
    parsed = get_parsed()
    days = range(1, YEAR * 365+1)
    sb_mdl = parsed.getModuleByName("SB")
    results = []
    logger.info("===============parsed===============")
    for thickness in range(4, 5):
        probs = []
        parsed.setConstant("SCREEN_THICKNESS", thickness)
        for d in days:
            parsed.setVariable("day", d)
            fail_prob = sb_mdl.commands["sb_fail_cmd"].prob()
            probs.append(fail_prob)
        results.append(probs)
        logger.info("thickness={}, p_max={}".format(thickness, probs[-1]))
    return results


def test_final():
    # result_parsed = test_parsed()
    # result_built = test()
    # for ps1, ps2 in zip(result_parsed, result_built):
    #     for p1, p2 in zip(ps1, ps2):
    #         assert p1 == p2
    result1 = test_parsed()[0]
    result2 = test()[0]
    precision = 1e-6
    for day, (v1, v2) in enumerate(zip(result1, result2)):
        assert fabs(v1 - v2) <= precision, "day={}, v1={}, v2={}".format(day+1, v1, v2)


if __name__ == '__main__':
    test_final()