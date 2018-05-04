import os
curdir = os.getcwd()
pardir = os.path.dirname(os.path.abspath(curdir))
import sys
sys.path.append(pardir)
from collections import namedtuple


class State(object):
    def __init__(self, state_id, ap_set):
        self.state_id = state_id
        self.ap_set = ap_set

    def __str__(self):
        result = 'State(id: %d, %s)' % (self.sid, str(self.ap_set))
        return result

# fields = ["state_id", "ap_set"]
# State = namedtuple("State", fields)



