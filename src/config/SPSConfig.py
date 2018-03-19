# -*- coding:utf-8 -*-
from module.Module import Constant

class SPSConfig(object):
    def __init__(self):
        self.params = {}
        self.params['SB_K'] = Constant('SB_K', 0.0039)
        self.params['SB_B'] = Constant('SB_B', 12)
        self.params['SB_P_THRESHOLD'] = Constant('SB_P_THRESHOLD', 0.7)
        self.params['SB_A_MU'] = Constant('SB_A_MU', 0.1754)
        self.params['SB_A_SIGMA'] = Constant('SB_A_SIGMA', 0.02319029 * 21)
        self.params['S3R_K'] = Constant('S3R_K', 200.5 / 3.0)  # s3r, bdr, bcr三个模块均摊电离能损
        self.params['S3R_DELTAV_THRESHOLD'] = Constant('S3R_DELTAV_THRESHOLD', 450)
        self.params['S3R_A_MU'] = Constant('S3R_A_MU', 570.8 * 18 - 570.8 * 5)
        self.params['S3R_A_SIGMA'] = Constant('S3R_A_SIGMA', 6.7471 * 120)
        self.params['S3R_B'] = Constant('S3R_B', 0.01731)
        self.params['SCREEN_THICKNESS'] = Constant('SCREEN_THICKNESS', 1)
        self.params['DURATION_IN_DAY'] = Constant('DURATION_IN_DAY', 365)

    def getParam(self, name):
        if name in self.params.keys():
            return self.params[name]
        else:
            raise Exception('no parameter found: {0}'.format(name))


