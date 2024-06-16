#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""
import uuid
import ntplib
import pyperclip
import winreg
import hashlib
import tkinter as tk
import traceback
from time import ctime, sleep
from tkinter.messagebox import showinfo, showwarning
from datetime import datetime

class Control:

    def __init__(self):
        self.check_network()

    def init(self, win):
        """
        窗口初始化
        """
        from wingui import WinGUI
        
        self.win:WinGUI = win

        self.after_id = None
        self.win.tk_input_machine_code.config(state='readonly')

        mac_address = self.get_mac_address()
        machine_code = self.hash_msg(mac_address)
        self.win.tk_var_machine_code.set(machine_code)
        register_code = self.get_register_code_form_winreg()
        if register_code:
             self.win.tk_var_register_code.set(register_code)
             self.check(register_code)

    def get_register_code_form_winreg(self):
        # 操作注册表需要赋予完全访问权限
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

    def copy_to_clipboard(self):
        pyperclip.copy(self.win.tk_var_machine_code.get())
        showinfo(title="提示", message="复制成功")

    def paste_from_clipboard(self, event):
        self.win.tk_var_register_code.set(pyperclip.paste())

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

    def check_exp_time(self, expire):
        current_datetime = self.get_beijin_time()
        if current_datetime > expire:
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
            self.after_id = self.win.after(1000, self.start_countdown, count - 1)
        else:
            # 倒计时结束时显示提示
            self.win.tk_label_expire_status.config(text = f'已到期，请重新注册本软件')

    def decrypt(self, ciphertext:str):
        from Crypto.Cipher import AES
        import base64

        msg_bytes = bytes.fromhex(ciphertext)

        key =  msg_bytes[:16]
        # 提取 IV
        iv = msg_bytes[16: 16 + AES.block_size]
        # 提取实际密文
        actual_ciphertext = msg_bytes[16 + AES.block_size:]
        # 创建 AES CFB 解密对象
        cipher = AES.new(key, AES.MODE_CFB, iv)
        # 执行解密操作
        base64_encoded = cipher.decrypt(actual_ciphertext)
        return  base64.b64decode(base64_encoded).decode('utf-8')

    def check(self, register_code):
        if self.after_id:
            self.win.after_cancel(self.after_id)
            self.after_id = None
        if len(register_code) != 224:
            showinfo(title="提示", message="注册码错误")
            return False
        try:
            license_text = self.decrypt(register_code)[::-1]
        except Exception:
            traceback.print_exc(file = open('error.log', 'a+'))
            showinfo(title="提示", message="注册码错误")
            return False
        machine_code = license_text[:32]
        checkbox_machine = license_text[32:33]
        checkbox_expire =  license_text[33:34]
        expire =  datetime.fromtimestamp(int(license_text[34:50]) / 1000000)
        if int(checkbox_machine) == 1:
            if self.win.tk_var_machine_code.get().strip() != machine_code:
                showinfo(title="提示", message="注册码不匹配")
                return False
        if int(checkbox_expire) == 1:
            if self.check_exp_time(expire):
                showinfo(title="提示", message="注册码已过期")
                return False
            now = self.get_beijin_time()
            date = expire - now
            seconds = date.seconds +  date.days * 24 * 60 * 60
            self.start_countdown(seconds)
        else:
            self.win.tk_label_expire_status.config(text = f'已注册，永久有效')
        self.set_register_code_to_winreg(register_code)
        # TODO 更新远程数据库, ID为注册码, 更新登录电脑的ip,系统版本,电脑用户名,登录时间
        return True

    def login(self):
        register_code = self.win.tk_var_register_code.get().strip()
        if self.check(register_code):
            showinfo(title="提示", message="注册成功")
        else:
            # 删除注册表
            pass