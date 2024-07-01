
import time
import base64
import json
import re
import os

def generate_jti():
    return  re.sub(r'^([0-9A-F]{4})([0-9A-F]{8})([0-9A-F]{5}).+', r'\1_\2_\3',\
                     os.urandom(9).hex().upper())

# 定义urlSafeBase64函数
def url_safe_base64(input):
    if not isinstance(input, bytes):
        input = input.encode('utf-8')
    encoded = base64.b64encode(input).decode('utf-8')
    return encoded.replace('+', '-').replace('/', '_').rstrip('=')

def encode_jwt(body):
    header = {
        'typ': 'JWT',
        'alg': 'EdDSA'
    }
    signature = os.urandom(64)
    # 对头部、主体和签名进行处理，并拼接它们
    result = '.'.join(map(url_safe_base64, [json.dumps(header), json.dumps(body), signature]))

    return result

def generate_refresh_token_obj(steamid:str, aud, myip:str) -> dict:
    # iss: jwt签发者
    # sub: jwt所面向的用户
    # aud: 接收jwt的一方
    # exp: jwt的过期时间，这个过期时间必须要大于签发时间
    # nbf: 定义在什么时间之前，该jwt都是不可用的.
    # iat: jwt的签发时间
    # jti: jwt的唯一身份标识，主要用来作为一次性token。
    now = int(time.time())
    refresh_token_obj = {
        'iss': 'steam',
        'sub': steamid,
        'aud': aud + ['renew', 'derive'],
        'exp': now + (60 * 60 * 24 * 200),
        'nbf': now - (60 * 60 * 24 * 100),
        'iat': now,
        'jti': generate_jti(),
        'oat': now,
        'per': 1,
        'ip_subject': myip,
        'ip_confirmer': myip
    } 
    return refresh_token_obj

def generate_refresh_token(refresh_token_obj:dict) -> str:
    return encode_jwt(refresh_token_obj)

def generate_access_token(refresh_token_obj:dict) -> str:
    access_token_obj = {
        **refresh_token_obj,
        'iss': f"r:{refresh_token_obj['jti']}",
        'aud': ['machine'],
        'jti': generate_jti(),
        'rt_exp': refresh_token_obj['exp'],
        'per': 0
    }
    return encode_jwt(access_token_obj)


if __name__ == '__main__':
    steamid = '76561198110478321'
    aud = ['client', 'web']
    myip = '.'.join(map(str, os.urandom(4)))
    refresh_token_obj = generate_refresh_token_obj(steamid, aud, myip)
    print('refresh_token:', generate_refresh_token(refresh_token_obj))
    print('access_token:', generate_access_token(refresh_token_obj))