from Tkinter import *

master = Tk()

scrollbar = Scrollbar(master)
scrollbar.pack(side=TOP, fill=X)

listbox = Listbox(master, yscrollcommand=scrollbar.set)
for i in range(1000):
    listbox.insert(END, str(i))
listbox.pack(side=TOP, fill=X)

scrollbar.config(command=listbox.yview)

mainloop()