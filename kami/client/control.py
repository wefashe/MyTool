#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""
import uuid
import base64
import ntplib
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
        mac_address = self.get_mac_address()
        machine_code = self.hash_msg(mac_address)
        # self.win.tk_input_machine_code.insert(0, machine_code)
        self.win.tk_var_machine_code.set(machine_code)
        self.win.tk_input_machine_code.config(state='readonly')

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
        self.win.tk_label_expire_status.config(text = f'剩余使用时间：{days}天{hours:02}小时{minutes:02}分钟{seconds:02}秒')
        if count > 0:
            # 每1000毫秒（1秒）更新一次
            self.win.after(1000, self.start_countdown, count - 1)
        else:
            # 倒计时结束时显示提示
            self.win.tk_label_expire_status.config(text = f'剩余使用时间：已经到期')

    def login(self, event):
        var_register_code = self.win.tk_var_register_code.get().strip()
        BLOCK_SIZE = AES.block_size # 16的倍数
        # key长度必须是16, 24, 32
        key = '9876543219876543'
        try:
            encrypted_msg_bytes = bytes.fromhex(var_register_code)
            cipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
            cipher_decrypt = cipher.decrypt(encrypted_msg_bytes)
            decrypted_msg = unpad(cipher_decrypt, BLOCK_SIZE)
            decoded_bytes = base64.b64decode(decrypted_msg)
            license_dict = eval(decoded_bytes.decode('utf-8'))
        except Exception as e:
            traceback.print_exc(file = open('error.log', 'a+'))
            showinfo(title="提示", message="注册码错误")
            return
        
        psw = license_dict['psw']
        if psw and psw != self.win.tk_var_machine_code.get().strip():
            showinfo(title="提示", message="机器码不一致")
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
            showinfo(title="提示", message="注册成功")
        else:
            self.win.tk_label_expire_status.config(text = f'剩余使用时间：永久有效')
