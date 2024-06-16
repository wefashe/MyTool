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
        self.tk_input_machine_code,self.tk_var_machine_code,imc_x_pos,imc_y_pos = self.__tk_input_machine_code(self)
        self.tk_button_machine_code,bmc_x_pos,bmc_y_pos = self.__tk_button_machine_code(self,x_pos=imc_x_pos + 5)
        self.tk_input_register_code,self.tk_var_register_code,irc_x_pos,irc_y_pos = self.__tk_input_register_code(self, y_pos = 65)
        self.tk_button_register_code,brc_x_pos,brc_y_pos = self.__tk_button_register_code(self,x_pos=irc_x_pos + 5, y_pos = 65)
        self.tk_label_expire_status,les_x_pos,les_y_pos = self.__tk_label_expire_status(self, y_pos = 105)

    def __win(self):
        self.title("被注册软件")
        width, height = 500, 140
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        
        self.resizable(width=False, height=False)

    def __tk_input_machine_code(self, parent, x_pos = 20, y_pos = 20):
        label = Label(parent,text="机器码: ",anchor="center", )
        stringVar = StringVar()
        entry = Entry(parent, textvariable=stringVar)
        label_width = 50
        entry_width = 350
        height = 30
        label.place(x=x_pos, y=y_pos, width=label_width, height=height)
        entry.place(x=x_pos+label_width, y=y_pos, width=entry_width, height=height)
        return entry, stringVar, x_pos + label_width + entry_width, y_pos+height
    
    def __tk_button_machine_code(self, parent, x_pos = 20, y_pos = 20):
        button = Button(parent, text="复制", takefocus=False,)
        button_width = 50
        button_height = 30
        button.place(x=x_pos, y=y_pos, width=button_width, height=button_height)
        return button, x_pos+button_width, y_pos+button_height
    
    def __tk_input_register_code(self, parent, x_pos = 20, y_pos = 20):
        label = Label(parent,text="注册码: ",anchor="center", )
        stringVar = StringVar()
        entry = Entry(parent, textvariable=stringVar)
        label_width = 50
        entry_width = 350
        height = 30
        label.place(x=x_pos, y=y_pos, width=label_width, height=height)
        entry.place(x=x_pos+label_width, y=y_pos, width=entry_width, height=height)
        return entry, stringVar, x_pos + label_width + entry_width, y_pos+height

    def __tk_button_register_code(self, parent, x_pos = 20, y_pos = 20):
        button = Button(parent, text="注册", takefocus=False, state=DISABLED)
        button_width = 50
        button_height = 30
        button.place(x=x_pos, y=y_pos, width=button_width, height=button_height)
        return button, x_pos+button_width, y_pos+button_height
    
    def __tk_label_expire_status(self, parent, x_pos = 20, y_pos = 20):
        label = Label(parent, )
        label_width = 350
        label_height = 30
        label.place(x=x_pos, y=y_pos, width=label_width, height=label_height)
        return label, x_pos + label_width + label_width, y_pos+label_height

    def show(self):
        self.mainloop()

class WinGUI(Win):
    
    def __init__(self, control):
        from control import Control
        
        self.ctl:Control = control
        super().__init__()
        self.__event_bind()
        self.ctl.init(self)

    def __event_bind(self):
        """
        事件绑定
        """
        self.tk_var_register_code.trace_add('write', self.ctl.check_button_register_code)
        self.tk_button_machine_code.config(command=self.ctl.copy_to_clipboard)
        self.tk_button_register_code.config(command=self.ctl.login)

if __name__ == "__main__":
    win = Win()
    win.show()