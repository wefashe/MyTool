#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口布局, 事件绑定
"""

from tkinter import *
from tkinter.ttk import *

class Win(Tk):
    def __init__(self):
        super().__init__()
        self.__win()

    def __win(self):
        self.title("被注册软件")
        width, height = 600, 500
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        
        self.resizable(width=False, height=False)


    def show(self):
        self.mainloop()

class WinGUI(Win):
    def __init__(self, control):
        self.control = control
        super().__init__()
        self.__event_bind()
        self.control.init(self)

    def __event_bind(self):
        """
        事件绑定
        """
        pass

if __name__ == "__main__":
    win = Win()
    win.show()