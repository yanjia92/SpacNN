# -*- coding:utf-8 -*-
import copy


def shallow_cpy(l):
    # 对数组中的每个元素进行牵拷贝
    return [copy.copy(elem) for elem in l]

