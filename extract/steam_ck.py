import re
import requests
import json
import time
import base64
from bs4 import BeautifulSoup
from selenium import webdriver

url = 'https://help.steampowered.com'

host = re.findall(r'^(?:https?:\/\/)?([^\/]+)', url)[0]

ck = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEVGMl8yNDM2MjkyOV9CNEFGRiIsICJzdWIiOiAiNzY1NjExOTkwMTIzODIwNzQiLCAiYXVkIjogWyAiY2xpZW50IiwgIndlYiIgXSwgImV4cCI6IDE3MTYwMTA1MTYsICJuYmYiOiAxNzA3MjgzNDMzLCAiaWF0IjogMTcxNTkyMzQzMywgImp0aSI6ICIxODA1XzI0NkVERDhBXzg5NTVBIiwgIm9hdCI6IDE3MTI0OTg3ODAsICJydF9leHAiOiAxNzMwNjIyNTM2LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTg5LjEwNy4yMS41OSIsICJpcF9jb25maXJtZXIiOiAiMTg5LjEwNy4yMS41OSIgfQ.toPmNGeTtidvFbKPdGb2RDwSnBxZKCKJGny5QO0Za7OszFhR_tbWN4x6iq6_w9dOjoVty5R0HqN7IlEaDFDBAA'

# ck = input('输入CY: ').strip('666----').strip()

if '%7C%7C' in ck:
    ck = ck.split('%7C%7C')[1]
if '----' in ck:
    ck = ck.split('----')[0]

encodestr = ck.split('.')[1]
# base64字符串个数必须是4的倍数，不够后面补=号
if len(encodestr) % 4:
    encodestr += '=' * (4 - len(encodestr) % 4)
decodestr = base64.b64decode(encodestr, validate=True)
obj = json.loads(decodestr)

obj["exp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(obj["exp"]))
obj["nbf"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(obj["nbf"]))
obj["iat"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(obj["iat"]))
obj["oat"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(obj["oat"]))

if 'rt_exp' in obj: 
    obj["rt_exp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(obj["rt_exp"]))








print(json.dumps(obj, ensure_ascii=False, indent=2))
# iss: jwt签发者
# sub: jwt所面向的用户
# aud: 接收jwt的一方
# exp: jwt的过期时间，这个过期时间必须要大于签发时间
# nbf: 定义在什么时间之前，该jwt都是不可用的.
# iat: jwt的签发时间
# jti: jwt的唯一身份标识，主要用来作为一次性token。








headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': host,
    'Pragma': 'no-cache',
    'Referer': 'https://store.steampowered.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

# cookies = {
#     'steamLoginSecure': f'{obj["sub"]}%7C%7C{ck}'
# }

# print(f'666----steamLoginSecure={obj["sub"]}%7C%7C{ck}')

# browser = webdriver.Chrome()
# browser.get(url)
# browser.add_cookie(cookies)
# browser.refresh()


resp = requests.get('https://api.steampowered.com/ISteamUserOAuth/GetTokenDetails/v1/', headers=headers, params={
    'access_token': ck
} )
print(resp.content)
# resp = requests.get(url, headers=headers, cookies=cookies)

# cookies = resp.cookies
# for cookie in cookies:
#     print(f"Name: {cookie.name}, Value: {cookie.value}")

# soup = BeautifulSoup(resp.text, 'html.parser')
# menu = soup.find('div', id='global_action_menu')
# name = menu.find('span', id='account_pulldown').get_text().strip()
# # money = menu.find('a', id='header_wallet_balance').get_text().strip()

# print(f'登录用户名: {name}',  )