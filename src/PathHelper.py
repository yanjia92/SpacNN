import os
from util.SystemUtil import on_windows_platform


def get_sep():
    if on_windows_platform():
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


def get_results_dir():
    return get_proj_dir() + get_sep() + "result"


def get_data_dir():
    return get_proj_dir() + get_sep() + "data"


def test():
    print get_src_dir()
    print get_proj_dir()


if __name__ == "__main__":
    test()
