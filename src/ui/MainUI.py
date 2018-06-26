# -*- coding: utf-8 -*-
from Tkinter import *
from manager.Manager import Manager
from director.Director import Director
from ui.CodeWindow import CodeWindow

'''
设计思路: 一个dict维护从command_name到command的映射
'''


def add_file_menu(f):
    def wrapper(*args, **kwargs):
        comm_map = args[0].comm_map
        menu_bar = f(*args, **kwargs)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=comm_map["open"])
        menu_bar.add_cascade(label="Model", menu=file_menu)
        return menu_bar
    return wrapper


def add_option_menu(f):
    def wrapper(*args, **kwargs):
        comm_map = args[0].comm_map
        menu_bar = f(*args, **kwargs)

        option_menu = Menu(menu_bar, tearoff=0)
        option_menu.add_command(label="Option", command=comm_map["option"])
        menu_bar.add_cascade(label="Option", menu=option_menu)
        return menu_bar
    return wrapper


class UIOperator(object):
    def __init__(self, comm_map):
        self.comm_map = comm_map
        self.root = Tk()
        self.root.title("SpacNN")
        self.frame_width = 800
        self.frame_height = 1000
        self.root.geometry("{}x{}".format(self.frame_width, self.frame_height))
        self.root.config(menu=self._get_menu_bar())
        lcode_window = Label(self.root, text="Model")
        lcode_window.pack()
        self._add_code_window()
        # print self.root.children.keys()
        lLTL = Label(self.root, text="LTL formula for the path")
        lLTL.pack()
        var_LTL = StringVar()
        eLTL = Entry(self.root, textvariable=var_LTL, name="eLTL")
        # eLTL.bind("<Return>", self.comm_map["ltl_input"])
        # self.root.bind_class("Entry", "<FocusOut>", self.comm_map["ltl_input"])
        eLTL.pack()

        # buttons
        train_button = Button(self.root, text="train", command=self.comm_map["train"])
        train_button.pack()
        predict_button = Button(self.root, text="predict", command=self.comm_map["predict"])
        predict_button.pack()

        # children = self.root.winfo_children()
        # print children

    @add_option_menu
    @add_file_menu
    def _get_menu_bar(self):
         return Menu(self.root, name="menu")

    def _add_code_window(self):
        CodeWindow(self.root)

    def start_ui_loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    manager = Manager()
    director = Director(manager)
    ui_operator = UIOperator(director.comm_map)
    director.root = ui_operator.root
    ui_operator.start_ui_loop()
