import os
import re
import uuid
import base64
import ntplib
import hashlib
import hashlib
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import tkinter as tk
from tkinter import ttk

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

def generate_unique_17_number():
    # 获取当前时间戳（毫秒级）
    timestamp = int(datetime.timestamp(get_beijin_time()) * 1000) % 10**10  # 保证时间戳部分是10位
    # 确保不以0开头，生成一个随机数
    first_digit = random.choice('123456789')
    # 生成6位随机数字
    random_digits = ''.join(random.choices('0123456789', k=6))
    # 组合成17位数字
    unique_number = f"{first_digit}{timestamp}{random_digits}"
    return unique_number

def get_exp_time(years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0):
    # 当前日期和时间
    current_datetime = get_beijin_time()
    # 使用relativedelta进行年和月的加减
    new_date = current_datetime + relativedelta(years=years, months=months)
    # 使用timedelta进行周、天、小时、分钟和秒的加减
    new_date = new_date + timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
    return new_date

def generate_jti():
    return  re.sub(r'^([0-9A-F]{4})([0-9A-F]{8})([0-9A-F]{5}).+', r'\1_\2_\3',  os.urandom(9).hex().upper())

license_dict = {}
mac_address = get_mac_address()
machine_code = hash_msg(mac_address)
license_dict['iss'] = machine_code
unique_17_number = generate_unique_17_number()
license_dict['sub'] = unique_17_number

exp_time = get_exp_time(years=0,days=0, hours=1, minutes=0, seconds=0)
license_dict['exp'] = datetime.timestamp(exp_time)
iat_time = get_beijin_time()
license_dict['iat'] = datetime.timestamp(iat_time)

target_machine_code = 'F2510763602D8BCCC069A2AE808EF63F'
license_dict['psw'] = target_machine_code
license_dict['jti'] =generate_jti()

license_str = str(license_dict)
# print(license_str)
license_text = base64.b64encode(license_str.encode('utf-8'))
# print(license_text.decode('utf-8'))

# 对加密数据进行补位
BLOCK_SIZE = AES.block_size # 16的倍数
# key长度必须是16, 24, 32
key = '9876543219876543'

cipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
encrypted_msg = cipher.encrypt(pad(license_text, BLOCK_SIZE))
msg_text = encrypted_msg.hex().upper()
print('卡密：',msg_text)


win = tk.Tk()
win.title('经典注册机')


win.mainloop()


# 1F9282646F93227D3D504982F1FB3275215BE20AD42A8025437D3DBCD5FA3AADE806F4CEE70DFB85188D2ED0C5B6E1BB5785C1D90AE75FE9F795635A94FD5C4DDB1A8B3E7B3084BA046943410692A4C46C30216EFB74D4B433E3A6ABA103AD99BEED4AF5DEDE56C94CDD2FD7E5323B7EA23F0A1AFC3D5371D3982388E437612E8D402E1B1A86D469EEB7061E2C2565D47684BFFE1474ADDE68A9D9442565BBE657A427278DA2AE30F8770E6E03691E08BE2917F2A61AF1885E03FD5D68484CB8CB2653E3682BF613782925EC97B6FE43EC8928191B6741021B999A742E15914DF04DF9264A8EC9AE51EFA2E131FA1636A2C580289E1B417F31FA5EB51840C7FB12F24B0E8999D258109B36658002F2E3

# 1F9282646F93227D3D504982F1FB3275215BE20AD42A8025437D3DBCD5FA3AADE806F4CEE70DFB85188D2ED0C5B6E1BB5785C1D90AE75FE9F795635A94FD5C4DFC263E32BB4C2426596D260C7FC29B91797AF14B719DACC851DA9C0C30E5224157FE5F799F189532BF6A9210FD1CB416B4EA01C1052BA0F925CC12044C0D0C7E8D402E1B1A86D469EEB7061E2C2565D4758D576AF9C43C3ACCA5147B6FF29324AB312E48AEF8B09CAF7C1126947A10ECBE2917F2A61AF1885E03FD5D68484CB8CB2653E3682BF613782925EC97B6FE43EC8928191B6741021B999A742E15914DE29DE68696B917A58ADDD9CB0EE56618AFC58B379956E600F157292496318BFE5312429E8204700C6C4BC09742588402