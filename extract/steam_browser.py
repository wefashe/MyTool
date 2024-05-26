import tkinter as tk
import base64
import json
import time
from tkinter import messagebox
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

win = tk.Tk() 
win.title('cookie免登录 ' + str(tk.TkVersion))
win.resizable(False, False) #防止用户调整尺寸

width = 800 # win.winfo_width()
height = 300 # win.winfo_height()
#计算屏幕中央的位置
x = int(win.winfo_screenwidth()/2 -  width/ 2)
y = int(win.winfo_screenheight()/2 - height/ 2)
win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

tree = ttk.Treeview(win)  
tree.pack(pady=20, expand=tk.YES, fill=tk.BOTH)

tree["columns"] = ("name", "steamid", "state", "cookie")
tree['show'] = 'headings'
tree['selectmode'] = 'browse'

tree.column("name", width= 100, minwidth=100, anchor='w')  
tree.column("steamid", width= 130, minwidth=130, anchor='w')  
tree.column("state", width= 50, minwidth=50, anchor='w')  
tree.column("cookie",width=500, minwidth=500, anchor='w')
tree.heading("name", text="帐户" , anchor='w')
tree.heading("steamid", text="STEAM ID" , anchor='w')
tree.heading("state", text="状态" , anchor='w')
tree.heading("cookie", text="COOKIE", anchor='w')
# 读取cookies
with open(f'extract/test.txt', mode='r', encoding="UTF-8") as file:
    for line in file:
        array = line.strip().split('----')
        cookie = array[1].split("=")[1]
        ck =  cookie.split("%7C%7C")
        encodestr = ck[1].split('.')[1]
        # base64字符串个数必须是4的倍数，不够后面补=号
        if len(encodestr) % 4:
            encodestr += '=' * (4 - len(encodestr) % 4)
        decodestr = base64.b64decode(encodestr, validate=True)
        obj = json.loads(decodestr)
        if int(time.time()) > int(obj["exp"]):
            state = '已过期'
        else:
            state = '未过期'
        tree.insert('',tk.END,values=(array[0],obj['sub'], state, cookie))

def doubleClick(event):
    e = event.widget                                  
    row = e.identify("item",event.x,event.y)          
    values = e.item(row,"values")    
    if values[2] == '已过期':
        messagebox.showwarning("提示", f"{values[0]} 帐户的COOKIE已过期!")
        return
    global driver
    if 'driver' not in globals():
        options = webdriver.EdgeOptions()
        options.use_chromium = True
        options.add_experimental_option("detach", True)
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        driver = webdriver.Edge(options=options,service=EdgeService(EdgeChromiumDriverManager().install()), keep_alive=True)
        driver.maximize_window()
        # 首先清除由于浏览器打开已有的cookies
        driver.delete_all_cookies()       
        driver.get("https://store.steampowered.com/account")
        # 要登录的网站
    driver.add_cookie({"name": 'steamLoginSecure', "value": values[len(values) - 1]})
    driver.get("https://store.steampowered.com/account")
    # driver.refresh() 不一定一直这个页面

tree.bind('<Double-1>', doubleClick)

win.mainloop() 

if 'driver' in globals():
    # 关闭当前浏览器
    # driver.close()
    # 关闭所有浏览器
    driver.quit()