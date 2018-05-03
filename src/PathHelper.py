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


def get_log_dir():
    src_dir = get_src_dir()
    path_sep = get_sep()
    return src_dir + path_sep + "log"

def get_prism_model_dir():
    return get_proj_dir() + get_sep() + "prism_model"

def test():
    print get_src_dir()
    print get_proj_dir()


if __name__ == "__main__":
    test()
