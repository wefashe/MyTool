import json
import random
import requests
import pickle
import asyncio
import websockets

# 获取 CM (Connection Manager) 服务器列表 用于 Steam 帐户登录认证、好友在线状态、聊天和游戏邀请等等方面 
# cellid 地区相关id， format 格式, vdf js xml
url = 'https://api.steampowered.com/ISteamDirectory/GetCMListForConnect/v0001/?cellid=0&format=js'
headers = {
    'user-agent': 'Valve/Steam HTTP Client 1.0',
    'accept-charset': 'ISO-8859-1,utf-8,*;q=0.7',
    'accept': 'text/html,*/*;q=0.9'
}
resp = requests.get(url, headers=headers)
resp_json = resp.json()
if not resp_json['response'] or not resp_json['response']['success'] or not resp_json['response']['serverlist']:
    exit()

cmList = resp_json['response']['serverlist']

cmList = sorted(cmList, key=lambda x: x["wtd_load"])

cmList = [server for server in cmList if server['type'] =='websockets' and server['realm'] == 'steamglobal']

rand_upper_bound = min(20, len(cmList))
cm = cmList[random.randint(0, rand_upper_bound - 1)]

# print(json.dumps(serverlist, ensure_ascii=False, indent=2))

async def main(cm):
    async with websockets.connect(f'wss://{cm["endpoint"]}/cmsocket/') as websocket:
        message = "Hello, server!"
        #         protoHeader = {
        #     'steamid': '0',
        #     'client_sessionid':  0,
        # };
        await websocket.send(message)
        print(f"Sent: {message}")

        response = await websocket.recv()
        if type(response) == 'bytes':
            print(f'Received unexpected frame type from {cm["endpoint"]}: {type(response)}')
        print(f"Received: {response}")

asyncio.get_event_loop().run_until_complete(main(cm))

