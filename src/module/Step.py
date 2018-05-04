class Step(object):
    def __init__(
        self,
        state=None,
        next_move=None,
        state_id=None,
        ap_set=None,
        holding_time=None,
        passed_time=None,
        transition=None,
        rate=None,
        biasing_rate=None,
        exit_rate=None,
        biasing_exit_rate=None
    ):
        self.state = state
        self.next_move = next_move
        # if state and next_move:
        #     self.state_id = state.state_id
        #     self.ap_set = state.ap_set
        #     self.holding_time = next_move.holding_time
        #     self.passed_time = next_move.passed_time
        #     self.exit_rate = next_move.exit_rate
        #     self.biasing_exit_rate = next_move.biasing_exit_rate
        #     if next_move.cmd:
        #         self.transition = next_move.cmd.name
        #         self.rate = next_move.cmd.prob
        #         self.biasing_rate = next_move.cmd.biasing_rate
        #     else:
        #         self.transition = "step_without_move"
        #         self.rate = 0.0
        #         self.biasing_rate = 0.0
        # else:
        #     self.init(
        #         state_id,
        #         ap_set,
        #         holding_time,
        #         passed_time,
        #         transition,
        #         rate,
        #         biasing_rate,
        #         exit_rate,
        #         biasing_exit_rate
        #     )

    def init(
            self,
            state_id,
            ap_set,
            holding_time,
            passed_time,
            transition,
            rate,
            biasing_rate,
            exit_rate,
            biasing_exit_rate):
        self.state_id = state_id
        # current state's apSet of State before transition happen
        self.apSet = ap_set
        # time duration before transfer to next state
        self.holdingTime = holding_time
        # time(steps) passed before entering current state
        self.passedTime = passed_time
        # transition name to be taken
        self.transition = transition
        # original rate of the chosen transition
        # used to compute the likelihood ratio of original distribution and the
        # biased distribution
        self.rate = rate
        self.exitRate = exit_rate
        # biasing rate(probability of DTMC actually)
        # by failure biasing methods, such as SFB, BFB, ...
        self.biasingRate = biasing_rate
        self.biasingExitRate = biasing_exit_rate

    def __str__(self):
        return str(self.ap_set)

    def __repr__(self):
        if not hasattr(self.rate, '__call__'):
            return 'Step:(ap={}, command={}, prob={})'.format(
                str(self.ap_set), self.transition, self.rate)
        return 'Step:(ap={}, command={}, prob={})'.format(
            str(self.ap_set), self.transition, self.rate())

    def __getattribute__(self, item):
        if item == "state" or item == "next_move":
            return object.__getattribute__(self, item)
        if item == "state_id" or item == "ap_set":
            return object.__getattribute__(self.state, item)
        return object.(self.next_move, item)

    def asKey(self):
        lAPSet = sorted(list(self.ap_set))
        result = ','.join(lAPSet)
        return '[%s]' % result

    # for now, consider DTMC situation only
    def likelihood(self):
        return self.rate / self.biasing_rate

    def isInitState(self, all_up_label):
        return all_up_label in self.ap_set
