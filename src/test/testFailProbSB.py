from module.Module import *
from util.MathUtils import *
from util.util import *

YEAR = 2

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

# solar battery module of the system
sb = Module("solar battery module")

# set initial value None to denote uncertainty
screenthick = Constant('SCREEN_THICKNESS', None)
sb.addConstant(screenthick)
# the dose of one year: dose = K_SB * thickness
sb.addConstant(Constant('SB_K', 0.0039))
sb.addConstant(Constant('SB_B', 12))
sb.addConstant(Constant('SB_P_THRESHOLD', 0.7))
sb.addConstant(Constant('SB_A_MU', 0.1754))
sb.addConstant(Constant('SB_A_SIGMA', 0.02319029 * 21))

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
    sb.setConstant(Constant('SCREEN_THICKNESS', 1))
    ps = []
    for v in [Variable('day', i) for i in interval(1, 365*YEAR, 1)]:
        dose = v.getValue()/365.0 * sb.getConstant("SB_K").getValue() * sb.getConstant("SCREEN_THICKNESS").getValue()
        x = (1- sb.getConstant("SB_P_THRESHOLD").getValue())/ (log(1 + sb.getConstant("SB_B").getValue() * dose))
        std_x = (x - sb.getConstant("SB_A_MU").getValue())/sb.getConstant("SB_A_SIGMA").getValue()
        p = 1 - pcf(std_x)
        ps.append(p)
    print str(ps[-3:])

if __name__ == '__main__':
    test()