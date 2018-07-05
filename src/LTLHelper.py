# -*- coding:utf-8 -*-


class LTLHelper(object):

    @classmethod
    def get_duration(cls, parsed_ltl):
        '''
        解析parsed_ltl中的duration,即 U[0, num]中的num
        目前ltl_parser不支持interval until的解析
        :param parsed_ltl: parsed_ltl
        :return: duration in str
        '''
        for token in parsed_ltl:
            if token.startswith("U"):
                # U[1, 20]
                str_duration = token.split(",")[1][:-1]
                return str_duration.strip()
        print "Not a until formula"
        return None

