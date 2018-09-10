import time
from module.Module import BoundedVariable

times = 100000


def funcadd(v1, v2):
    return v1+v2


def testfunc():
    v1 = 1
    v2 = 3
    for i in range(times):
        funcadd(v1, v2)


def testlambda():
    v1 = 1
    v2 = 3
    func = lambda x,y: x+y
    for i in range(times):
        func(v1, v2)

# test for retrieve action of map
def testmap():
    v1 = BoundedVariable('a', 1, range(2), int)
    d = {"a": v1,
         "func": lambda: 1+2
    }
    for i in range(74825):
        v = d.get("func")
        if callable(v):
            pass
        else:
            pass

begin = time.clock()
testmap()
end = time.clock()
print end - begin

