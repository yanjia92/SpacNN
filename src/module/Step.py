class Step(object):
    def __init__(self, state, next_move=None):
        if next_move:
            self.init(
                state.state_id,
                state.ap_set,
                next_move.holding_time,
                next_move.passed_time,
                next_move.cmd.name,
                next_move.cmd.prob,
                next_move.cmd.biasing_rate,
                next_move.exit_rate,
                next_move.biasing_exit_rate)
        else:
            self.init(state.state_id, state.ap_set)

    def init(
            self,
            stateId,
            apSet,
            holdingTime=None,
            passedTime=None,
            transition=None,
            rate=None,
            biasingRate=None,
            exitRate=None,
            biasingExitRate=None):
        # current state's stateId before transition happen
        self.stateId = stateId
        # current state's apSet of State before transition happen
        self.apSet = apSet
        # time duration before transfer to next state
        self.holdingTime = holdingTime
        # time(steps) passed before entering current state
        self.passedTime = passedTime
        # transition name to be taken
        self.transition = transition
        # original rate of the chosen transition
        # used to compute the likelihood ratio of original distribution and the
        # biased distribution
        self.rate = rate
        self.exitRate = exitRate
        # biasing rate(probability of DTMC actually)
        # by failure biasing methods, such as SFB, BFB, ...
        self.biasingRate = biasingRate
        self.biasingExitRate = biasingExitRate

    def __str__(self):
        return str(self.apSet)

    def __repr__(self):
        if not hasattr(self.rate, '__call__'):
            return 'Step:(ap={}, command={}, prob={})'.format(
                str(self.ap_set), self.transition, self.rate)
        return 'Step:(ap={}, command={}, prob={})'.format(
            str(self.apSet), self.transition, self.rate())

    def asKey(self):
        lAPSet = sorted(list(self.apSet))
        result = ','.join(lAPSet)
        return '[%s]' % result

    # for now, consider DTMC situation only
    def likelihood(self):
        return self.rate / self.biasingRate

    def isInitState(self):
        return "allUp" in self.apSet
