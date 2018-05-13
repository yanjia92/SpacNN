# -*- coding: utf-8 -*-
import tkFileDialog
from Tkinter import END


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

    def init_comm_map(self):
        self.comm_map["open"] = self.open_file()





