import os
import platform


class LogHelper(object):

    def __init__(self):
        print "logging root: {}".format(str(LogHelper.LOGGING_ROOT))

    @staticmethod
    def get_sep():
        if "Windows" in platform.system():
            sep = '\\'
        else:
            sep = '/'
        return sep

    @classmethod
    def get_logging_root(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = base_dir[:base_dir.rfind(cls.get_sep())]
        return src_dir + cls.get_sep() + "log" + cls.get_sep()


if __name__ == "__main__":
    print LogHelper.get_logging_root()