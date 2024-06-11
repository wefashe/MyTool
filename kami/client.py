
import uuid
import ntplib
import hashlib
import base64
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import tkinter as tk
from tkinter import ttk

def get_beijin_time():
    try:
        response = ntplib.NTPClient().request('ntp.aliyun.com')
        return datetime.fromtimestamp(response.tx_time)
    except Exception as e:
        print(e)
        return datetime.now()

def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

def hash_msg(msg, salt=None):
    sha256 = hashlib.sha256()
    sha256.update(msg.encode('utf-8'))
    if salt:
        sha256.update(salt.encode('gbk'))
    res = sha256.hexdigest()
    return res.upper()[::2]


def get_beijin_time():
    try:
        response = ntplib.NTPClient().request('ntp.aliyun.com')
        return datetime.fromtimestamp(response.tx_time)
    except Exception as e:
        print(e)
        return datetime.now()
    
def check_exp_time(exp_time):
    current_datetime = get_beijin_time()
    exp_datetime = datetime.fromtimestamp(exp_time)
    print(current_datetime)
    print(exp_datetime)
    if current_datetime > exp_datetime:
        return True
    else:
        return False
    
def copy_to_clipboard(event):
    # 全选文本
    event.widget.select_range(0, 'end')
    event.widget.icursor('end')
    # 复制机器码到剪贴板
    event.widget.clipboard_clear()
    event.widget.clipboard_append(event.widget.get())

def start_countdown(count):
    total_seconds = count
    days = total_seconds // (24 * 3600)
    total_seconds = total_seconds % (24 * 3600)

    hours = total_seconds // 3600
    total_seconds %= 3600

    minutes = total_seconds // 60

    seconds = total_seconds % 60

    # 更新标签文本
    label.config(text=f'剩余时间：{days}天{hours:02}小时{minutes:02}分钟{seconds:02}秒')
    
    if count > 0:
        # 每1000毫秒（1秒）更新一次
        win.after(1000, start_countdown, count - 1)
    else:
        # 倒计时结束时显示提示
        label.config(text="已到期！")

def login():
    msg_text = card_code_entry.get()
    BLOCK_SIZE = AES.block_size # 16的倍数
    # key长度必须是16, 24, 32
    key = '9876543219876543'

    encrypted_msg_bytes = bytes.fromhex(msg_text)
    cipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
    cipher_decrypt = cipher.decrypt(encrypted_msg_bytes)
    decrypted_msg = unpad(cipher_decrypt, BLOCK_SIZE)

    print(decrypted_msg.decode('utf-8'))

    license_str = base64.b64decode(decrypted_msg)
    license_dict = eval(license_str)
    print(license_dict)

    if check_exp_time(license_dict['exp']):
        return

    now = get_beijin_time()
    exp = datetime.fromtimestamp(license_dict['exp'])

    date = exp - now
    seconds = date.seconds +  date.days * 24 * 60 * 60
    start_countdown(seconds)

        

win = tk.Tk()
win.geometry("600x250")
win.title('卡密测试 ' + str(tk.TkVersion))
win.resizable(False, False)
show_kami = ttk.Label(win, text='机器码: ')
show_kami.pack()


input_kami = ttk.Entry(win, width=34)
mac_address = get_mac_address()
machine_code = hash_msg(mac_address)
input_kami.insert(0, machine_code)
input_kami.config(state='readonly')
input_kami.pack()
# 绑定双击事件到复制功能
input_kami.bind("<Double-1>", copy_to_clipboard)


# 创建并设置卡密输入框
card_code_label = tk.Label(win, text="卡 密:")
card_code_label.pack()

card_code_entry = tk.Entry(win, width=35)
card_code_entry.pack()

# 创建标签用于显示倒计时
label = tk.Label(win, width=35)
label.pack(pady=20)

# 创建登录按钮
login_button = ttk.Button(win, text="登录", command=login)
login_button.pack()

win.mainloop()
    

