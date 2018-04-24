from testPrepareCmds import getBuiltModel, timeit

def test():
    model = getBuiltModel()
    # model.prepareCommands()
    timeit(model.genRandomPath, 365*2)  # test generate a one-year path.
    timeit(model.genRandomPath, 365*2)

test()