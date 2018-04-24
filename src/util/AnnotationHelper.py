import time


def timeit(fn):
    def inner(*args, **kwargs):
        begin = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        print "Timeit result of func {}: {}".format(fn.__name__, end - begin)
        return result
    return inner