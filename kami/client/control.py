#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""
import uuid
import base64
import ntplib
import winreg
import hashlib
import traceback
import tkinter as tk
from wingui import WinGUI
from tkinter.messagebox import showinfo
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class Control:

    win: WinGUI

    def __init__(self):
        pass

    def init(self, win):
        """
        窗口初始化
        """
        self.win = win
        # 操作注册表需要赋予完全访问权限

        # self.add_winreg_key(sub_key_name)
        mac_address = self.get_mac_address()
        machine_code = self.hash_msg(mac_address)
        # self.win.tk_input_machine_code.insert(0, machine_code)
        self.win.tk_var_machine_code.set(machine_code)
        self.win.tk_input_machine_code.config(state='readonly')

        register_code = self.get_register_code_form_winreg()
        if register_code:
             self.win.tk_var_register_code.set(register_code)
             self.check(register_code)

    def get_register_code_form_winreg(self):
        self.winreg_root_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        self.winreg_key_name = 'f'
        try:
            self.winreg_my_key = winreg.OpenKey(self.winreg_root_key, self.winreg_key_name)
        except FileNotFoundError:
            self.winreg_my_key = winreg.CreateKey(self.winreg_root_key, self.winreg_key_name)
        register_code = winreg.QueryValue(self.winreg_root_key, self.winreg_key_name).strip()
        winreg.CloseKey(self.winreg_root_key)
        return register_code
    
    def set_register_code_to_winreg(self, register_code):
        self.winreg_root_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        self.winreg_key_name = 'f'
        try:
            self.winreg_my_key = winreg.OpenKey(self.winreg_root_key, self.winreg_key_name)
        except FileNotFoundError:
            self.winreg_my_key = winreg.CreateKey(self.winreg_root_key, self.winreg_key_name)
        winreg.SetValue(self.winreg_root_key,self.winreg_key_name, winreg.REG_SZ, register_code.strip())
        winreg.CloseKey(self.winreg_root_key)

    def get_mac_address(self):
        return ":".join([uuid.uuid1().hex[-12:][e:e + 2] for e in range(0, 11, 2)])
    
    def hash_msg(self, msg, salt='!@#$%^&*()'):        
        for i in range(3):
            # msg整体插入salt的每个元素之间
            msg = hashlib.md5((str(msg).join(salt)).encode('UTF-8')).hexdigest()
        return msg.upper()
    def check_button_register_code(self, *args):
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

    def get_beijin_time(self):
        try:
            response = ntplib.NTPClient().request('ntp.aliyun.com')
            return datetime.fromtimestamp(response.tx_time)
        except Exception as e:
            traceback.print_exc(file = open('error.log', 'a+'))
            return datetime.now()

    def check_exp_time(self, exp_time):
        current_datetime = self.get_beijin_time()
        exp_datetime = datetime.fromtimestamp(exp_time)
        if current_datetime > exp_datetime:
            return True
        else:
            return False
        
    def start_countdown(self, count):
        total_seconds = count
        days = total_seconds // (24 * 3600)
        total_seconds = total_seconds % (24 * 3600)

        hours = total_seconds // 3600
        total_seconds %= 3600

        minutes = total_seconds // 60

        seconds = total_seconds % 60
        # 更新标签文本
        self.win.tk_label_expire_status.config(text = f'已注册，{days}天{hours:02}时{minutes:02}分{seconds:02}秒后过期')
        if count > 0:
            # 每1000毫秒（1秒）更新一次
            self.win.after(1000, self.start_countdown, count - 1)
        else:
            # 倒计时结束时显示提示
            self.win.tk_label_expire_status.config(text = f'已到期，请重新注册本软件')

    def check(self, register_code):
        BLOCK_SIZE = AES.block_size # 16的倍数
        # key长度必须是16, 24, 32
        key = '9876543219876543'
        try:
            encrypted_msg_bytes = bytes.fromhex(register_code)
            cipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
            cipher_decrypt = cipher.decrypt(encrypted_msg_bytes)
            decrypted_msg = unpad(cipher_decrypt, BLOCK_SIZE)
            decoded_bytes = base64.b64decode(decrypted_msg)
            license_dict = eval(decoded_bytes.decode('utf-8'))
        except Exception as e:
            traceback.print_exc(file = open('error.log', 'a+'))
            showinfo(title="提示", message="注册码不正确")
            return
        
        psw = license_dict['psw']
        if psw and psw != self.win.tk_var_machine_code.get().strip():
            showinfo(title="提示", message="注册码不匹配")
            return
        exp = license_dict['exp']
        if exp:
            if self.check_exp_time(exp):
                showinfo(title="提示", message="注册码已过期")
                return
            now = self.get_beijin_time()
            exp = datetime.fromtimestamp(license_dict['exp'])

            date = exp - now
            seconds = date.seconds +  date.days * 24 * 60 * 60
            self.start_countdown(seconds)
        else:
            self.win.tk_label_expire_status.config(text = f'已注册，永久有效')
        self.set_register_code_to_winreg(register_code)

    def login(self, event):
        register_code = self.win.tk_var_register_code.get().strip()
        self.check(register_code)
        showinfo(title="提示", message="注册成功")