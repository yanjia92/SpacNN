# -*- coding: utf-8 -*-
from ModelTestBase import ModelTestBase
from copy import copy, deepcopy


'''
测试Command对象的拷贝
'''

class CommandCopyTest(ModelTestBase):

    def setUp(self):
        ModelTestBase.setUp(self)

    def _get_model_name(self):
        return "queue_network"

    def testCopyCommand(self):
        route_cmds = self._model.get_commands("route")
        if route_cmds is None or not len(route_cmds):
            return
        cmd = route_cmds[0]
        cp_cmd = copy(cmd)
        cp_cmd.incr_hit_cnt()
        self.assertNotEqual(cmd.get_hit_cnt(), cp_cmd.get_hit_cnt())