# -*- coding: utf-8 -*-
import tkFileDialog


class Director(object):

    def __init__(self, manager):
        self.manager = manager
        self.comm_map = {}
        self.init_comm_map()

    def open_file(self):
        def inner():
            filename = tkFileDialog.askopenfilename(title="Select your PRISM model")
            print filename
            self.manager.read_model_file(filename)
        return inner

    def init_comm_map(self):
        self.comm_map["open"] = self.open_file()





