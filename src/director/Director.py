# -*- coding: utf-8 -*-
import tkFileDialog
from ui.testInputDialog import ParamInputDialog
import tkMessageBox
from util.util import *
from itertools import product
from ui.testInputDialog import ManagerParamInputDialog
from Tkinter import *
from util.CsvFileHelper import write_csv_rows
from tkMessageBox import showinfo
from util.FileHelper import write_2_file
from LTLHelper import LTLHelper
from util.CsvFileHelper import parse_csv_cols
import logging


class Director(object):

    def __init__(self, manager):
        self.manager = manager
        self.comm_map = {}
        self.init_comm_map()
        self.widget_var_map = {}
        self.model_edited = False
        self.model_opened = False
        self.prism_true_datas = []
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def open_file(self):
        def inner():
            self.model_opened = False
            filename = tkFileDialog.askopenfilename(
                title="Select your PRISM model")
            var = self.widget_var_map["model_file_path"]
            if var:
                var.set(filename)
            self.manager.read_model_file(filename)
            if hasattr(self, "root"):
                cw_text = self.root.children["cw_text"]
                # cw_text.clear()
                cw_text.delete("1.0", END)
                with open(filename, "r") as f:
                    for l in f:
                        cw_text.insert(END, l)
            self.model_opened = True
        return inner

    def _input_unsure_params(self, names):
        ''':return {name: values_list}'''
        if not hasattr(self, "root"):
            print "Please add root to the Director. "
        vals_map = ParamInputDialog(self.root, "Specify parameters to train",
                                    names).show()  # name: [begin, step, end]
        for name, vlist in vals_map.items():
            begin, end, step = vlist
            vals_map[name] = interval(begin, end, step)
        return vals_map

    def train(self):
        def inner():
            if not hasattr(self, "root"):
                self.logger.error("root not attached to Director instance")
                return
            for widget in self.root.pack_slaves():
                if isinstance(widget, Entry) and widget._name == "eLTL":
                    strLTL = widget.get()
                    parsed_ltl = self.manager.ltl_parser.parse_line(strLTL)
                    self.manager.set_model_duration(LTLHelper.get_duration(parsed_ltl))
                    result = self.manager.set_ltl(parsed_ltl)
                    if not result:
                        tkMessageBox.showerror("Error", "ltl 设置错误")
                    break
            # get unsure params
            params_names = self.manager.unsure_param_names()
            # show dialog for user to input
            vals_map = self._input_unsure_params(
                params_names)
            self.manager.set_train_constants(*vals_map.items())
            self.manager.train_network()
            print "Train finished"
        return inner

    def ltl_input(self):
        def inner(event=None):
            strLTL = event.widget.get()
            parsed_ltl = self.manager.ltl_parser.parse_line(strLTL)
            result = self.manager.set_ltl(parsed_ltl)
            if result:
                # ltl set
                tkMessageBox.showinfo("Info", "LTL公式已设定")
            else:
                tkMessageBox.showerror(
                    "Error", "Open a .prism model before setting LTL")
        return inner

    def predict(self):
        def inner():
            unsure_names = self.manager.unsure_param_names()
            if len(unsure_names) == 0:
                tkMessageBox.showerror(
                    "Your model contains no unsure parameters.")
                return
            vals_map = self._input_unsure_params(
                unsure_names)
            test_xs = [test_x for test_x in product(*vals_map.values())]
            self.manager.set_test_xs(test_xs)

            test_ys = self.manager.run_test()
            self.manager.save_predict_results(test_xs, test_ys)
            if len(self.prism_true_datas) > 0:
                error = self._mse(test_ys, self.prism_true_datas[1])
                if error:
                    print "predict mse: {}".format(error)
            self.manager.plot_expr_datas(test_xs, test_ys)
        return inner

    def option(self):
        def inner():
            if not hasattr(self, "root"):
                print "Error in Director. Specify ui root to Director"
            custom_options = ManagerParamInputDialog(
                self.root, "custom options", self.manager.manager_params).show()
            self.manager.manager_params.update(custom_options)
        return inner

    def save(self):
        '''
        write model back to file system and rm * from file path
        :return: None
        '''
        def inner(event):
            print "save key event caught."
            if self.model_edited:
                widget = event.widget
                model_content = widget.get("1.0", END)
                path_var = self.widget_var_map["model_file_path"]
                path = path_var.get()
                # rm * from path
                if path[-1] == "*":
                    path = path[:-1]
                    path_var.set(path)
                # save to file system
                write_2_file(model_content, path)
                self.model_edited = False
        return inner

    def menu_save(self, widget):
        '''
        menu save的command
        :param widget: label widget for file path
        :return: None
        '''
        def inner():
            if widget:
                model_content = widget.get("1.0", END)
                path_var = self.widget_var_map["model_file_path"]
                path = path_var.get()
                # rm * from path
                if path[-1] == "*":
                    path = path[:-1]
                    path_var.set(path)
                # save to file system
                write_2_file(model_content, path)
                self.model_edited = False
        return inner

    def export(self):
        def inner():
            export_to = tkFileDialog.asksaveasfilename(
                title="export result to")
            xs = self.manager.predict_xs
            ys = self.manager.predict_ys
            datas = []
            for index, y in enumerate(ys):
                row = list(xs[index])
                row.append(y)
                datas.append(row)
            param_names = list(self.manager.unsure_param_names())
            param_names.append("result")
            written = write_csv_rows(export_to, datas, param_names)
            if written == len(datas):
                showinfo("Info", "Result exported to {}".format(export_to))
        return inner

    def help(self):
        def inner():
            help_text = """
                                    Spacc使用说明
            1. 打开模型
            使用菜单: Model -> Open 打开一个以prism作为后缀的模型文件,模型文件的语法采用PRISM模型语言一样的语法,用户可以直接使用PRISM软件的模型文件.
            2. 设定LTL公式
            用户可以在LTL输入框内输入模型应该满足的LTL公式,LTL公式的语法和PRISM语言支持的保持一致.
            3. 进行训练
            软件假设用户打开的模型文件中包含不确定参数,此时软件可以针对此模型进行训练.点击Train按钮,软件展示出非确定参数录入对话框,用户可以输入每个参数的起始值,结束值以及步长值,点击Finish即可开始训练.
            4. 进行预测
            点击Predict按钮即可进行预测.软件会根据训练的结果对模型在未知参数下的模型预测,并会画出模型在不同参数下满足LTL性质的曲线图.
            5. 导出结果
            用户可以点击Export按钮导出预测结果
            """
            tkMessageBox.showinfo("help", help_text)
        return inner

    def register_widget_var(self, key, variable):
        """将一个widget对应的变量注册到map"""
        if key in self.widget_var_map.keys():
            # todo system level logger
            print "Error: key {} has been registered in Director object. ".format(key)
            return
        self.widget_var_map[key] = variable

    def _get_widget_var(self, key):
        '''
        获取通过UIOperator注册的widget对应的variable
        :return: variable
        '''
        if key not in self.widget_var_map.keys():
            # todo add system level logger
            print "Error key {} not exist in Director.widget_var_map"
            return
        return self.widget_var_map[key]

    def on_model_edited(self):
        '''
        append * to file path when file is edited.
        :return: None
        '''
        def inner(event):
            if self.model_edited or (not self.model_opened):
                return
            file_path_var = self._get_widget_var("model_file_path")
            if file_path_var:
                path = file_path_var.get()
                path += "*"
                file_path_var.set(path)
            self.model_edited = True
        return inner

    def on_adding_prism_true_data(self):
        def inner():
            path = tkFileDialog.askopenfilename(title="Select your true data from PRISM")
            self.prism_true_datas = parse_csv_cols(path, float)
            print "PRISM true data added. "
        return inner

    def init_comm_map(self):
        self.comm_map["open"] = self.open_file()
        self.comm_map["train"] = self.train()
        self.comm_map["ltl_input"] = self.ltl_input()
        self.comm_map["predict"] = self.predict()
        self.comm_map["option"] = self.option()
        self.comm_map["save"] = self.save()
        self.comm_map["export"] = self.export()
        self.comm_map["help"] = self.help()
        self.comm_map["on_model_edited"] = self.on_model_edited()
        self.comm_map["menu_save"] = self.menu_save
        self.comm_map["atdfp"] = self.on_adding_prism_true_data()

    def _mse(self, y1s, y2s):
        '''
        compute the mean square error of y1 and y2
        :param y1: list of datas
        :param y2: list of datas
        :return:
        '''
        if len(y1s) == 0 or len(y2s) == 0:
            return
        if len(y1s) != len(y2s):
            return
        temp = [(v1 - v2) ** 2 for (v1, v2) in zip(y1s, y2s)]
        return sum(temp) / len(temp)

