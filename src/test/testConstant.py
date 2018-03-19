# -*- coding: utf-8 -*-
from module.Module import Constant

c1 = Constant('c', 10)
c2 = Constant('c', 3)

def testConstantArithmatics():
    assert c1 + c2 == 13
    assert c1 + 3 == 13
    assert c1 / 5 == 2
    assert -c1 + 9 == -1
    assert 1.0 / (c1 / 5) == 0.5
    assert -c1 + 9 == -1
    assert c1 / c1 == 1

def testConstantCompare():
    assert c1 < 11
    assert c2 < c1
    assert c1 > c2
    assert c1 > 9
    assert c1 == 10
    assert 10 == c1

if __name__ == '__main__':
    testConstantArithmatics()
    testConstantCompare()
