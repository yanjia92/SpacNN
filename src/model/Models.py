# -*- coding: utf-8 -*-
from module.ModulesFile import *
from module.Module import *
from math import *
from util.MathUtils import pcf


def sps_model_dtmc(duration):
    # duration: timer.day的最大值:天数
    # timer module of the system
    timer = Module('timer_module')
    timer.addConstant(Constant('TIME_LIMIT', duration))
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
        cs: vs['timer_turn'] == True and vs['day'] < timer.getConstant('TIME_LIMIT').get_value(),
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
    sb.addConstant(Constant('SB_A_SIGMA', 0.02319029*21))

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
            temp = pcf(std_x)
            i = id(day_var)
            return 1- temp
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

    s3r = Module('S3R模块')
    s3r.addConstant(screenthick)
    s3r.addConstant(Constant('S3R_K', 200.5 / 3.0))  # s3r, bdr, bcr三个模块均摊电离能损
    s3r.addConstant(Constant('S3R_DELTAV_THRESHOLD', 450))
    s3r.addConstant(Constant('S3R_A_MU', 570.8 * 18))
    s3r.addConstant(Constant('S3R_A_SIGMA', 6.7471 * 120))
    s3r.addConstant(Constant('S3R_B', 0.01731))

    s3r_status = Variable(
        's3r_status',
        1,
        range(2),
        int,
        True
    )
    s3r.addVariable(s3r_status)

    def s3rfailaction(vs, cs):
        vs['s3r_status'].set_value(0)
        vs['timer_turn'].set_value(True)

    def f2(day_var):
        def failprobs3r():
            iel_dose = day_var.get_value() / 365.0 * (s3r.getConstant('S3R_K').get_value() / \
                                                      s3r.getConstant('SCREEN_THICKNESS').get_value())
            x = s3r.getConstant('S3R_DELTAV_THRESHOLD').get_value() / (s3r.getConstant('S3R_B').get_value()
                                                                       * pow(e, s3r.getConstant('S3R_B').get_value() * iel_dose))
            std_x = (x - s3r.getConstant('S3R_A_MU').get_value()) / \
                    s3r.getConstant('S3R_A_SIGMA').get_value()
            return 1 - pcf(std_x)
        return failprobs3r

    def f2n(day_var):
        def normalprobs3r():
            iel_dose = day_var.get_value() / 365.0 * (s3r.getConstant('S3R_K').get_value() / \
                                                      s3r.getConstant('SCREEN_THICKNESS').get_value())
            x = s3r.getConstant('S3R_DELTAV_THRESHOLD').get_value() / (s3r.getConstant('S3R_B').get_value()
                                                                       * pow(e, s3r.getConstant(
                'S3R_B').get_value() * iel_dose))
            std_x = (x - s3r.getConstant('S3R_A_MU').get_value()) / \
                    s3r.getConstant('S3R_A_SIGMA').get_value()
            return pcf(std_x)
        return normalprobs3r

    s3r_comm_fail = Command(
        's3r failure command',
        lambda vs, cs: vs['s3r_status'] == 1 and vs['timer_turn'] == False,
        s3rfailaction,
        s3r,
        f2(timer.getVariable('day')),
        CommandKind.FAILURE
    )
    s3r.addCommand(s3r_comm_fail)
    s3r_comm_norm = Command(
        's3r normal command',
        lambda vs, cs: vs['timer_turn'] == False and vs['s3r_status'] == 1,
        lambda vs, cs: vs['timer_turn'].set_value(True),
        s3r,
        f2n(timer.getVariable('day'))
    )
    s3r.addCommand(s3r_comm_norm)

    def failureif(vs, cs):
        return vs['s3r_status'] == 0 or vs['sb_status'] == 0

    labels = dict()
    labels['up'] = lambda vs, cs: vs['s3r_status'] == 1 and vs['sb_status'] == 1
    labels['failure'] = lambda vs, cs: vs['s3r_status'] == 0 or vs['sb_status'] == 0

    i = id(timer.getVariable('day'))

    model = ModulesFile.ModulesFile(
        ModelType.DTMC,
        modules=[timer, sb, s3r],
        failureCondition=failureif,
        labels=labels,
        stopCondition=failureif
    )

    ii = id(model.localVars['day'])
    assert i == ii
    return model
