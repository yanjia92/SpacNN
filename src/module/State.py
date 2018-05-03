import os
curdir = os.getcwd()
pardir = os.path.dirname(os.path.abspath(curdir))
import sys
sys.path.append(pardir)

class State(object):
    def __init__(self, stateId, apSet):
        self.state_id = stateId
        self.ap_set = apSet

    def __str__(self):
        result = 'State(id: %d, %s)' % (self.sid, str(self.ap_set))
        return result

    # check if ap holds at current state
    def checkAP(self, apName):
       return apName in self.ap_set

    # vs,cs,labels: OrderedDict
    def updateAPs(self, vs, cs, labels):
        self.ap_set.clear()
        for ap, func in labels.items():
            if func(vs, cs):
                self.ap_set.add(ap)

    def clearAPSet(self):
        self.ap_set.clear()



