# -*- coding:utf-8 -*-


class AntitheticStepMixin(object):
    '''
    Interface containing methods that a step must implement for generating antithetic path
    '''

    def get_command(self):
        '''
        return the choosed command of this step
        :return:
        '''
        pass

    def get_seed(self):
        '''
        return the random number used for generating next state
        :return:
        '''
        pass

