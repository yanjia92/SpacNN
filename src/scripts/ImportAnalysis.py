import sys
import os
from PathHelper import get_sep

def analysis_import(py_file):
    dependencies = set()
    with open(py_file) as f:
        for line in f:
            line = line.strip()
            if line.find("import") == 0 or line.find("from") == 0:
                dependencies.add(line.split(" ")[1])
    return dependencies


def main():
    args = sys.argv
    if len(args) != 2:
        print "usage: python ImportAnalysis.py path_to_root"
        sys.exit(1)
    root = args[1]
    dependencies = set()
    for dirpath, dirnames, filenames in os.walk(root):
        # print "dirpath={}, dirnames={}, filenames={}".format(dirpath, dirnames, filenames)
        for f in filenames:
            if f[-2:] == "py":
                if not dirpath.endswith(get_sep()):
                    dirpath += get_sep()
                dependencies.update(analysis_import(dirpath + f))
    print str(dependencies)


if __name__ == "__main__":
    main()
