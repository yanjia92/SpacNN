from Tkinter import *
from ModifiedAwareText import ModifiedAwareText


class CodeWindow:
    def __init__(self, root, director):
        '''a fixed size scrollable text widget'''
        self.director = director
        self.scrollbar = None
        self.text = None
        self.text_pad(root)
        self.var = None

    def text_pad(self, root):
        self.scrollbar = Scrollbar(root)
        self.text = ModifiedAwareText(root, {"name": "cw_text"})
        self.text.register_modified_handler(self.director.comm_map["on_model_edited"])
        self.scrollbar.pack(side=RIGHT, fill=X)
        self.text.pack(side=TOP, fill=X)
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set, state=NORMAL)

    def insert(self, index, chars, *args):
        self.text.insert(index, chars, *args)

    def clear(self):
        self.text.delete('1.0', END)
