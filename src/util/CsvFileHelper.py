# -*- coding:utf-8 -*-
from SystemUtil import on_windows_platform


def write_csv_rows(file_path, datas, headers=None, sep=","):
    assert len(datas) > 0
    lens = map(len, datas)
    assert len(set(lens)) == 1
    if headers:
        assert len(headers) == len(datas[0])
    with open(file_path, "w") as f:
        if headers:
            header_line = sep.join(headers)
            f.write(header_line)
            if on_windows_platform():
                f.write("\r\n")
            else:
                f.write("\n")
        for data in datas:
            data = map(str, data)
            f.write(sep.join(data))
            if on_windows_platform():
                f.write("\r\n")
            else:
                f.write("\n")
    return len(datas)


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


def test_write():
    write_to = "/Users/bitbook/Documents/temp.csv"
    datas = []
    for _ in range(3):
        datas.append(tuple(range(3)))
    headers = ["col1", "col2", "col3"]
    write_csv_rows(write_to, datas, headers)


if __name__ == "__main__":
    # test()
    test_write()
