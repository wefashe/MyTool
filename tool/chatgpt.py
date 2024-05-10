import json
import requests

def get_result(prompt):    
    headers = {
        "authority": "api.binjie.fun",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://chat.jinshutuan.com",
        "pragma": "no-cache",
        "referer": "https://chat.jinshutuan.com/",
        "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    url = "https://api.binjie.fun/api/generateStream"

    data = {
        "prompt": "{}".format(prompt),
        "userId": "#/chat/1683173371474",
        "network": True,
        "system": "",
        "apikey":"",
        "withoutContext": True,
        "stream": True
    }
    data = json.dumps(data, separators=(',', ':'))
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.encoding = "utf-8"
        if response.status_code == 200:
            return response.text
    except BaseException:
        return "查询失败"
    
while True:
    prompt = input('问: ')
    if prompt == 'exit':
        break
    print('答:', get_result(prompt))
