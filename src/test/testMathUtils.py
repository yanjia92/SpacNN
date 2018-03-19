import matplotlib.pyplot as plt
from util.util import *
from util.MathUtils import *

def testPCF():
    x = interval(-10, 10, 0.1)
    y = map(pcf, x)
    plt.plot(x, y)
    plt.show()


if __name__ == '__main__':
    testPCF()