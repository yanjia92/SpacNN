from testPrepareCmds import getBuiltModel, timeit

def test():
    model = getBuiltModel()
    model.prepareCommands()
    timeit(model.genRandomPath, 365*2)

test()