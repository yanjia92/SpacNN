# -*- coding: utf-8 -*-
from module.Module import Module, Constant, Variable, Command, CommandKind
from util.MathUtils import *
from util.util import *
import logging
import sys
from config.SPSConfig import SPSConfig
logger = logging.getLogger("test fail prob sb.py")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)
import matplotlib.pyplot as plt
from compiler.PRISMParser import ModelConstructor

YEAR = 5

# timer module of the system
timer = Module('timer_module')
timer.addConstant(Constant('TIME_LIMIT', YEAR * 365))  # 2 years
day = Variable(
    'day',
    1,
    range(timer.getConstant('TIME_LIMIT').getValue() + 1),
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
    vs['day'].setValue(vs['day'].getValue() + 1)
    vs['timer_turn'].setValue(False)

inc_day = Command(
    'inc day',
    lambda vs,
    cs: vs['timer_turn'] == True and vs['day'] <= timer.getConstant('TIME_LIMIT').getValue(),
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
    vs['sb_status'].setValue(0)
    vs['timer_turn'].setValue(True)

# use closure to delay the computation of fail rate
def f1(day_var):
    def failprobsb():
        # return the failure probability of solar battery after day-dose
        niel_dose = sb.getConstant('SB_K').getValue() * sb.getConstant('SCREEN_THICKNESS').getValue() * (day_var.getValue() / 365.0)
        x = (1 - sb.getConstant('SB_P_THRESHOLD').getValue()) / \
            log(1 + niel_dose * sb.getConstant('SB_B').getValue())
        std_x = (
            x -
            sb.getConstant('SB_A_MU').getValue() /
            sb.getConstant('SB_A_SIGMA').getValue())
        return 1- pcf(std_x)
    return failprobsb

def f1n(day_var):
    def normalprobsb():
        niel_dose = sb.getConstant('SB_K').getValue() * sb.getConstant('SCREEN_THICKNESS').getValue() * (
        day_var.getValue() / 365.0)
        x = (1 - sb.getConstant('SB_P_THRESHOLD').getValue()) / \
            log(1 + niel_dose * sb.getConstant('SB_B').getValue())
        std_x = (
            x -
            sb.getConstant('SB_A_MU').getValue() /
            sb.getConstant('SB_A_SIGMA').getValue())
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
    lambda vs, cs: vs['timer_turn'].setValue(True),
    sb,
    f1n(timer.getVariable('day'))
)
sb.addCommand(comm_normal)


def test():
    for t in range(1, 11):
        sb.setConstant(Constant('SCREEN_THICKNESS', t))
        ps = []
        doses = []
        std_xs = []
        for v in [Variable('day', i) for i in interval(1, 365*YEAR, 1)]:
            dose = v.getValue()/365.0 * sb.getConstant("SB_K").getValue() * sb.getConstant("SCREEN_THICKNESS").getValue()
            doses.append(dose)
            x = (1- sb.getConstant("SB_P_THRESHOLD").getValue())/ (log(1 + sb.getConstant("SB_B").getValue() * dose))
            std_x = (x - sb.getConstant("SB_A_MU").getValue())/sb.getConstant("SB_A_SIGMA").getValue()
            p = 1 - pcf(std_x)
            ps.append(p)
            std_xs.append(std_x)
        # if t == 10:
        #     # when thickness = 10
        #     logger.info("max dose=%f, max prob=%f", doses[-1], ps[-1])
        #     plt.plot(doses, ps, "k")
        #     plt.xlabel("dose")
        #     plt.ylabel("failure probability")
        #     plt.show()
        print "p={}, std_x={}".format(ps[-1], std_xs[-1])


def get_parsed():
    constructor = ModelConstructor()
    model = constructor.parseModelFile("../../prism_model/smalltest.prism")
    return model


# 测试同样的数据for parsed model
def test_parsed():
    parsed = get_parsed()
    days = range(1, YEAR * 365)
    sb_mdl = parsed.getModuleByName("SB")
    fail_probs = []
    for thickness in range(1, 11):
        parsed.setConstant("SCREEN_THICKNESS", thickness)
        for day in days:
            parsed.setVariable("day", day)
            fail_prob = sb_mdl.commands[0].prob
            print "thickness={}, prob={}".format(thickness, fail_prob)


if __name__ == '__main__':
    # test()
    test_parsed()