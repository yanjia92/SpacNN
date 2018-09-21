from module.Module import BoundedVariable


def t():
    v = BoundedVariable("a", 1, range(2), int)
    assert v == 1
    v.set_value(0)
    assert v == 0


t()