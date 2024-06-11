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

exp_time = get_exp_time(years=0,days=0, hours=0, minutes=1, seconds=0)
license_dict['exp'] = datetime.timestamp(exp_time)
iat_time = get_beijin_time()
license_dict['iat'] = datetime.timestamp(iat_time)

target_machine_code = '6BB85C7403A653DDC68F2DC0353CD32B'
license_dict['psw'] = target_machine_code
license_dict['jti'] =generate_jti()

license_str = str(license_dict)
print(license_str)
license_text = base64.b64encode(license_str.encode('utf-8'))
print(license_text.decode('utf-8'))

# 对加密数据进行补位
BLOCK_SIZE = AES.block_size # 16的倍数
# key长度必须是16, 24, 32
key = '9876543219876543'

cipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
encrypted_msg = cipher.encrypt(pad(license_text, BLOCK_SIZE))
msg_text = encrypted_msg.hex().upper()
print('卡密：',msg_text)


