try:
    import matplotlib.pyplot as plt
except ImportError:
    print "matplotlib not installed."
from math import *


def plot_multi(*args, **kwargs):
    '''args: line_data, format: (x, y, label)'''
    if "title" in kwargs.keys():
        title = kwargs.get("title")
        plt.title(title)

    for line_data in args:
        x, y, label = line_data
        plt.plot(x, y, label=label)
    
    if "legend" in kwargs.keys() and not kwargs.get("legend"):
        pass
    else:
        plt.legend()
    if "xlabel" in kwargs.keys():
        plt.xlabel(kwargs.get("xlabel"))
    if "ylabel" in kwargs.keys():
        plt.ylabel(kwargs.get("ylabel"))
    plt.show()


def test():
    x1 = (1, 2, 3)
    y1 = map(lambda x: sin(x), x1)
    x2 = (1, 2, 3)
    y2 = map(lambda x: cos(x), x2)
    line_datas = ((x1, y1, "label1"), (x2, y2, "label2"))
    plot_multi(*line_datas)


if __name__ == "__main__":
    test()

