from module.State import State
from module.NextMove import NextMove
import logging
import sys
logger = logging.getLogger("Step logger")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.ERROR)


class Step(object):
    def __init__(
        self,
        ap_set,
        next_move
    ):
        self.next_move = next_move
        self.ap_set = ap_set

    # def init(
    #         self,
    #         state_id,
    #         ap_set,
    #         holding_time,
    #         passed_time,
    #         transition,
    #         rate,
    #         biasing_rate,
    #         exit_rate,
    #         biasing_exit_rate):
    #     self.state_id = state_id
    #     # current state's apSet of State before transition happen
    #     self.apSet = ap_set
    #     # time duration before transfer to next state
    #     self.holdingTime = holding_time
    #     # time(steps) passed before entering current state
    #     self.passedTime = passed_time
    #     # transition name to be taken
    #     self.transition = transition
    #     # original rate of the chosen transition
    #     # used to compute the likelihood ratio of original distribution and the
    #     # biased distribution
    #     self.rate = rate
    #     self.exitRate = exit_rate
    #     # biasing rate(probability of DTMC actually)
    #     # by failure biasing methods, such as SFB, BFB, ...
    #     self.biasingRate = biasing_rate
    #     self.biasingExitRate = biasing_exit_rate

    def __str__(self):
        return str(self.ap_set)

    def __repr__(self):
        if not hasattr(self.prob, '__call__'):
            return 'Step:(ap={}, command={}, prob={})'.format(
                str(self.ap_set), self.name, self.prob)
        return 'Step:(ap={}, command={}, prob={})'.format(
            str(self.ap_set), self.name, self.prob())

    def __getattr__(self, item):
        # owner = self.map[item]
        # return object.__getattribute__(owner, item)
        if item in self.next_move._fields:
            return getattr(self.next_move, item)
        if self.next_move.cmd is not None and item in self.next_move.cmd.__dict__.keys():
            return self.next_move.cmd.__dict__[item]

    def asKey(self):
        lAPSet = sorted(list(self.ap_set))
        result = ','.join(lAPSet)
        return '[%s]' % result

    # for now, consider DTMC situation only
    def likelihood(self):
        return self.rate / self.biasing_rate

    def isInitState(self, all_up_label):
        return all_up_label in self.ap_set


def test():
    next_move = NextMove()
    step = Step(set(), next_move)
    print step
    # print State.__dict__


if __name__ == "__main__":
    test()
