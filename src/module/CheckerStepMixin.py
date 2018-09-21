# -*- coding:utf-8 -*-
# interface methods of Step class used in Checker class


class CheckerStepMixin(object):
    def get_ap_set(self):
        '''
        获取当前状态对应的ap
        :return:  a set containing all the aps of the state this Step instance holds
        '''
        pass

    def get_passed_time(self):
        '''
        获取到当前Step时系统已经运行的时间
        :return: float
        '''
        pass

    def get_holding_time(self):
        '''
        获取当前Step的延时
        :return: float
        '''
        pass
