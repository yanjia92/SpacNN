import os
curdir = os.getcwd()
pardir = os.path.dirname(os.path.abspath(curdir))
import sys
sys.path.append(pardir)
from util.AnnotationHelper import deprecated


@deprecated("State class is no longer used, since state_id is not needed. The whole class could be replaced by ap_set")
class State(object):
    # state_id = None
    # ap_set = None

    def __init__(self, state_id, ap_set):
        self.state_id = state_id
        self.ap_set = ap_set

    def __str__(self):
        result = 'State(id: %d, %s)' % (self.sid, str(self.ap_set))
        return result


def test():
    s = State(1, set())
    print s.__dict__


if __name__ == "__main__":
    test()