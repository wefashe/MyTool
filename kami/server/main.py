#!/usr/bin/env python3
# -*-coding:utf-8 -*-

from wingui import WinGUI
from control import Control

if __name__ == '__main__':

    control = Control()
    win = WinGUI(control)
    win.show()