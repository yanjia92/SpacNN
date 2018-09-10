from module.Module import *
from math import log, e, pow
from util.MathUtils import pcf
import logging
# logger = logging.getLogger('ModuleFactory logger')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.ERROR)


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
        module = Module('SB')
        module.addConstant(config.getParam('SB_K'))
        module.addConstant(config.getParam('SB_A_MU'))
        module.addConstant(config.getParam('SB_A_SIGMA'))
        module.addConstant(config.getParam('SB_B'))
        module.addConstant(config.getParam('SB_P_THRESHOLD'))

        module.add_variable(
            BoundedVariable(
                'sb_status',
                1,
                range(2),
                int
            )
        )   

        def _module_action_guard(vs, cs):
            timer_turn = vs['timer_turn'].get_value()
            sb_status = vs['sb_status'].get_value()
            s3r_status = vs['s3r_status'].get_value()
            bcr_status = vs['bcr_status'].get_value()
            bdr_status = vs['bdr_status'].get_value()
            return timer_turn == False and sb_status == 1 and s3r_status == 1 and bcr_status == 1 and bdr_status == 1

        def faction(vs, cs):
            vs['sb_status'].set_value(0)
            vs['timer_turn'].set_value(True)

        # normal action
        def naction(vs, cs):
            vs['timer_turn'].set_value(True)

        def f(day_var):
            def inner():
                day = day_var.get_value()
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
                'sb_fail_cmd',
                _module_action_guard,
                faction,
                module,
                f(self.timer.getVariable('day'))
            )
        )

        module.addCommand(
            Command(
                'sb_nrl_cmd',
                _module_action_guard,
                naction,
                module,
                n(self.timer.getVariable('day'))
            )
        )
        return module

    def _timermodule(self):
        config = self.config
        module = Module('TIME')
        module.add_variable(
            BoundedVariable(
                'day',
                1,
                range(1, config.getParam('DURATION_IN_DAY') + 1),
                int
            )
        )
        module.add_variable(
            BoundedVariable(
                'timer_turn',
                False,
                set([True, False]),
                bool
            )
        )

        def _timer_action_guard(vs, cs):
            day_val = vs['day'].get_value()
            DAY_MAX = self.config.getParam("DURATION_IN_DAY")
            t_turn = vs['timer_turn'].get_value()
            return day_val < DAY_MAX and t_turn == True

        def action(vs, cs):
            # vs['day'].set_value(vs['day'].get_value() + 1)
            vs['day'].incr()
            vs['timer_turn'].set_value(False)

        module.addCommand(
            Command(
                'inc day',
                _timer_action_guard,
                action,
                module,
                lambda: 1.0
            )
        )
        return module

    def _s3rmodule(self):
        config = self.config
        module = Module('S3R')
        module.addConstant(config.getParam('S3R_K'))
        module.addConstant(config.getParam('S3R_A_MU'))
        module.addConstant(config.getParam('S3R_A_SIGMA'))
        module.addConstant(config.getParam('S3R_B'))
        module.addConstant(config.getParam('S3R_DELTAV_THRESHOLD'))

        module.add_variable(
            BoundedVariable(
                's3r_status',
                1,
                range(2),
                int
            )
        )

        def _module_action_guard(vs, cs):
            timer_turn = vs['timer_turn'].get_value()
            sb_status = vs['sb_status'].get_value()
            s3r_status = vs['s3r_status'].get_value()
            bcr_status = vs['bcr_status'].get_value()
            bdr_status = vs['bdr_status'].get_value()
            return timer_turn == False and sb_status == 1 and s3r_status == 1 and bcr_status == 1 and bdr_status == 1

        def faction(vs, cs):
            vs['s3r_status'].set_value(0)
            vs['timer_turn'].set_value(True)

        def naction(vs, cs):
            vs['timer_turn'].set_value(True)

        def f(day_var):
            def inner():
                day = day_var.get_value()
                dose = module.getConstant('S3R_K') / config.getParam(
                    'SCREEN_THICKNESS') * (day / 365.0)
                x = config.getParam('S3R_DELTAV_THRESHOLD') / (
                    config.getParam('S3R_B') * pow(e, config.getParam('S3R_B') * dose))
                std_x = (-config.getParam('S3R_A_MU') + x) / \
                    config.getParam('S3R_A_SIGMA').get_value()
                p = 1 - pcf(std_x)
                # logger.info('day:{0}, s3r failure prob:{1}'.format(day, p))
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
                's3r_fail_cmd',
                _module_action_guard,
                faction,
                module,
                f(self.timer.getVariable('day'))
            )
        )

        module.addCommand(
            Command(
                's3r_nrl_cmd',
                _module_action_guard,
                naction,
                module,
                n(self.timer.getVariable('day'))
            )
        )
        return module

    def _bcrmodule(self):
        config = self.config
        module = Module('BCR')

        module.add_variable(
            BoundedVariable(
                'bcr_status',
                1,
                range(2),
                int
            )
        )

        def _module_action_guard(vs, cs):
            timer_turn = vs['timer_turn'].get_value()
            sb_status = vs['sb_status'].get_value()
            s3r_status = vs['s3r_status'].get_value()
            bcr_status = vs['bcr_status'].get_value()
            bdr_status = vs['bdr_status'].get_value()
            return timer_turn == False and sb_status == 1 and s3r_status == 1 and bcr_status == 1 and bdr_status == 1

        def faction(vs, cs):
            vs['bcr_status'].set_value(0)
            vs['timer_turn'].set_value(True)

        def naction(vs, cs):
            vs['timer_turn'].set_value(True)

        def f(day_var):
            def inner():
                day = day_var.get_value()
                dose = config.getParam('S3R_K') / config.getParam(
                    'SCREEN_THICKNESS') * (day / 365.0)
                x = config.getParam('S3R_DELTAV_THRESHOLD') / (
                    config.getParam('S3R_B') * pow(e, config.getParam('S3R_B') * dose))
                std_x = (-config.getParam('S3R_A_MU') + x) / \
                    config.getParam('S3R_A_SIGMA').get_value()
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
                'bcr_fail_cmd',
                _module_action_guard,
                faction,
                module,
                f(self.timer.getVariable('day'))
            )
        )

        module.addCommand(
            Command(
                'bcr_nrl_cmd',
                _module_action_guard,
                naction,
                module,
                n(self.timer.getVariable('day'))
            )
        )
        return module

    def _bdrmodule(self):
        config = self.config
        module = Module('BDR')

        module.add_variable(
            BoundedVariable(
                'bdr_status',
                1,
                range(2),
                int
            )
        )
        def _module_action_guard(vs, cs):
            timer_turn = vs['timer_turn'].get_value()
            sb_status = vs['sb_status'].get_value()
            s3r_status = vs['s3r_status'].get_value()
            bcr_status = vs['bcr_status'].get_value()
            bdr_status = vs['bdr_status'].get_value()
            return timer_turn == False and sb_status == 1 and s3r_status == 1 and bcr_status == 1 and bdr_status == 1

        def faction(vs, cs):
            vs['bdr_status'].set_value(0)
            vs['timer_turn'].set_value(True)

        def naction(vs, cs):
            vs['timer_turn'].set_value(True)

        def f(day_var):
            def inner():
                day = day_var.get_value()
                dose = config.getParam('S3R_K') / config.getParam(
                    'SCREEN_THICKNESS') * (day / 365.0)
                x = config.getParam('S3R_DELTAV_THRESHOLD') / (
                    config.getParam('S3R_B') * pow(e, config.getParam('S3R_B') * dose))
                std_x = (-config.getParam('S3R_A_MU') + x) / \
                    config.getParam('S3R_A_SIGMA').get_value()
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
                'bdr_fail_cmd',
                _module_action_guard,
                faction,
                module,
                f(self.timer.getVariable('day'))
            )
        )

        module.addCommand(
            Command(
                'bdr_nrl_cmd',
                _module_action_guard,
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
