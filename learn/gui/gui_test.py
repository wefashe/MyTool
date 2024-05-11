import tkinter as tk
from tkinter import ttk # tkinter扩展tkk
from tkinter import filedialog # 选择文件
from tkinter import messagebox # 消息弹框
import asyncio # 异步编程
import threading # 多线程

win = tk.Tk() # 创建 Tkinter 窗口

# Variable: BooleanVar, DoubleVar, IntVar, StringVar 可以进行双向绑定

#显示标签
def print_tk_text(text):
   file_path = filedialog.askopenfilename()
   tk.Label(win, text=text + file_path, font=('Helvetica 13 bold')).pack()
def print_ttk_text(text):
   messagebox.showinfo("ttk按钮被点击了", "哈哈哈")
   ttk.Label(win, text=text, font=('Helvetica 13 bold')).pack()

button1 = tk.Button(win, text="点击tk按钮",  command=lambda:print_tk_text('tk按钮被点击了,选择了文件：')) # 创建按钮
button1.pack(pady=10) # 按钮添加到窗口
button2 = ttk.Button(win, text="点击ttk按钮",  command=lambda:print_ttk_text('ttk按钮被点击了')) # 创建按钮
button2.pack(pady=10) # 按钮添加到窗口


# TODO 


win.geometry("600x250") # 设置窗口大小和初始位置
win.configure(bg='IndianRed') # 背景色
win.wm_attributes("-topmost", 1)  # 窗口置顶
win.iconbitmap('learn/gui/favicon.ico') # 设置图标
win.title('测试窗口') # 标题
win.mainloop() # 进入消息循环