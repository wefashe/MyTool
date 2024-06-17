#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""

import random
import string
import ntplib
import hashlib
import pyperclip
from datetime import datetime, timedelta
import tkinter as tk
from time import ctime, sleep
from dateutil.relativedelta import relativedelta
from tkinter.messagebox import showinfo, showwarning

class Control:

    def __init__(self):
        self.check_network()

    def init(self, win):
        """
        窗口初始化
        """
        from wingui import WinGUI
        
        self.win:WinGUI = win
        self.win.tk_var_radio_expire.set(2)
        self.win.tk_var_checkbox_machine.set(1)
        self.win.tk_button_copy_register_code.config(state=tk.DISABLED) 
        self.win.tk_input_register_code.config(state='readonly')
        self.win.tk_datetime_expire_date.config(mindate=self.get_beijin_time())
    
    def check_network(self, host="www.baidu.com", port=80, timeout=5):
        try:
            import socket
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        except Exception as e:
            showwarning("警告", "网络不可用，请检查您的连接")
            exit()

    def get_beijin_time(self, retries=3, delay=1):
        self.check_network()
        servers = [
            "ntp.aliyun.com", "ntp1.aliyun.com", "ntp2.aliyun.com", 
            "ntp3.aliyun.com", "ntp4.aliyun.com", "ntp5.aliyun.com", 
            "ntp6.aliyun.com", "ntp7.aliyun.com"
        ]
        client = ntplib.NTPClient()
        for attempt in range(len(servers)):
            try:
                response = client.request(servers[attempt-1])
                print(f"time from {servers[attempt-1]}: {ctime(response.tx_time)}")
                return datetime.fromtimestamp(response.tx_time)
            except Exception as e:
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...", e)
                    sleep(delay)
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
            self.win.tk_radio_expire_date.config(state=tk.DISABLED)
            self.win.tk_datetime_expire_date.config(state=tk.DISABLED)

    def check_radio_expire_date(self, *args):
        var_radio_expire = self.win.tk_var_radio_expire.get()      
        if var_radio_expire == 4:
            self.win.tk_datetime_expire_date.config(state=tk.NORMAL)
            self.win.tk_datetime_expire_date.set_date(self.get_beijin_time())  
        else:
            self.win.tk_datetime_expire_date.config(state=tk.DISABLED)

    def check_button_copy_register_code(self, *args):
        var_register_code = self.win.tk_var_register_code.get().strip()
        if var_register_code:
            self.win.tk_button_copy_register_code.config(state=tk.NORMAL)
        else:
            self.win.tk_button_copy_register_code.config(state=tk.DISABLED) 
    
    def button_paste_machine_code(self):
        self.win.tk_var_machine_code.set(pyperclip.paste())

    def button_copy_register_code(self):
        pyperclip.copy(self.win.tk_var_register_code.get())
        showinfo(title="提示", message="复制成功!")

    def encrypt(self, plaintext:str):
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
    
    def random_str(self, len = 5):
        # 定义字符集，包括大写字母、小写字母和数字
        characters = string.ascii_letters + string.digits
        # 使用random.choice()从字符集中随机选择5个字符
        random_string = ''.join(random.choice(characters) for _ in range(len))
        return random_string

    def button_create_register_code(self):
        now = self.get_beijin_time()
        var_checkbox_machine = self.win.tk_var_checkbox_machine.get()
        if var_checkbox_machine == 1:
            var_machine_code = self.win.tk_var_machine_code.get().strip()
            if not var_machine_code:
                showwarning(title="警告", message="机器码为空!")
                return
            if len(var_machine_code) != 32:
                showwarning(title="警告", message="机器码错误!")
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
            expire = now
        # app_info 软件信息，现在暂无，随机数代替
        app_code = '01'
        app_info = self.random_str(12).upper() + app_code
        timestamp = int(datetime.timestamp(expire) * 1000000)
        # 14 + 1 + 32 + 1 + 16 = 64
        license_text = f'{app_info}{var_checkbox_machine}{var_machine_code}{var_checkbox_expire}{timestamp}'
        print(len(license_text), license_text)
        encrypt_license_text = self.encrypt(license_text[::-1])
        print(len(encrypt_license_text), encrypt_license_text)
        # TODO 先存远程数据库, ID为注册码, 加上生成电脑的ip,系统版本,电脑用户名,创建时间
        self.win.tk_var_register_code.set(encrypt_license_text)
        pyperclip.copy(encrypt_license_text)
        showinfo(title="提示", message="生成成功!")
        


