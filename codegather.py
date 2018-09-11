# -*- coding:utf-8 -*-
import os


def _append2(src_path, dest_path):
    if os.path.isfile(src_path) and os.path.isfile(dest_path):
        with open(dest_path, 'a') as target:
            with open(src_path, 'r') as src:
                target.write(src.read())
    else:
        print "src={} or dest={} path not exist".format(src_path, dest_path)


def _gen_dir_filter(exclusive_paths):
    def _filter(_tuple):
        dirpath = _tuple[0]
        for prefix in exclusive_paths:
            if dirpath.startswith(prefix):
                return False
        return True
    return _filter


def _gen_file_filter(extensions):
    def _filter(_file):
        if _file.startswith("__") or _file.startswith("_"):
            return False
        for extension in extensions:
            if _file.endswith(extension):
                return True
            return False
    return _filter


# 整理src目录下的所有源代码文件，并将其汇总到sources.txt中

def gather(root_path, exlusive_paths=None, dest_path=None, extensions=(".py",)):
    if not root_path:
        return
    if not dest_path:
        dest_path = os.path.join(os.getcwd(), "sources.txt")

    dir_filter = _gen_dir_filter(exlusive_paths)
    file_filter = _gen_file_filter(extensions)
    dirs = []
    for dirname, dirpaths, filenames in os.walk(root_path):
        dirs.append((dirname, dirpaths, filenames))
    dirs = filter(dir_filter, dirs)
    for dir_tuple in dirs:
        filtered_files = filter(file_filter, dir_tuple[2])
        for src_path in filtered_files:
            print os.path.join(dir_tuple[0], src_path)
            _append2(os.path.join(dir_tuple[0], src_path), dest_path)


if __name__ == "__main__":
    exclusive_paths = [
        "D:\Users\jyan\Desktop\SpacNN\src\compiler\ply",
        "D:\Users\jyan\Desktop\SpacNN\\venv"
    ]
    root_path = os.getcwd()
    gather(root_path, exclusive_paths)

