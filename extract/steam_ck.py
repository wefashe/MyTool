import requests
import json
import base64
from bs4 import BeautifulSoup

ck = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEVGMl8yNDM2MjkyOV9CNEFGRiIsICJzdWIiOiAiNzY1NjExOTkwMTIzODIwNzQiLCAiYXVkIjogWyAiY2xpZW50IiwgIndlYiIgXSwgImV4cCI6IDE3MTYwMTA1MTYsICJuYmYiOiAxNzA3MjgzNDMzLCAiaWF0IjogMTcxNTkyMzQzMywgImp0aSI6ICIxODA1XzI0NkVERDhBXzg5NTVBIiwgIm9hdCI6IDE3MTI0OTg3ODAsICJydF9leHAiOiAxNzMwNjIyNTM2LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTg5LjEwNy4yMS41OSIsICJpcF9jb25maXJtZXIiOiAiMTg5LjEwNy4yMS41OSIgfQ.toPmNGeTtidvFbKPdGb2RDwSnBxZKCKJGny5QO0Za7OszFhR_tbWN4x6iq6_w9dOjoVty5R0HqN7IlEaDFDBAA'
encodestr = ck.split('.')[1]
if len(encodestr) % 4:
    encodestr += '=' * (4 - len(encodestr) % 4)
decodestr = base64.b64decode(encodestr, validate=True)
obj = json.loads(decodestr)
print(json.dumps(obj, ensure_ascii=False, indent=2))
header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': f'steamLoginSecure={obj["sub"]}%7C%7C{ck}',
    'DNT': '1',
    'Host': 'store.steampowered.com',
    'Pragma': 'no-cache',
    'Referer': 'https://store.steampowered.com/steamaccount/addfunds/',
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

resp = requests.get('https://store.steampowered.com/account/', headers=header)
soup = BeautifulSoup(resp.text, 'html.parser')
menu = soup.find('div', id='global_action_menu')
name = menu.find('span', id='account_pulldown').get_text().strip()
money = menu.find('a', id='header_wallet_balance').get_text().strip()

print(f'登录用户名: {name}, 钱包：{money}',  )