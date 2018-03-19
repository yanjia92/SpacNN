# -*- coding: utf-8 -*-
import unittest
from model.ModelFactory import *
from model.ModuleFactory import *
from config.SPSConfig import SPSConfig
import logging

logger = logging.getLogger('testModel logger')
filehandler = logging.FileHandler('../log/testmodel.log', mode='w')
logger.addHandler(filehandler)
logger.setLevel(logging.INFO)

class Test(unittest.TestCase):
    def setUp(self):
        if not hasattr(self, 'model'):
            self.model = ModelFactory(ModuleFactory(SPSConfig())).spsmodel()
        self.paths = 120
        self.length = 730

    def testgeneratepath(self):
        for thickness in range(1, 2):
            self.model.constants['SCREEN_THICKNESS'].value = thickness
            paths = self.paths
            length = self.length
            # 生成paths条时间长度为length的随机路径
            for _ in range(paths):
                _, path = self.model.genRandomPath(length)
                logger.info('{0}, {1}'.format(thickness, path))



if __name__ == '__main__':
    unittest.main()
