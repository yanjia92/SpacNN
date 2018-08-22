from compiler.PRISMParser import ModelConstructor as Constructor


def buildCommand():
    constructor = Constructor()
    model = constructor._parseModelFile("../../prism_model/CommandTest.prism")
    return model.modules.values()[0].commands.values()[0]


def test():
    cmd = buildCommand()
    assert cmd.evaluate() == True
    cmd.execute()
    assert cmd.vs['a'].get_value() == 0


if __name__ == '__main__':
    test()
