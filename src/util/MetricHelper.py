import time


def timeit(func, *args, **kwargs):
    begin = time.time()
    func(*args, **kwargs)
    end = time.time()
    print "Running {} caused: {}".format(func.__name__, end-begin)