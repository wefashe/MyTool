#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""

import ntplib
import hashlib
import pyperclip
from datetime import datetime, timedelta
import tkinter as tk
from dateutil.relativedelta import relativedelta
from tkinter.messagebox import showinfo

class Control:

    def __init__(self):
        pass

    def init(self, win):
        """
        窗口初始化
        """
        from wingui import WinGUI
        
        self.win:WinGUI = win
        self.win.tk_var_radio_expire.set(2)
        self.win.tk_var_checkbox_machine.set(1)
        self.win.tk_button_copy_register_code.config(state=tk.DISABLED) 

    def get_beijin_time(self):
        try:
            response = ntplib.NTPClient().request('ntp.aliyun.com')
            return datetime.fromtimestamp(response.tx_time)
        except Exception as e:
            print(e)
            return datetime.now()
        
    def get_exp_time(self, current_datetime, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0):
        # 使用relativedelta进行年和月的加减
        new_date = current_datetime + relativedelta(years=years, months=months)
        # 使用timedelta进行周、天、小时、分钟和秒的加减
        new_date = new_date + timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
        return new_date

    def check_checkbox_machine(self, *args):
        var_checkbox_machine = self.win.tk_var_checkbox_machine.get()
        if var_checkbox_machine == 1:
            self.win.tk_label_machine_code.config(state=tk.NORMAL)
            self.win.tk_input_machine_code.config(state=tk.NORMAL)
            self.win.tk_button_paste_machine_code.config(state=tk.NORMAL)
        else :
            self.win.tk_label_machine_code.config(state=tk.DISABLED)
            self.win.tk_input_machine_code.delete(0, 'end')
            self.win.tk_input_machine_code.config(state=tk.DISABLED)
            self.win.tk_button_paste_machine_code.config(state=tk.DISABLED)

    def check_checkbox_expire(self, *args):
        var_checkbox_expire = self.win.tk_var_checkbox_expire.get()
        if var_checkbox_expire == 1:
            self.win.tk_radio_expire_week.config(state=tk.NORMAL)
            self.win.tk_radio_expire_month.config(state=tk.NORMAL)
            self.win.tk_radio_expire_quarter.config(state=tk.NORMAL)
            self.win.tk_radio_expire_date.config(state=tk.NORMAL)
            self.check_radio_expire_date(None)
        else:
            self.win.tk_radio_expire_week.config(state=tk.DISABLED)
            self.win.tk_radio_expire_month.config(state=tk.DISABLED)
            self.win.tk_radio_expire_quarter.config(state=tk.DISABLED)
            self.win.tk_datetime_expire_date.set_date(self.get_beijin_time()) 
            self.win.tk_radio_expire_date.config(state=tk.DISABLED)
            self.win.tk_datetime_expire_date.config(state=tk.DISABLED)

    def check_radio_expire_date(self, *args):
        var_radio_expire = self.win.tk_var_radio_expire.get()      
        now = self.get_beijin_time()
        if var_radio_expire == 4:
            self.win.tk_datetime_expire_date.config(state=tk.NORMAL)
            self.win.tk_datetime_expire_date.set_date(now)  
        else:
            self.win.tk_datetime_expire_date.set_date(now)  
            self.win.tk_datetime_expire_date.config(state=tk.DISABLED)

    def check_button_copy_register_code(self, *args):
            var_register_code = self.win.tk_var_register_code.get().strip()
            if var_register_code:
                self.win.tk_button_copy_register_code.config(state=tk.NORMAL)
            else:
                self.win.tk_button_copy_register_code.config(state=tk.DISABLED) 
    
    def button_paste_machine_code(self, event):
        self.win.tk_var_machine_code.set(pyperclip.paste())

    def button_copy_register_code(self, event):
        pyperclip.copy(self.win.tk_var_register_code.get())
        showinfo(title="提示", message="复制成功!")

    def encrypt(self, plaintext):
        from Crypto.Random import get_random_bytes
        from Crypto.Cipher import AES
        import base64
        key = get_random_bytes(16) 
        # 生成一个随机的 IV
        iv = get_random_bytes(AES.block_size)
        # 创建 AES CFB 加密对象
        cipher = AES.new(key, AES.MODE_CFB, iv)
        # 执行加密操作
        base64_encoded = base64.b64encode(plaintext.encode('utf-8'))
        ciphertext = cipher.encrypt(base64_encoded)
        return (key + iv + ciphertext).hex().upper()

    def button_create_register_code(self, event):
        now = self.get_beijin_time()
        var_checkbox_machine = self.win.tk_var_checkbox_machine.get()
        if var_checkbox_machine == 1:
            var_machine_code = self.win.tk_var_machine_code.get().strip()
            if not var_machine_code:
                showinfo(title="提示", message="机器码为空!")
                return
            if len(var_machine_code) != 32:
                showinfo(title="提示", message="机器码不正确!")
                return
        else:
            var_machine_code = hashlib.md5((str( datetime.timestamp(now))).encode('UTF-8')).hexdigest().upper()
        var_checkbox_expire = self.win.tk_var_checkbox_expire.get()
        if var_checkbox_expire == 1:
            var_radio_expire = self.win.tk_var_radio_expire.get()
            if var_radio_expire == 1:
                expire = self.get_exp_time(now, weeks=1)
            elif var_radio_expire == 2:
                expire = self.get_exp_time(now, months=1)
            elif var_radio_expire == 3:
                expire = self.get_exp_time(now, months=3)
            elif var_radio_expire == 4:
                expire_date = self.win.tk_datetime_expire_date.get_date()
                if expire_date == now.date():
                    expire = datetime.combine(expire_date, datetime.max.time())
                else:
                    expire = datetime.combine(expire_date, now.time())
            else:
                expire = datetime.combine(now.date(), datetime.max.time())
        else:
            expire = self.get_beijin_time()
        license_text = f'{var_machine_code}{var_checkbox_machine}{var_checkbox_expire}{int(datetime.timestamp(expire) * 1000000)}'[::-1]
        self.win.tk_var_register_code.set(self.encrypt(license_text))
        showinfo(title="提示", message="注册码生成成功!")


