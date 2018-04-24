from model.ModelFactory import ModelFactory


def test():
    duration = 1*365*2
    parsed = ModelFactory.get_parsed()
    built = ModelFactory.get_built()
    parsed.prepareCommands()
    built.prepareCommands()
    print "parsed result"
    _, _ = parsed.genRandomPath(duration=duration)
    print "built result"
    _, _ = built.genRandomPath(duration=duration)


test()
