# -*- coding: utf-8 -*-
from module.Module import Module, Constant, Variable, Command, CommandKind
from util.MathUtils import *
from util.util import *
import logging
import sys
from config.SPSConfig import SPSConfig
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
        return 1 - pcf(std_x)
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
    results = []
    logger.info("===============built===============")
    for t in range(1, 11):
        sb.setConstant(Constant('SCREEN_THICKNESS', t))
        ps = []
        doses = []
        std_xs = []
        for v in [Variable('day', i) for i in interval(1, 365*YEAR, 1)]:
            dose = v.getValue()/365.0 * sb.getConstant("SB_K").getValue() * sb.getConstant("SCREEN_THICKNESS").getValue()
            doses.append(dose)
            x = (1 - sb.getConstant("SB_P_THRESHOLD").getValue())/ (log(1 + sb.getConstant("SB_B").getValue() * dose))
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
        # print "p={}, std_x={}".format(ps[-1], std_xs[-1])
        results.append(ps)
        logger.info("thickness={}, p_max={}".format(t, ps[-1]))
    return results


def get_parsed():
    constructor = ModelConstructor()
    model = constructor.parseModelFile("../../prism_model/smalltest.prism")
    return model


# 测试同样的数据for parsed model
def test_parsed():
    parsed = get_parsed()
    days = range(1, YEAR * 365+1)
    sb_mdl = parsed.getModuleByName("SB")
    results = []
    logger.info("===============parsed===============")
    for thickness in range(1, 11):
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
    test_parsed()
    test()
    print interval(1, 365*YEAR, 1)[-1]
    print range(1, YEAR * 365+1)[-1]


if __name__ == '__main__':
    test_final()