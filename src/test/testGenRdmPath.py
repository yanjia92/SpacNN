# -*- coding:utf-8 -*-
from model.ModelFactory import ModelFactory
import cProfile, pstats, StringIO
import io
from module.ModulesFile import StepGenThd
import time

duration = 1*365*2


def test_parsed(parsed=None):
    if not parsed:
        parsed = ModelFactory.get_parsed()
        parsed.duration = duration
        parsed.prepare_commands()
    # thd = StepGenThd(model=parsed)
    # thd.setDaemon(True)
    # thd.start()
    # time.sleep(2)  # 模拟用户输入
    pr = cProfile.Profile()
    pr.enable()
    path = parsed.get_random_path_V2()
    pr.disable()
    print "len of path:{}".format(len(path))
    s = StringIO.StringIO()
    sortby = "cumulative"
    ps = pstats.Stats(pr, stream=io.FileIO("./parsed", mode='w')).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()


def test_built():
    built = ModelFactory.get_built()
    built.prepare_commands()
    pr = cProfile.Profile()
    pr.enable()
    # result, path = built.gen_random_path(duration=duration)
    path = built.get_random_path_V2(duration=duration)
    # _, path = built.gen_random_path(duration=duration)
    pr.disable()
    # id1 = id(path[0].ap_set)
    # id2 = id(path[1].ap_set)
    # print "len of path:{}".format(len(path))
    s = StringIO.StringIO()
    sortby = "cumulative"
    ps = pstats.Stats(pr, stream=io.FileIO("./built", mode='w')).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()


test_parsed()
# test_built()
