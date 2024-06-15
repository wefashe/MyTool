#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""

import ntplib
from datetime import datetime, timedelta
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

    def check_radio_expire(self, *args):
        var_radio_expire = self.win.tk_var_radio_expire.get()
        import tkinter as tk
        if var_radio_expire == 1:
            expire = self.get_exp_time(weeks=1)
            self.win.tk_datetime_expire.set_date(expire)
        elif var_radio_expire == 2:
            expire = self.get_exp_time(months=1)
            self.win.tk_datetime_expire.set_date(expire)
        elif var_radio_expire == 3:
            expire = self.get_exp_time(months=3)
            self.win.tk_datetime_expire.set_date(expire) 
        
        if var_radio_expire == 4:
            expire = self.get_exp_time()
            self.win.tk_datetime_expire.set_date(expire) 
            self.win.tk_datetime_expire.config(state=tk.NORMAL)
        else:
            self.win.tk_datetime_expire.config(state=tk.DISABLED)