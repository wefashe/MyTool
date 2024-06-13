#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""
import uuid
import hashlib
import tkinter as tk
from wingui import WinGUI
from tkinter.messagebox import showinfo

class Control:

    win: WinGUI

    def __init__(self):
        pass

    def init(self, win):
        """
        窗口初始化
        """
        self.win = win
        mac_address = self.get_mac_address()
        machine_code = self.hash_msg(mac_address)
        # self.win.tk_input_machine_code.insert(0, machine_code)
        self.win.tk_var_machine_code.set(machine_code)
        self.win.tk_input_machine_code.config(state='readonly')
        self.win.tk_input_register_code.config(state='readonly')

    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
    
    def hash_msg(self, msg, salt=None):
        sha256 = hashlib.sha256()
        sha256.update(msg.encode('utf-8'))
        if salt:
            sha256.update(salt.encode('gbk'))
        res = sha256.hexdigest()
        return res.upper()[::2]
    
    def check_button_register_code(self):
        var_register_code = self.win.tk_var_register_code.get().strip()
        if var_register_code:
            self.win.tk_button_register_code.config(state=tk.NORMAL)
        else:
            self.win.tk_button_register_code.config(state=tk.DISABLED)    

    def copy_to_clipboard(self, event, widget):
        # event.widget.select_range(0, 'end')
        # event.widget.icursor('end')
        # event.widget.clipboard_clear()
        # event.widget.clipboard_append(event.widget.get())
        widget.select_range(0, 'end')
        widget.icursor('end')
        self.win.clipboard_clear()
        self.win.clipboard_append(widget.get())
        showinfo(title="提示", message="复制成功")


    def paste_from_clipboard(self, event, widget):
        # event.widget.delete(0, 'end')
        # event.widget.insert(0, event.widget.clipboard_get())
        widget.delete(0, 'end')
        # widget.insert(0, self.win.clipboard_get())
        self.win.tk_var_register_code.set(self.win.clipboard_get())
