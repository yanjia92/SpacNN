# -*- coding:utf-8 -*-
import unittest
from compiler.LTLParser import LTLParser
from util.StringUtil import StringUtil


class Test(unittest.TestCase):
    def setUp(self):
        self.ltls = []
        self.ltls.append("true U<= 10 failure")
        self.ltls.append("true U<=10 failure")
        self.ltls.append("true U<= 10.2 failure")
        self.parser = LTLParser().build_parser()

    def _get_duration(self, parsed_ltl):
        '''
        从解析后的ltl公式中获取duration,即U后面的数字
        :param parsed_ltl:
        :return: duration_in_str
        '''
        for token in parsed_ltl:
            if token.startswith("U"):
                # U[1, 20]
                str_duration = token.split(",")[1][:-1]
                return str_duration.strip()
        print "Not a until formula"
        return None

    def test_parse_until_duration(self):
        '''
        验证parser能够正确解析出duration
        :return:
        '''
        parser = self.parser
        for ltl in self.ltls:
            parsed_ltl = parser.parse_line(ltl)
            str_duration = self._get_duration(parsed_ltl)
            self.assertTrue(
                StringUtil.isnum(str_duration),
                "parsed_ltl:{}, str_duration:{}".format(
                    parsed_ltl,
                    str_duration))
