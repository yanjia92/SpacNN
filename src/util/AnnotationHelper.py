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


# def test_built():
#     built = ModelFactory.get_built()
#     built.prepare_commands()
#     pr = cProfile.Profile()
#     pr.enable()
#     # result, path = built.gen_random_path(duration=duration)
#     path = built.get_random_path_V2(duration=duration)
#     pr.disable()
#     id1 = id(path[0].ap_set)
#     id2 = id(path[1].ap_set)
#     print "len of path:{}".format(len(path))
#     s = StringIO.StringIO()
#     sortby = "cumulative"
#     ps = pstats.Stats(pr, stream=io.FileIO("./built", mode='w')).sort_stats(sortby)
#     ps.print_stats()
#     print s.getvalue()
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
    # def wrapper(*args, **kwargs):
    #     pr = cProfile.Profile()
    #     pr.enable()
    #     func(*args, **kwargs)
    #     pr.disable()
    #     s = StringIO.StringIO()
    #     sortby = "cumulative"
    #     ps = pstats.Stats(pr, stream=io.FileIO(name, mode='w')).sort_stats(sortby)
    #     ps.print_stats()
    #     print s.getvalue()
    #
    # return wrapper

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

if __name__ == "__main__":
    print test(1)



