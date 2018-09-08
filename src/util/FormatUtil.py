# -*- coding:utf-8 -*-


def str2num(val):
    '''
    将一个代表字符串转化为数字
    :param val: number in str
    :return: number
    '''
    if isinstance(val, str):
        result = None
        try:
            if val.index('.') != -1:
                result = float(val)
            elif val.isdigit():
                result = int(val)
        except ValueError,e:
            raise Exception("Invalid parameter passed to str2num: {}".format(val))
        if result is None:
            raise Exception("Invalid parameter passed to str2num: {}".format(val))
        return result
    else:
        if isinstance(val, int) or isinstance(val, float):
            return val


