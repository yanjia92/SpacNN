from module.Module import Variable


def t():
    v = Variable("a", 1, range(2), int)
    assert v == 1
    v.set_value(0)
    assert v == 0


t()