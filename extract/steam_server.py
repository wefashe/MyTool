
import json
import random
import requests
import asyncio
import websockets
from google.protobuf import json_format
import steammessages_clientserver_login_pb2 as steammessages__clientserver__login__pb2
import steammessages_base_pb2 as steammessages__base__pb2

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
# print(json.dumps(cmList, ensure_ascii=False, indent=2))

def get_cm_server(): # 随机获取服务器信息
    return cmList[random.randint(0, min(20, len(cmList)) - 1)]
def encode(proto, obje): # 编码
    return json_format.Parse(json.dumps(obje), proto).SerializeToString()
def decode(proto, msge): # 解码
    proto.ParseFromString(msge)
    return json_format.MessageToJson(proto)
async def ping(ws): # 心跳检测
    while True:
        try:
            await ws.send('ping')
            await asyncio.sleep(10)
        except:
            break


async def main():
    while True: # 换服务器
        cm = get_cm_server()
        while True: # 断线重连
            try:
                print(f'Connecting to {cm["endpoint"]}')
                async with websockets.connect(f'wss://{cm["endpoint"]}/cmsocket/') as websocket:
                    encoded_client_Hello = encode( steammessages__clientserver__login__pb2.CMsgClientHello(), {
                        'protocol_version': 65580
                    })

                    encoded_proto_buf_header = encode( steammessages__base__pb2.CMsgProtoBufHeader(), {
                        'steamid': '0',
                        'client_sessionid': 0
                    })

                    header = bytearray(8)
                    PROTO_MASK = 0x80000000
                    header[:4] = (9805 | PROTO_MASK).to_bytes(4, byteorder='little', signed=False)
                    header[4:] = len(encoded_proto_buf_header).to_bytes(4, byteorder='little', signed=False)
                    await websocket.send(header + encoded_proto_buf_header + encoded_client_Hello)

                    asyncio.create_task(ping(websocket))

                    timeout = 1000
                    while True: 
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=timeout)            
                        except websockets.exceptions.ConnectionClosed as e:
                            # 1000 正常关闭码 1006 服务端内部错误异常关闭码
                            print(e)
                            if e.code == 1006:
                                print('restart')
                                await asyncio.sleep(2)
                                break
                        except asyncio.TimeoutError:
                            print(f'Connecting to {cm["endpoint"]} timed out after {timeout} ms')
                            timeout = min(1000, timeout * 2)
                        else:
                            if type(response) == 'bytes':
                                print(f'Received unexpected frame type from {cm["endpoint"]}: {type(response)}')
                            print(f"Received: {response}")
                            rawEmsg = int.from_bytes(response[0:4], byteorder='little')
                            hdrLength = int.from_bytes(response[4:8], byteorder='little')
                            hdrBuf = response[8:8+hdrLength]
                            msgBody = response[8+hdrLength:]

                            if not rawEmsg & PROTO_MASK:
                                raise ValueError(f"Received unexpected non-protobuf message {rawEmsg}")
                            
                            result = decode( steammessages__base__pb2.CMsgProtoBufHeader(), hdrBuf)

                            print('decoded: ', result)
                            eMsg = (rawEmsg & ~PROTO_MASK)  
                            if eMsg != 1:
                                print(f'11111111111')
                            print('eMsg', eMsg, 'cm', cm["endpoint"])
                            if eMsg == 751: # 751时 换服务器
                                result = decode( steammessages__clientserver__login__pb2.CMsgClientLogonResponse(), msgBody)
                                print(result)
                                break


                            # TODO  具体业务

                            return # 结束方法
            except ConnectionRefusedError as e:
                print(e)
                global count
                # 重连3次
                if count == 3:  
                    return
                count += 1
                await asyncio.sleep(2)

asyncio.get_event_loop().run_until_complete(main())

