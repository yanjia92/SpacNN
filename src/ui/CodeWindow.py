from Tkinter import *


class CodeWindow:
    def __init__(self, root, director):
        '''a fixed size scrollable text widget'''
        self.scrollbar = None
        self.text = None
        self.text_pad(root)
        self.director = director
        self.var = None

    def text_pad(self, root):
        self.scrollbar = Scrollbar(root)
        self.var = StringVar()
        self.var.trace("w", self.director.comm_map["on_model_edited"])
        self.text = Text(root, {"name": "cw_text", "textvariable": self.var})
        self.director.register_widget_var("model_content", self.var)
        self.scrollbar.pack(side=RIGHT, fill=X)
        self.text.pack(side=TOP, fill=X)
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set, state=NORMAL)

    def insert(self, index, chars, *args):
        self.text.insert(index, chars, *args)

    def clear(self):
        self.text.delete('1.0', END)
