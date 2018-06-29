from tkinter import *
import tkinter.filedialog, tkinter.messagebox
import os
from os import system

# the root window:
def Sticky():
    r = Tk()
    r.option_add('*font', '{Helvetica} 11')
    t = Text(r, bg = '#f9f3a9', wrap = 'word', undo = True)
    t.focus_set()
    t.pack(fill = 'both', expand = 1)
    r.geometry('220x235')
    r.title('Note')

    TextWidget(t) # pass along t, your Text

    m = tkinter.Menu(r)
    m.add_command(label="+", command=text.new_window)
    m.add_command(label="Save", command=text.save_file)
    m.add_command(label="Save As", command=text.save_file_as)
    m.add_command(label="Open", command=text.open_file)
    r.config(menu=m)

    r.mainloop()

# the text widget, and all of its functions:
class TextWidget:
    def __init__(self, text):
        self.text = text # pass the text widget
        self.filename = ''
        self._filetypes = [
        ('Text', '*.txt'),
            ('All files', '*'),
            ]

    def save_file(self, whatever = None):
        if (self.filename == ''):
            self.save_file_as()
        else:
            f = open(self.filename, 'w')
            f.write(self.text.get('1.0', 'end')) # change every 'self' that refers to the Text, to self.text
            f.close()
            tkinter.messagebox.showinfo('FYI', 'File Saved.')

    def save_file_as(self, whatever = None):
        self.filename = tkinter.filedialog.asksaveasfilename(defaultextension='.txt',
                                                             filetypes = self._filetypes)
        f = open(self.filename, 'w')
        f.write(self.text.get('1.0', 'end'))
        f.close()
        tkinter.messagebox.showinfo('FYI', 'File Saved')

    def open_file(self, whatever = None, filename = None):
        if not filename:
            self.filename = tkinter.filedialog.askopenfilename(filetypes = self._filetypes)
        else:
            self.filename = filename
        if not (self.filename == ''):
            f = open(self.filename, 'r')
            f2 = f.read()
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', f2)
            f.close()
            self.text.title('Sticky %s)' % self.filename)

    def new_window(self):
        Sticky()

    def help(whatever = None):
        tkinter.messagebox.showinfo('Help', message = '''
Help
''')


# make it so:
if __name__ == '__main__':
    Sticky()