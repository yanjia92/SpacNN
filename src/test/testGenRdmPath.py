from model.ModelFactory import ModelFactory
import cProfile, pstats, StringIO
import io


duration = 1*365*2


def test_parsed():
    parsed = ModelFactory.get_parsed()
    parsed.prepareCommands()
    pr = cProfile.Profile()
    pr.enable()
    result, path = parsed.genRandomPath(duration=duration)
    pr.disable()
    print "len of path:{}".format(len(path))
    s = StringIO.StringIO()
    sortby = "cumulative"
    ps = pstats.Stats(pr, stream=io.FileIO("./parsed", mode='w')).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()


def test_built():
    built = ModelFactory.get_built()
    built.prepareCommands()
    pr = cProfile.Profile()
    pr.enable()
    result, path = built.genRandomPath(duration=duration)
    pr.disable()
    print "len of path:{}".format(len(path))
    s = StringIO.StringIO()
    sortby = "cumulative"
    ps = pstats.Stats(pr, stream=io.FileIO("./built", mode='w')).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()


test_parsed()
# test_built()
