# -*- coding:utf-8 -*-

def str2num(val):
    '''
    将一个代表字符串转化为数字
    :param val: number in str
    :return: number
    '''
    try:
        if '.' in val:
            result = float(val)
        else:
            result = int(val)
    except ValueError,e:
        print "input({}) is not a number in string".format(val)
        return None
    return result



