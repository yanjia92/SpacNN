# -*- coding: utf-8 -*-
import time
from collections import defaultdict
from threading import Thread
import cProfile
import StringIO
import pstats
import io

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


def async(fn):
    def wrapper(*args, **kwargs):
        thrd = Thread(target=fn, args=args, kwargs=kwargs)
        thrd.start()
    return wrapper


def profileit(filepath):
    def decorator(func):
        def decorated_func(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            result = func(*args, **kwargs)
            pr.disable()
            s = StringIO.StringIO()
            sortby = "cumulative"
            ps = pstats.Stats(pr, stream=io.FileIO(filepath, mode='w')).sort_stats(sortby)
            ps.print_stats()
            # print s.getvalue()
            return result
        return decorated_func
    return decorator


def deprecated(message=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print message
            return func(*args, **kwargs)
        return wrapper
    return decorator


def testname(name):
    def wrapper(f):
        print name
        return f
    return wrapper


def testname2(name):
    def decorator(func):
        print name
        def wrapper1(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper1
    return decorator


def setresult(value):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return value
        return wrapper
    return decorator


@profileit("./profileit_test")
def test(a):
    return a


def singleton(cls):
    '''
    使用注解实现单例模式
    :param cls:
    :return:
    '''
    instances = {}

    def _singleton(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return _singleton


if __name__ == "__main__":
    print test(1)



