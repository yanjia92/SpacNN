class NextMove(object):
    def __init__(
            self,
            cmd=None,
            holding_time=None,
            passed_time=None,
            exit_rate=None,
            biasing_exit_rate=None):
        self.cmd = cmd
        self.holding_time = holding_time
        self.passed_time = passed_time
        self.exit_rate = exit_rate
        self.biasing_exit_rate = biasing_exit_rate

