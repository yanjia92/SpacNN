from module.NextMove import NextMove
# logger = logging.getLogger("Step logger")
# logger.addHandler(logging.StreamHandler(sys.stdout))
# logger.setLevel(logging.ERROR)


class Step(object):
    def __init__(
        self,
        ap_set,
        next_move
    ):
        self.next_move = next_move
        self.ap_set = ap_set

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        # if not hasattr(self.prob, '__call__'):
        #     return 'Step:(ap={}, command={}, prob={})'.format(
        #         str(self.ap_set), self.name, self.prob)
        # return 'Step:(ap={}, command={}, prob={})'.format(
        #     str(self.ap_set), self.name, self.prob())
        return "{} of module_{}, action={}".format(self.name, self.cmds[0].module, [var.name for var in self.cmds[0].action.keys()])

    def __getattr__(self, item):
        # owner = self.map[item]
        # return object.__getattribute__(owner, item)
        if item in self.next_move._fields:
            return getattr(self.next_move, item)
        if self.next_move.cmds is not None and item in self.next_move.cmds[0].__dict__.keys():
            return self.next_move.cmds[0].__dict__[item]

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
