import os
curdir = os.getcwd()
pardir = os.path.dirname(os.path.abspath(curdir))
import sys
sys.path.append(pardir)

class State(object):
    def __init__(self, stateId, apSet):
        self.stateId = stateId
        self.apSet = apSet

    def __str__(self):
        result = 'State(id: %d, %s)' % (self.sid, str(self.apSet))
        return result

    # check if ap holds at current state
    def checkAP(self, apName):
       return apName in self.apSet

    # vs,cs,labels: OrderedDict
    def updateAPs(self, vs, cs, labels):
        self.apSet.clear()
        for ap, func in labels.items():
            if func(vs, cs):
                self.apSet.add(ap)

    def clearAPSet(self):
        self.apSet.clear()



