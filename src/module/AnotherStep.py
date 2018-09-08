from module.CheckerStepMixin import CheckerStepMixin


class AnotherStep(CheckerStepMixin):
    def __init__(self, model_vars, passed_time, duration, label_mapper):
        self._vars = model_vars
        self._passed_time = passed_time
        self._duration = duration
        self._lbl_mapper = label_mapper

    def get_duration(self):
        return self._duration

    def get_passed_time(self):
        return self._passed_time

    def get_ap_set(self):
        return self._lbl_mapper(self._vars)