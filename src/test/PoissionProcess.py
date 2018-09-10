# -*- coding:utf-8 -*-
# building a simple poission process with ModulesFile.py
from module.ModulesFile import *
from module.Module import *
from constant.Constants import *


def poission_model():
    module = Module("poission process")
    module.addConstant(Constant('r', None))

    # variable definition
    v = BoundedVariable('n', 0, None, int, False)  # n: int init 0;
    module.add_variable(v)
    # command definition

    comm = Command(
        '',
        lambda vs,
        cs: True,
        lambda vs,
        cs: vs['n'].set_value(
            vs['n'].get_value() +
            1),
        module,
        module.getConstant("r"),
        CommandKind.NONE,
        None)
    module.addCommand(comm)

    # 增加label表示n>=4这个ap
    labels = dict()
    def nge4(vs, cs):
        return vs['n'] >= 4
    labels['nge4'] = nge4

    model = ModulesFile(ModelType.CTMC, modules=[module], labels=labels)
    return model


def test_run():
    model = poission_model()
    _, steps = model.gen_random_path(1.0)
    model.exportPathTo(steps, OUTPUT_DIR + "path.txt")


def main():
    test_run()


if __name__ == '__main__':
    main()
