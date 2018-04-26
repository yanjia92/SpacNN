# -*- coding: utf-8 -*-
import time
from collections import defaultdict

# make sure one function only get called once
already_timed = set()
timeit_map = defaultdict(lambda: 0)
countit_map = defaultdict(lambda: 0)


def timeandcount(fn):

    def inner(*args, **kwargs):
        countit_map[fn.__name__] += 1
        begin = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        if fn.__name__ not in already_timed:
            print "Timeit result of func {}: {}".format(fn.__name__, end - begin)
            timeit_map[fn.__name__] = end - begin
            already_timed.add(fn.__name__)
        return result

    return inner


def print_stat():
    for k, v in countit_map.items():
        print "k={}, v={}".format(k, v)

    timesum = 0
    for func_name in timeit_map.keys():
        timesum += timeit_map[func_name] * countit_map[func_name]
    print "timesum={}".format(timesum)


def clear_stat():
    already_timed.clear()
    timeit_map.clear()
    countit_map.clear()

