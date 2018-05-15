# -*- coding: utf-8 -*-
import tkFileDialog
from Tkinter import END
from ui.testInputDialog import ParamInputDialog
import tkMessageBox
from util.util import *
from itertools import product
from PathHelper import *


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

    def _input_unsure_params(self, names):
        ''':return {name: values_list}'''
        if len(names) == 0:
            tkMessageBox.showerror("Error", "Open a .prism model or your model contains no unsure parameters. ")
            return
            # display dialog
        if not hasattr(self, "root"):
            print "Please add root to the Director. "
        vals_map = ParamInputDialog(self.root, "Specify parameters to train",
                                    names).show()  # name: [begin, step, end]
        for name, vlist in vals_map.items():
            begin, step, end = vlist
            vals_map[name] = interval(begin, end, step)
        return vals_map

    def train(self):
        def inner():
            # get unsure params
            params_names = self.manager.unsure_param_names()
            vals_map = self._input_unsure_params(params_names)  # show dialog for user to input
            self.manager.set_train_constants(*vals_map.items())
            self.manager.train_network()
            print "Train finished"

        return inner

    def ltl_input(self):
        def inner(event=None):
            strLTL = event.widget.get()
            ltl = [token.lstrip() for token in strLTL.split(',')]
            result = self.manager.set_ltl(ltl)
            if result:
                # ltl set
                tkMessageBox.showinfo("Info", "LTL公式已设定")
            else:
                tkMessageBox.showerror("Error", "Open a .prism model before setting LTL")
        return inner

    def predict(self):
        def inner():
            #  get unsure parameter names
            unsure_names = self.manager.unsure_param_names()
            vals_map = self._input_unsure_params(unsure_names)  # show dialog for user to input
            # self.manager.set_test_x(vals_map.values())
            test_xs = [test_x for test_x in product(*vals_map.values())]
            self.manager.set_test_xs(test_xs)
            # self.manager.run_test(prism_data="C:\\Users\\yanjia\\Documents\\proj\\SpacNN\\prism_model\\YEAR1_T_1_10_1")
            # self.manager.run_test()
            self.manager.run_test(prism_data=get_prism_model_dir() + get_sep() + "YEAR1_T_1_10_1")
        return inner

    def init_comm_map(self):
        self.comm_map["open"] = self.open_file()
        self.comm_map["train"] = self.train()
        self.comm_map["ltl_input"] = self.ltl_input()
        self.comm_map["predict"] = self.predict()





