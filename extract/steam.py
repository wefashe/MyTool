import os
import re
import json
import time
import base64

# iss: jwt签发者
# sub: jwt所面向的用户
# aud: 接收jwt的一方
# exp: jwt的过期时间，这个过期时间必须要大于签发时间
# nbf: 定义在什么时间之前，该jwt都是不可用的.
# iat: jwt的签发时间
# jti: jwt的唯一身份标识，主要用来作为一次性token。

def generate_jti():
    return  re.sub(r'^([0-9A-F]{4})([0-9A-F]{8})([0-9A-F]{5}).+', r'\1_\2_\3',  os.urandom(9).hex().upper())

steamid = '76561198110478321'
aud = ['client', 'web']

now = int(time.time())
myip = '.'.join(map(str, os.urandom(4)))

refresh_token_data = {
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

guard_data = {
    **refresh_token_data,
    'iss': f"r:{refresh_token_data['jti']}",
    'aud': ['machine'],
    'jti': generate_jti(),
    'rt_exp': refresh_token_data['exp'],
    'per': 0
};

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

print('refreshToken: ', encode_jwt(refresh_token_data))
print('guardData: ', encode_jwt(guard_data))


session_client_id = str(int.from_bytes(os.urandom(8), byteorder='big', signed=False))
print(session_client_id)