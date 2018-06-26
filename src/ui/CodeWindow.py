from Tkinter import *


class CodeWindow:
    def __init__(self, root):
        '''a fixed size scrollable text widget'''
        # frame = Frame(root)
        # frame.pack()
        self.textPad(root)

        return

    def textPad(self, root):
        # scroll = Scrollbar(master, borderwidth=1, name="cw_scroll")
        # scroll.pack(side=TOP, fill=X)

        # self.text = Text(master, {"name": "cw_text"})
        # self.text.configure(yscrollcommand=scroll.set)
        # scroll.config(command=self.text.yview)
        # self.text.pack(side=TOP, fill=X)
           
        # return
        self.scrollbar = Scrollbar(root)
        self.text = Text(root, {"name": "cw_text"})
        self.scrollbar.pack(side=RIGHT, fill=X)
        self.text.pack(side=TOP, fill=X)
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set, state=NORMAL)

        return

    def insert(self, index, chars, *args):
        self.text.insert(index, chars, *args)

    def clear(self):
        self.text.delete('1.0', END)





# from Tkinter import *
#
#
# class scrollTxtArea:
#     def __init__(self, root):
#         frame = Frame(root)
#         frame.pack(fill=X)
#         self.textPad(frame)
#         return
#
#     def textPad(self, frame):
#         # add a frame and put a text area into it
#         textPad = Frame(frame)
#         self.text = Text(textPad, height=30, width=90)
#
#         # add a vertical scroll bar to the text area
#         scroll = Scrollbar(textPad)
#         self.text.configure(yscrollcommand=scroll.set)
#
#         # pack everything
#         self.text.pack(side=LEFT)
#         scroll.pack(side=RIGHT, fill=Y)
#         textPad.pack(side=TOP)
#         return
#
#
# def main():
#     root = Tk()
#     foo = scrollTxtArea(root)
#     root.title('TextPad With a Vertical Scroll Bar')
#     root.mainloop()
#
#
# main()
