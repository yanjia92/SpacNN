# -*- coding:utf-8 -*-
import os.path as ospath
import sys
import StringIO


def walk(root_dir, **options):
    '''
    return [path] of files selected by options
    :param root_dir: root directory to search
    :param options: options to filter files: type for now
    :return:
    '''
    file_type = options.get("type")
    if not file_type.startswith(".") or len(file_type) <= 1:
        return []
    paths = []

    def is_type(fname):
        return fname.endswith(file_type)

    def callback(file_filter, dirname, fnames):
        for fname in map(lambda fname: ospath.join(dirname, fname), fnames):
            if file_filter(fname) and ospath.isfile(fname):
                paths.append(fname)

    ospath.walk(root_dir, callback, is_type)
    return paths


def _get_content(path):
    '''
    return a stringIO object whose content is the file specified by path
    :param path: path
    :return: StringIO
    '''
    if ospath.exists(path) and ospath.isfile(path):
        output = StringIO.StringIO()
        fname = ospath.split(path)[1]
        output.write(fname + '\n')
        output.write("=" * len(fname))
        output.write('\n')
        with open(path, "r") as f:
            for line in f:
                output.write(line)
        return output


def _append_2(var1, var2):
    '''
    append the content of var2 to var1
    :param var1: StringIO
    :param var2: StringIO
    :return: new StringIO object
    '''
    var1.write(var2.getvalue())
    return var1


def main():
    root_dir = sys.argv[1]
    dest_file_name = sys.argv[2]
    py_files = walk(root_dir, type=".py")
    contents = map(_get_content, py_files)
    result = reduce(_append_2, contents)
    with open(ospath.join(root_dir, dest_file_name), "w") as f:
        f.write(result.getvalue())


if __name__ == "__main__":
    main()
