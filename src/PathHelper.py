import os
import platform


def get_sep():
    if "Windows" in platform.system():
        return '\\'
    else:
        return '/'


def get_src_dir():
    working_dir = os.path.dirname(os.path.realpath(__file__))
    return working_dir


def get_proj_dir():
    src_dir = get_src_dir()
    path_sep = get_sep()
    return src_dir[:src_dir.rfind(path_sep)]


def test():
    print get_src_dir()
    print get_proj_dir()


test()
