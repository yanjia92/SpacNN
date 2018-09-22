# -*- coding: utf-8 -*-
from PathHelper import *
import re
from compiler.removeComment import clear_comment


class RenamingHelper(object):
    '''
    helper class to handle prism file module renaming
    '''

    def __init__(self, path):
        '''
        constructor
        :param path: path of prism file
        '''
        self._original_path = path
        self._path = clear_comment(path)
        self._lines = []
        self._module_map = {}  # {module_name: (begin_index, end_index)}
        self._module_substitute_map = {}  # {module_name: [(str, str)]}
        self._module_def_pattern = r'module (?P<module_name>[a-zA-Z]\w*)'
        self._substitute_pattern = r'\w+\s*=\s*\w+'
        self._substitute_cmp = self._gen_subs_cmp()
        self._load()

    def _load(self):
        '''
        read file contents into self._lines
        :return:
        '''
        with open(self._path) as f:
            self._lines = f.readlines()
        self._load_modules()

    def _find_end_index(self, begin_index):
        '''
        从 begin_index+1 处开始查找endmodule行
        :param begin_index: the index of module AAA line in self._lines
        :return: endmodule line index(exclusive)
        '''
        for index in range(begin_index, len(self._lines)):
            if "endmodule" in self._lines[index]:
                return index + 1

    def _get_module_name(self, line):
        '''
        获取module的名字
        :param line: module AAA line
        :return: module name
        '''
        match = re.search(self._module_def_pattern, line)
        if match:
            return match.group("module_name")

    def _get_substitute(self, line):
        '''
        获取renaming statement中的所有的代替对
        :param line: example: module process2 = process1[a1=a2, a3=a4] endmodule
        :return: [(original, substitute)]
        '''
        substitutes = re.findall(self._substitute_pattern, line)
        results = []
        module_name_handled = False
        for equation in substitutes:
            tokens = equation.split('=')
            tokens = map(lambda token: token.strip(), tokens)
            if not module_name_handled:
                module_name_handled = True
                tokens[0], tokens[1] = tokens[1], tokens[0]
            results.append(tuple(tokens))
        return results

    def _load_modules(self):
        '''
        找到所有已定义的modules，存放到_modules_map中
        :return:
        '''
        for index, line in enumerate(self._lines):
            if "module" in line:
                module_name = self._get_module_name(line)
                if not module_name:
                    continue
                if "endmodule" in line:
                    end_index = index + 1
                    subs_tuples = self._get_substitute(line)
                    self._module_substitute_map[module_name] = subs_tuples
                else:
                    end_index = self._find_end_index(index)
                self._module_map[module_name] = tuple([index, end_index])

    def _gen_subs_cmp(self):
        def compare(subs1, subs2):
            original1, substitute1 = subs1
            original2, substitute2 = subs2
            if substitute1 == original2:
                return 1
            if substitute2 == original1:
                return -1
            return 0
        return compare

    def _sort_substitute(self, subs):
        '''
        对substitute对进行排序，要达到的效果是每个替换不会影响到其他任意一个替换
        :param subs: [(original, substitute)]
        :return: None
        '''
        subs.sort(cmp=self._substitute_cmp)

    def _substitute(self, content, subs):
        '''
        把content中出现的所有的original替换成substitute
        :param content: string
        :param subs: [(original, substitute)]
        :return: 替换后的list of string
        '''
        result = []
        for line in content:
            for old, new in subs:
                line = line.replace(old, new)
            result.append(line)
        return result

    def rewrite(self):
        '''
        重写重命名的modules
        :return:
        '''
        to_extends = []
        to_removes = []
        for module_name, substitutes in self._module_substitute_map.items():
            begin_index, _ = self._module_map[module_name]
            to_removes.append(self._lines[begin_index])
            base_module_name = substitutes[0][0]
            if base_module_name in self._module_map.keys():
                base_begin_index, base_end_index = self._module_map[base_module_name]
                content = self._lines[base_begin_index:base_end_index]
                self._sort_substitute(substitutes)
                subs_content = self._substitute(content, substitutes)
                to_extends.append(subs_content)
        for to_remove in to_removes:
            self._lines.remove(to_remove)
        for to_extend in to_extends:
            self._lines.extend(to_extend)

    def get_content(self):
        return self._lines


def main():
    path = get_prism_model_dir() + get_sep() + "herman7.prism"
    helper = RenamingHelper(path)
    helper.rewrite()
    content = helper.get_content()
    for line in content:
        print line


if __name__ == "__main__":
    main()