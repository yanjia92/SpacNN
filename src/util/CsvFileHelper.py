# -*- coding:utf-8 -*-
from SystemUtil import on_windows_platform
from os.path import exists, isfile


def write_csv_rows(file_path, datas, headers=None, sep=",", transformer=None):
    '''
    :param file_path:
    :param datas: list of list
    :param headers: list of string
    :param sep: separator
    :param transformer: transform(row_data)
    :return: None
    '''
    # validate file_path and datas
    # validation includes: all data rows should be same length
    # header's length should be same with data's row
    with open(file_path, "w") as f:
        if headers:
            header_line = sep.join(headers)
            f.write(header_line)
            if on_windows_platform():
                f.write("\r\n")
            else:
                f.write("\n")
        for data in datas:
            if transformer:
                transformer(data)
            try:
                # try not to write isinstance or type in python
                # see https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
                data = map(str, data)
                f.write(sep.join(data))
            except TypeError:
                # not iterable, e.g. not a tuple or list
                f.write(str(data))
            if on_windows_platform():
                f.write("\r\n")
            else:
                f.write("\n")


def parse_csv_cols(file_path, types=float, has_headers=True, sep=','):
    '''
    :return [[col]]
    '''
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


def parse_csv_rows(path, types=float, has_headers=True, sep=','):
    '''
    parse csv file row by row
    :param path: path to csv file
    :param types: single type or type list
    :param has_headers: False or True
    :param sep: separator
    :return: list of list
    '''
    results = []
    if not exists(path) or not isfile(path):
        raise Exception("path not exist when parsing file: {}".format(path))
    with open(path, "r") as f:
        is_first_line = True
        for _line in f:
            if is_first_line and has_headers:
                is_first_line = False
                continue
            results.append(_parse_line_row(_line, types, sep))
    return results


def _parse_line_row(line, types, sep=','):
    row = []
    values = map(lambda v: v.strip(), line.split(sep))
    if values and len(values) == 1:
        t = types
        if isinstance(types, list):
            t = types[0]
        return t(values[0])
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
    datas = parse_csv_rows(write_to, [int])
    print datas


if __name__ == "__main__":
    # test()
    test_write()
