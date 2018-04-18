# -*- coding: utf-8 -*-
def rmcomment(line):
    found = line.find(r"//")
    if found == -1:
        return line.strip()
    return line[:found].strip()



'''
remove the comment of _file
return the new file path that is already all-comments-removed
'''
def clear_comment(_file):
    new_lines = []
    with open(_file) as file:
        for line in file:
            if line == '\n':
                new_lines.append(line)
                continue
            new_line = rmcomment(line)
            if len(new_line) > 0:
                new_lines.append(new_line + "\n")
    point_idx = _file.rfind(".")
    result_file = _file[:point_idx] + "_temp." + _file[point_idx+1:]
    with open(result_file, 'w') as f:
        for l in new_lines:
            f.write(l)
    return result_file


def test_clear_comment():
    clear_comment("../../prism_model/smalltest.prism")

def testrmcomment():
    testcases = (
        ("abc; //abc", "abc;"),
        ("abc; ", "abc;"),
        ("int a = 1; // 这是一条注释", "int a = 1;"),
        ("// 这是一条注释", "")
    )

    for case in testcases:
        if rmcomment(case[0]) != case[1]:
            print case[0], case[1]

if __name__ == "__main__":
    test_clear_comment()


