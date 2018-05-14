from Tkinter import *
from ttk import *

# class progress_bar(tk.Tk):
#     def __init__(self, *args, **kwargs):
#         tk.Tk.__init__(self, *args, **kwargs)
#         self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
#         self.progress.pack()
#         self.val = 0
#         self.maxval = 1
#         self.progress["maximum"] = 1
#
#     def updating(self, val):
#         self.val = val
#         self.progress["value"] = self.val
#         print(self.val)
#
#         if self.val == self.maxval:
#             self.destroy()


# def test(i=0):
#     app.updating(float(i)/100)
#     if i < 100:
#         app.after(100, test, i+1)
#
#
# app = progress_bar()
# app.after(1, test)
# app.mainloop()

def show_process_bar():
    pro

app = Tk()
button = Button(app, text="click me", command=show_process_bar)
