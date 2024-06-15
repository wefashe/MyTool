#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口布局, 事件绑定
"""

from tkinter import *
from tkinter.ttk import *
from tkcalendar import DateEntry

class Win(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_input_machine_code,self.tk_var_machine_code,imc_x_pos,imc_y_pos = self.__tk_input_machine_code(self)
        self.tk_button_paste_machine_code,bmc_x_pos,bmc_y_pos = self.__tk_button_paste_machine_code(self,x_pos=imc_x_pos + 5)
        self.tk_input_register_code,self.tk_var_register_code,irc_x_pos,irc_y_pos = self.__tk_input_register_code(self, y_pos = 65)
        self.tk_button_copy_register_code,brc_x_pos,brc_y_pos = self.__tk_button_copy_register_code(self,x_pos=irc_x_pos + 5, y_pos = 65)
       
        #    self.date_frame = ttk.LabelFrame(self, text="Select Date")
        # self.date_frame.pack(pady=10, padx=10, fill="x")
       
        self.__tk_checkbox_machine(self)
        self.__tk_checkbox_expire(self)
        self.__tk_radio_expire(self)
        self.__tk_button_create_register_code(self)

    def __win(self):
        self.title("经典注册机")
        width, height = 500, 180
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
    
    def __tk_button_paste_machine_code(self, parent, x_pos = 20, y_pos = 20):
        button = Button(parent, text="粘贴", takefocus=False,)
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

    def __tk_button_copy_register_code(self, parent, x_pos = 20, y_pos = 20):
        button = Button(parent, text="复制", takefocus=False, state=DISABLED)
        button_width = 50
        button_height = 30
        button.place(x=x_pos, y=y_pos, width=button_width, height=button_height)
        return button, x_pos+button_width, y_pos+button_height
        
    def __tk_checkbox_machine(self, parent):
        intVar = IntVar()
        checkbox = Checkbutton(parent, text = "绑定电脑", variable = intVar, \
                 onvalue = 1, offvalue = 0)
        checkbox.place(x=20, y=110, width=75, height=30)
        return checkbox, intVar

    def __tk_checkbox_expire(self, parent):
        intVar = IntVar(value=1)
        checkbox = Checkbutton(parent, text = "限制时间", variable = intVar)
        checkbox.place(x=110, y=110, width=75, height=30)
        return checkbox, intVar
        
    def __tk_radio_expire(self, parent):
        intvar = IntVar()
        radioweek = Radiobutton(parent, text='周',value=1,variable=intvar)
        radiomonth = Radiobutton(parent, text='月',value=2,variable=intvar)
        radioquarter = Radiobutton(parent, text='季',value=3,variable=intvar)
        radioDate = Radiobutton(parent,value=4,variable=intvar)
        dateentry = DateEntry(parent)
        radioweek.place(x=185, y=110, width=35, height=30)
        radiomonth.place(x=220, y=110, width=35, height=30)
        radioquarter.place(x=255, y=110, width=35, height=30)
        radioDate.place(x=290, y=110, width=20, height=30)
        dateentry.place(x=310, y=110, width=95, height=30)
        return radioweek,radiomonth,radioquarter

    def __tk_button_create_register_code(self, parent, x_pos = 20, y_pos = 20):
        button = Button(parent, text="生成", takefocus=False)
        x_pos = 424
        y_pos = 110
        button_width = 50
        button_height = 30
        button.place(x=x_pos, y=y_pos, width=button_width, height=button_height)
        return button, x_pos+button_width, y_pos+button_height
    
    def show(self):
        self.mainloop()

class WinGUI(Win):

    def __init__(self, control):
        self.ctl = control
        super().__init__()
        self.__event_bind()
        self.ctl.init(self)

    def __event_bind(self):
        """
        事件绑定
        """
        # self.tk_var_register_code.trace_add('write', self.ctl.check_button_register_code)
        # self.tk_button_machine_code.bind('<Button-1>',lambda event: self.ctl.copy_to_clipboard(event, self.tk_input_machine_code))
        # self.tk_button_register_code.bind('<Button-1>', self.ctl.login)

if __name__ == "__main__":
    win = Win()
    win.show()