# -*- coding: utf-8 -*-
from module.Module import *
from util.MathUtils import *
from util.util import *
from model.ModuleFactory import ModuleFactory
from config.SPSConfig import SPSConfig
import unittest


class TestCase(unittest.TestCase):
    def setUp(self):
        self.config = SPSConfig()

    def testExport2PRISM(self):
        prismfileaddr = "/Users/bitbook/Documents/PostGradCourses/docrepo/hkht/NN/proj/prism_model/SYS.prism"
        self.config.export2prism(prismfileaddr)



if __name__ == "__main__":
    unittest.main()