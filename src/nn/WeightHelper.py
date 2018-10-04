# -*- coding:utf-8 -*-
from util.Geometry import aver_distance


class WeightHelper(object):
    '''
    计算训练数据的可靠性权重
    '''
    weight_threshold = 1.0e-2

    @classmethod
    def weight(cls, xs, ys):
        '''
        计算分段权值
        :param xs:
        :param ys:
        :return:
        '''
        distance = aver_distance(xs, ys)
        if distance < cls.weight_threshold:
            return [0.0 for _ in xs]
        weights = [1.0 / distance**2 for _ in xs]
        return weights
