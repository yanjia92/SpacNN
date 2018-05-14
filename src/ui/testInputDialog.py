# import tkinter as tk
#
# root=tk.Tk() # this will create the window
#
# def get_value():
#
#     fpoint=int(entry1.get()) # Gets point 1
#     lpoint=int(entry2.get()) # Gets point 2
#     points=[fpoint,lpoint]
#
#     ####### MODIFY A VARIABLE IN PARENT #######
#     root.geometry(entry1.get() + "x" + entry2.get())
#
# box1=tk.Label(root, text="First point")  # Label of box 1
# entry1=tk.Entry(root)                    # Box 1
#
# box2=tk.Label(root, text="Last point")   # Label of box 2
# entry2=tk.Entry(root)                    # box 2
#
# Done_button=tk.Button(root, name="done") #Button to terminate the "gui"
#
# ####### Configuring the button to call a function when pressed  #######
# Done_button.configure(command=get_value)
# #Done_button.bind("<Button-1>",get_value) # Run function "get_value" on click
# box1.grid(row=1, sticky="W",padx=4)             # position of label for box1
# entry1.grid(row=1,column=1,sticky="E", pady=4)  # position of box 1
# box2.grid(row=2, sticky="W",padx=4)             # position of label for box2
# entry2.grid(row=2,column=1,sticky="E", pady=4)  # position of box2
# Done_button.grid(row=3,column=1)                # position of "button
#
#
#
# root.mainloop()

import Tkinter as tk
from collections import OrderedDict

class MyDialog(object):
    def __init__(self, parent, prompt):
        self.toplevel = tk.Toplevel(parent)
        self.var = tk.StringVar()
        label = tk.Label(self.toplevel, text=prompt)
        entry = tk.Entry(self.toplevel, width=40, textvariable=self.var)
        button = tk.Button(self.toplevel, text="OK", command=self.toplevel.destroy)

        label.pack(side="top", fill="x")
        entry.pack(side="top", fill="x")
        button.pack(side="bottom", anchor="e", padx=4, pady=4)

    def show(self):
        self.toplevel.grab_set()
        self.toplevel.wait_window()
        value = self.var.get()
        return value


class ParamInputDialog(object):
    def __init__(self, parent, prompt, param_names):
        self.toplevel = tk.Toplevel(parent)
        lprompt = tk.Label(self.toplevel, text=prompt)
        lprompt.pack(side="top", fill="x")
        self.vars_map = OrderedDict()  # name : [begin_val, step_val, end_val]
        for name in param_names:
            self._add_le(name, self.toplevel)
        button = tk.Button(self.toplevel, text="Finish", command=self.toplevel.destroy)
        button.pack(side="bottom", anchor="e", padx=4, pady=4)

    def _add_le(self, name, toplevel):
        self.vars_map[name] = list()
        '''add label entry for each parameter'''
        lname = tk.Label(toplevel, text=name)
        lbeginvalue = tk.Label(toplevel, text="Begin Value")
        varbeginvalue = tk.DoubleVar()
        ebeginvalue = tk.Entry(toplevel, textvariable=varbeginvalue)
        self.vars_map[name].append(varbeginvalue)
        lstep = tk.Label(toplevel, text="Step")
        varstep = tk.DoubleVar()
        estep = tk.Entry(toplevel, textvariable=varstep)
        self.vars_map[name].append(varstep)
        lendvalue = tk.Label(toplevel, text="End Value")
        varendvalue = tk.DoubleVar()
        eendvalue = tk.Entry(toplevel, textvariable=varendvalue)
        self.vars_map[name].append(varendvalue)

        lname.pack(side="top", fill="x")
        lbeginvalue.pack(side="top", fill="x")
        ebeginvalue.pack(side="top", fill="x")
        lstep.pack(side="top", fill="x")
        estep.pack(side="top", fill="x")
        lendvalue.pack(side="top", fill="x")
        eendvalue.pack(side="top", fill="x")

    def show(self):
        self.toplevel.grab_set()
        self.toplevel.wait_window()

        for name, var_list in self.vars_map.items():
            val_list = map(lambda var: var.get(), var_list)
            self.vars_map[name] = val_list
        return self.vars_map

class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.button = tk.Button(self, text="Click me!", command=self.on_click)
        self.label = tk.Label(self, text="", width=40)
        self.label.pack(side="top", fill="x")
        self.button.pack(padx=20, pady=20)

    def on_click(self):
        # result = MyDialog(self, "Enter your name:").show()
        names = ["name1", "name2"]
        result = ParamInputDialog(self, "Specify these parameters to train the model", names).show()
        self.label.configure(text="your result: '%s'" % result)

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()