# -*- coding:utf-8 -*-
from PathHelper import *


def parse_csv(file_path, parse_line1=False, default_type=float):
    ''':return '''
    results = []
    with open(file_path, "r") as f:
        is_line1 = True
        for l in f:
            if is_line1:
                num_cols = l.count(',') + 1
                for _ in range(num_cols):
                    results.append(list())
                is_line1 = False
                if not parse_line1:
                    continue

            _parse_line(l, results, data_type=default_type)
    return results


def _parse_line(line, results, sep=',', data_type=float):
    values = map(lambda v: v.strip(), line.split(sep))
    for index, value in enumerate(values):
        results[index].append(data_type(value))


def test():
    file_path = get_prism_model_dir() + get_sep() + "YEAR1_T_1_5_1"
    results = parse_csv(file_path)
    print results


if __name__ == "__main__":
    test()