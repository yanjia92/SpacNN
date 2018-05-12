# -*- coding: utf-8 -*-
from Tkinter import *
from manager.Manager import Manager
from director.Director import Director

'''
设计思路: 一个dict维护从command_name到command的映射
'''

def add_file_menu(f):
    def wrapper(*args):
        comm_map = args[0].comm_map
        menu_bar = f(*args)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=comm_map["open"])
        menu_bar.add_cascade(label="Model", menu=file_menu)
        return menu_bar
    return wrapper


class UIOperator(object):
    def __init__(self, comm_map):
        self.comm_map = comm_map
        self.root = Tk()
        self.root.title("SpacNN")
        self.root.geometry("600x800")
        self.root.config(menu=self._get_menu_bar())

    @add_file_menu
    def _get_menu_bar(self):
         return Menu(self.root)

    def start_ui_loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    manager = Manager()
    director = Director(manager)
    ui_operator = UIOperator(director.comm_map)
    ui_operator.start_ui_loop()