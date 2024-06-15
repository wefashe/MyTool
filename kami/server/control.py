#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""

import ntplib
from datetime import datetime, timedelta
import tkinter as tk
from dateutil.relativedelta import relativedelta

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
        
    def get_exp_time(self, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0):
        # 当前日期和时间
        current_datetime = self.get_beijin_time()
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
            expire = self.get_exp_time()
            self.win.tk_datetime_expire_date.set_date(expire) 
            self.win.tk_radio_expire_date.config(state=tk.DISABLED)
            self.win.tk_datetime_expire_date.config(state=tk.DISABLED)

    def check_radio_expire_date(self, *args):
        var_radio_expire = self.win.tk_var_radio_expire.get()
        # if var_radio_expire == 1:
        #     expire = self.get_exp_time(weeks=1)
        #     self.win.tk_datetime_expire_date.set_date(expire)
        # elif var_radio_expire == 2:
        #     expire = self.get_exp_time(months=1)
        #     self.win.tk_datetime_expire_date.set_date(expire)
        # elif var_radio_expire == 3:
        #     expire = self.get_exp_time(months=3)
        #     self.win.tk_datetime_expire_date.set_date(expire)        
        if var_radio_expire == 4:
            self.win.tk_datetime_expire_date.config(state=tk.NORMAL)
            expire = self.get_exp_time()
            self.win.tk_datetime_expire_date.set_date(expire)  
        else:
            expire = self.get_exp_time()
            self.win.tk_datetime_expire_date.set_date(expire)  
            self.win.tk_datetime_expire_date.config(state=tk.DISABLED)

    def check_button_copy_register_code(self, *args):
            var_register_code = self.win.tk_var_register_code.get().strip()
            if var_register_code:
                self.win.tk_button_copy_register_code.config(state=tk.NORMAL)
            else:
                self.win.tk_button_copy_register_code.config(state=tk.DISABLED) 

