# -*- coding:utf-8 -*-


class StringUtil(object):

    num_set = set([str(item) for item in range(10)])
    num_set.add(".")

    @classmethod
    def isnum(cls, value):
        if value is None or not isinstance(value, str):
            return False

        value_set = set(value)
        return value_set.issubset(cls.num_set)


