#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""
窗口控制, 业务逻辑
"""

from wingui import WinGUI

class Control:

    win: WinGUI

    def __init__(self):
        pass

    def init(self, win):
        """
        窗口初始化
        """
        self.win = win