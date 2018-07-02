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


class ManagerParamInputDialog(object):
    def __init__(self, parent, prompt, params_map):
        self.toplevel = tk.Toplevel(parent)
        self.params_map = params_map
        # add prompt label
        lprompt = tk.Label(self.toplevel, text=prompt)
        lprompt.pack(side="top", fill="x")
        self.vars_map = dict()
        for name, value in self.params_map.items():
            self._add_le(name, value)
        button = tk.Button(self.toplevel, text="Finish", command=self.toplevel.destroy)
        button.pack(side="bottom", anchor="e", padx=4, pady=4)

    def _add_le(self, name, value):
        lname = tk.Label(self.toplevel, text=name)
        varvalue = tk.DoubleVar(value=value)
        evalue = tk.Entry(self.toplevel, textvariable=varvalue)
        self.vars_map[name] = varvalue
        lname.pack(side="top", fill="x")
        evalue.pack(side="top", fill="x")

    def show(self):
        self.toplevel.grab_set()
        self.toplevel.wait_window()

        for name, var in self.vars_map.items():
            self.vars_map[name] = var.get()
        return self.vars_map


class ParamInputDialog(object):
    # param input dialog
    # every param must have [start, end, step] value
    def __init__(self, parent, prompt, param_names):
        self.toplevel = tk.Toplevel(parent)
        lprompt = tk.Label(self.toplevel, text=prompt)
        lprompt.pack(side="top", fill="x")
        self.vars_map = OrderedDict()  # name : [begin_val, step_val, end_val]
        for name in param_names:
            self._input_param(name, self.toplevel)
        button = tk.Button(self.toplevel, text="Finish", command=self.toplevel.destroy)
        button.pack(side="bottom", anchor="e", padx=4, pady=4)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.toplevel.destroy)

    def _add_entry_with_label(self, label_text, var_type, var_name):
        '''var_type: 'f' for float or 'd' for integer'''
        label = tk.Label(self.toplevel, text=label_text)
        variable = (tk.DoubleVar(), tk.IntVar())['d' == var_type]
        entry = tk.Entry(self.toplevel, textvariable=variable)
        self.vars_map[var_name].append(variable)
        label.pack(side="top", fill="x")
        entry.pack(side="top", fill="x")

    def _input_param(self, name, toplevel):
        self.vars_map[name] = list()
        '''add label entry for each parameter'''
        label = tk.Label(toplevel, text=name)
        label.pack(side="top", fill="x")
        self._add_entry_with_label("Begin Value", 'f', name)
        self._add_entry_with_label("End Value", 'f', name)
        self._add_entry_with_label("Step Value", 'f', name)

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