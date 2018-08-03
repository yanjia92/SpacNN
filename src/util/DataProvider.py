# -*- coding: utf-8 -*-
from CsvFileHelper import parse_csv_rows
import logging
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def data_from_csv(path):
    '''
    从csv文件中加载数据
    :param path:
    :return: numpy.ndarray
    '''
    rows = parse_csv_rows(path, float)
    if rows and len(rows) <= 0:
        return np.array([]), np.array([])
    if len(rows[0]) < 2:
        logger.error("{} is not a valid csv file for providing data. It must contain at least one x and one y column", path)
        return np.array([]), np.array([])
    temp_xs = [row[:-1] for row in rows]
    temp_ys = [row[-1] for row in rows]
    xs = np.array(temp_xs)
    ys = np.array(temp_ys)
    return xs, ys


def test():
    path = "/Users/bitbook/Documents/FunctionRegressionProj/data/Q_TRIGGER_1_20_1.csv"
    xs, ys = data_from_csv(path)
    logger.debug("xs: %s, ys: %s", str(xs.tolist()), str(ys.tolist()))


if __name__ == "__main__":
    test()