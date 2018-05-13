# -*- coding: utf-8 -*-
import tkFileDialog
from Tkinter import END
from ui.testInputDialog import ParamInputDialog


class Director(object):

    def __init__(self, manager):
        self.manager = manager
        self.comm_map = {}
        self.init_comm_map()

    def open_file(self):
        def inner():
            filename = tkFileDialog.askopenfilename(title="Select your PRISM model")
            # print filename
            self.manager.read_model_file(filename)
            if hasattr(self, "root"):
                cw_text = self.root.children["cw_text"]
                with open(filename, "r") as f:
                    for l in f:
                        cw_text.insert(END, l)
        return inner

    def train(self):
        def inner():
            # get unsure params
            params_names = self.manager.unsure_param_names()
            # display dialog
            if not hasattr(self, "root"):
                print "Please add root to the Director. "
            vals_map = ParamInputDialog(self.root, "Specify parameters to train", params_names).show()
            print vals_map
        return inner

    def init_comm_map(self):
        self.comm_map["open"] = self.open_file()
        self.comm_map["train"] = self.train()





