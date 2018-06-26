# -*- coding:utf-8 -*-
from PathHelper import *


def parse_csv_cols(file_path, types, has_headers=True, sep=','):
    ''':return [[col]]'''
    data_rows = parse_csv_rows(file_path, types, has_headers, sep)
    return _as_cols(data_rows)


def _as_cols(data_matrix):
    if len(data_matrix) == 0:
        return []
    lens = map(lambda l: len(l), data_matrix)
    assert sum(map(lambda v: v-lens[0], lens)) == 0
    datas = []
    for data_tuple in zip(*data_matrix):
        datas.append(data_tuple)
    return datas


def parse_csv_rows(path, types, has_headers=True, sep=','):
    ''':return [[row]]'''
    results = []
    with open(path, "r") as f:
        first_line = True
        for _line in f:
            if first_line and has_headers:
                first_line = False
                continue
            results.append(_parse_line_row(_line, types, sep))
    return results


def _parse_line_row(line, types, sep=','):
    row = []
    values = map(lambda v: v.strip(), line.split(sep))
    if not isinstance(types, list):
        types = [types] * len(values)
    for (val, type) in zip(values, types):
        row.append(type(val))
    return row


def _parse_line(line, results, sep=',', data_type=float):
    values = map(lambda v: v.strip(), line.split(sep))
    for index, value in enumerate(values):
        results[index].append(data_type(value))


def test():
    file_path = get_prism_model_dir() + get_sep() + "YEAR1_T_1_5_1"
    results = parse_csv_rows(file_path, float)
    print results


if __name__ == "__main__":
    test()
