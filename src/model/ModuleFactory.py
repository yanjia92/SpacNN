from module.Module import *
from math import log, e, pow
from util.MathUtils import pcf
import logging
logger = logging.getLogger('ModuleFactory logger')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.ERROR)


class ModuleFactory(object):
    def __init__(self, config):
        self.config = config
        self.timer = self._timermodule()
        self.sb = self._sbmodule()
        self.s3r = self._s3rmodule()
        self.bcr = self._bcrmodule()
        self.bdr = self._bdrmodule()

    def _sbmodule(self):
        config = self.config
        module = Module('sb module')
        module.addConstant(config.getParam('SB_K'))
        module.addConstant(config.getParam('SB_A_MU'))
        module.addConstant(config.getParam('SB_A_SIGMA'))
        module.addConstant(config.getParam('SB_B'))
        module.addConstant(config.getParam('SB_P_THRESHOLD'))

        module.addVariable(
            Variable(
                'sb_status',
                1,
                range(2),
                int
            )
        )

        def guard(vs, cs):
            # sb_status and s3r_status must both be 1, e.g. the system has not
            # failed.
            return vs['timer_turn'] is False and vs['sb_status'] == 1 and vs['s3r_status'] == 1 and vs['bcr_status'] == 1 and vs['bdr_status'] == 1

        # failure action
        def faction(vs, cs):
            vs['sb_status'].setValue(0)
            vs['timer_turn'].setValue(True)

        # normal action
        def naction(vs, cs):
            vs['timer_turn'].setValue(True)

        def f(day_var):
            def inner():
                day = day_var.getValue()
                dose = module.getConstant(
                    'SB_K') * config.getParam('SCREEN_THICKNESS') * day / 365.0
                x = (-module.getConstant('SB_P_THRESHOLD') + 1) / \
                    (log(module.getConstant('SB_B') * dose + 1))
                std_x = 1.0 / (module.getConstant('SB_A_SIGMA') /
                               (-module.getConstant('SB_A_MU') + x))
                return 1 - pcf(std_x)
            return inner

        def n(day_var):
            def inner():
                ff = f(day_var)
                return 1 - ff()
            return inner

        if not hasattr(self, 'timer'):
            self.timer = self._timermodule()

        module.addCommand(
            Command(
                'sb failure',
                guard,
                faction,
                module,
                f(self.timer.getVariable('day'))
            )
        )

        module.addCommand(
            Command(
                'sb normal',
                guard,
                naction,
                module,
                n(self.timer.getVariable('day'))
            )
        )
        return module

    def _timermodule(self):
        config = self.config
        module = Module('timer module')
        module.addVariable(
            Variable(
                'day',
                1,
                range(1, config.getParam('DURATION_IN_DAY') + 1),
                int
            )
        )
        module.addVariable(
            Variable(
                'timer_turn',
                True,
                set([True, False]),
                bool
            )
        )

        def guard(vs, cs):
            day_val = vs['day'].getValue()
            DAY_MAX = self.config.getParam("DURATION_IN_DAY")
            t_turn = vs['timer_turn'].getValue()
            return day_val < DAY_MAX and t_turn is True

        def action(vs, cs):
            vs['day'].setValue(vs['day'].getValue() + 1)
            vs['timer_turn'].setValue(False)
        module.addCommand(
            Command(
                'inc day',
                guard,
                action,
                module,
                1.0
            )
        )
        return module

    def _s3rmodule(self):
        config = self.config
        module = Module('s3r module')
        module.addConstant(config.getParam('S3R_K'))
        module.addConstant(config.getParam('S3R_A_MU'))
        module.addConstant(config.getParam('S3R_A_SIGMA'))
        module.addConstant(config.getParam('S3R_B'))
        module.addConstant(config.getParam('S3R_DELTAV_THRESHOLD'))

        module.addVariable(
            Variable(
                's3r_status',
                1,
                range(2),
                int
            )
        )

        def guard(vs, cs):
            # the sb_status and s3r_status must both be 1 for this transition
            # to happen
            return vs['timer_turn'] is False and vs['s3r_status'] == 1 and vs['sb_status'] == 1 and vs['bcr_status'] == 1 and vs['bdr_status'] == 1

        def faction(vs, cs):
            vs['s3r_status'].setValue(0)
            vs['timer_turn'].setValue(True)

        def naction(vs, cs):
            vs['timer_turn'].setValue(True)

        def f(day_var):
            def inner():
                day = day_var.getValue()
                dose = module.getConstant('S3R_K') / config.getParam(
                    'SCREEN_THICKNESS') * (day / 365.0)
                x = config.getParam('S3R_DELTAV_THRESHOLD') / (
                    config.getParam('S3R_B') * pow(e, config.getParam('S3R_B') * dose))
                std_x = (-config.getParam('S3R_A_MU') + x) / \
                    config.getParam('S3R_A_SIGMA').getValue()
                p = 1 - pcf(std_x)
                logger.info('day:{0}, s3r failure prob:{1}'.format(day, p))
                return p
            return inner

        def n(day_var):
            def inner():
                ff = f(day_var)
                return 1 - ff()
            return inner

        if not hasattr(self, 'timer'):
            self.timer = self._timermodule()

        module.addCommand(
            Command(
                's3r failure',
                guard,
                faction,
                module,
                f(self.timer.getVariable('day'))
            )
        )

        module.addCommand(
            Command(
                's3r normal',
                guard,
                naction,
                module,
                n(self.timer.getVariable('day'))
            )
        )
        return module

    def _bcrmodule(self):
        config = self.config
        module = Module('bcr module')

        module.addVariable(
            Variable(
                'bcr_status',
                1,
                range(2),
                int
            )
        )

        def guard(vs, cs):
            # the sb_status and s3r_status must both be 1 for this transition
            # to happen
            return vs['timer_turn'] == False and vs['bcr_status'] == 1 and vs['sb_status'] == 1 and vs['bdr_status'] == 1 and vs['s3r_status'] == 1

        def faction(vs, cs):
            vs['bcr_status'].setValue(0)
            vs['timer_turn'].setValue(True)

        def naction(vs, cs):
            vs['timer_turn'].setValue(True)

        def f(day_var):
            def inner():
                day = day_var.getValue()
                dose = config.getParam('S3R_K') / config.getParam(
                    'SCREEN_THICKNESS') * (day / 365.0)
                x = config.getParam('S3R_DELTAV_THRESHOLD') / (
                    config.getParam('S3R_B') * pow(e, config.getParam('S3R_B') * dose))
                std_x = (-config.getParam('S3R_A_MU') + x) / \
                    config.getParam('S3R_A_SIGMA').getValue()
                p = 1 - pcf(std_x)
                # logger.info('day:{0}, bcr failure prob:{1}'.format(day, p))
                return p
            return inner

        def n(day_var):
            def inner():
                ff = f(day_var)
                return 1 - ff()
            return inner

        if not hasattr(self, 'timer'):
            self.timer = self._timermodule()

        module.addCommand(
            Command(
                'bcr failure',
                guard,
                faction,
                module,
                f(self.timer.getVariable('day'))
            )
        )

        module.addCommand(
            Command(
                'bcr normal',
                guard,
                naction,
                module,
                n(self.timer.getVariable('day'))
            )
        )
        return module

    def _bdrmodule(self):
        config = self.config
        module = Module('bdr module')

        module.addVariable(
            Variable(
                'bdr_status',
                1,
                range(2),
                int
            )
        )

        def guard(vs, cs):
            # the sb_status and s3r_status must both be 1 for this transition
            # to happen
            return vs['timer_turn'] == False and vs['bdr_status'] == 1 and vs['sb_status'] == 1 and vs['bcr_status'] == 1 and vs['s3r_status'] == 1

        def faction(vs, cs):
            vs['bdr_status'].setValue(0)
            vs['timer_turn'].setValue(True)

        def naction(vs, cs):
            vs['timer_turn'].setValue(True)

        def f(day_var):
            def inner():
                day = day_var.getValue()
                dose = config.getParam('S3R_K') / config.getParam(
                    'SCREEN_THICKNESS') * (day / 365.0)
                x = config.getParam('S3R_DELTAV_THRESHOLD') / (
                    config.getParam('S3R_B') * pow(e, config.getParam('S3R_B') * dose))
                std_x = (-config.getParam('S3R_A_MU') + x) / \
                    config.getParam('S3R_A_SIGMA').getValue()
                p = 1 - pcf(std_x)
                return p
            return inner

        def n(day_var):
            def inner():
                ff = f(day_var)
                return 1 - ff()
            return inner

        if not hasattr(self, 'timer'):
            self.timer = self._timermodule()

        module.addCommand(
            Command(
                'bdr failure',
                guard,
                faction,
                module,
                f(self.timer.getVariable('day'))
            )
        )

        module.addCommand(
            Command(
                'bdr normal',
                guard,
                naction,
                module,
                n(self.timer.getVariable('day'))
            )
        )
        return module

    def sbmodule(self):
        return self.sb

    def s3rmodule(self):
        return self.s3r

    def timermodule(self):
        return self.timer

    def bcrmodule(self):
        return self.bcr

    def bdrmodule(self):
        return self.bdr
