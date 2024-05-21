import json
import random
import requests
import asyncio
import websockets
from google.protobuf import json_format
import steammessages_clientserver_login_pb2 as steammessages__clientserver__login__pb2
import steammessages_base_pb2 as steammessages__base__pb2

def get_cm_server(): # 随机获取服务器信息
    global cmList 
    if 'cmList' not in globals() or len(cmList) == 0:
        # 获取 CM (Connection Manager) 服务器列表 用于 Steam 帐户登录认证、好友在线状态、聊天和游戏邀请等等方面 
        # cellid 地区相关id， format 格式, vdf js xml
        # https://api.steampowered.com/ISteamDirectory/GetCMList/v0001/?cellid=0&format=js
        # https://api.steampowered.com/ISteamDirectory/GetCMList/v1/?cellid=148&steamrealm=steamchina
        url = 'https://api.steampowered.com/ISteamDirectory/GetCMListForConnect/v0001/?cellid=0&format=js'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            resp_json = resp.json()
            if not resp_json['response'] or not resp_json['response']['success'] or not resp_json['response']['serverlist']:
                return {}
            cmList = resp_json['response']['serverlist']
            # endpoint：一个必需的字符串属性，用于指定服务器的端点。
            # legacy_endpoint：一个可选的字符串属性，用于指定旧版本服务器的端点。
            # type：一个必需的字符串属性，用于指定服务器类型。
            # dc：一个可选的字符串属性，用于指定数据中心。
            # realm：一个必需的字符串属性，用于指定服务器所属的领域。
            # load：一个可选的字符串属性，用于指定服务器的负载情况。
            # wtd_load：一个可选的字符串属性，可能用于指定服务器的另一种负载情况。
            cmList = [server for server in cmList if server['type'] =='websockets' and server['realm'] == 'steamglobal']
            cmList = sorted(cmList, key=lambda x: x["wtd_load"])
            # print(json.dumps(cmList, ensure_ascii=False, indent=2))
        except requests.exceptions.ConnectionError as e:
            raise ValueError('网络连接异常: ', e)
        except requests.exceptions.Timeout as e:
            raise ValueError('连接超时: ', e)
        except requests.exceptions.RequestException as e:
            raise ValueError('请求异常: ', e)
        except requests.exceptions.HTTPError as e:
            raise ValueError(f'HTTP错误, 状态码: {e.response.status_code}, {e}')
        except ValueError as e:
            print('响应解析异常: ', e)
    return cmList[random.randint(0, min(20, len(cmList)) - 1)]

def encode(proto, obje): # 编码
    return json_format.Parse(json.dumps(obje), proto).SerializeToString()
def decode(proto, msge): # 解码
    proto.ParseFromString(msge)
    return json.loads(json_format.MessageToJson(proto))

async def ping(ws): # 心跳检测
    while True:
        try:
            await ws.send('ping')
            await asyncio.sleep(10)
        except:
            break

PROTO_MASK = 0x80000000
PROTOCOL_VERSION = 65580

Multi = 1
CLIENT_HELLO = 9805
SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED = 9804
CLIENT_LOG_ON_RESPONSE = 751

client_session_id = 0
jobs = []

async def send_message(ws, msg_type, body, target_job_name):
    msg_proto_buf_header = {
        'steamid': '0',
        'client_sessionid':  client_session_id if msg_type != SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED else 0
    }
    if msg_type == SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED:
        pass
    encoded_msg_proto_buf_header = encode(steammessages__base__pb2.CMsgProtoBufHeader(), msg_proto_buf_header)
    header = bytearray(8)
    header[:4] = (msg_type | PROTO_MASK).to_bytes(4, byteorder='little', signed=False)
    header[4:] = len(encoded_msg_proto_buf_header).to_bytes(4, byteorder='little', signed=False)
    await ws.send(header + encoded_msg_proto_buf_header + body)
    return True

async def handle_message(body):
    if not isinstance(body, bytes):
        return
    rawEmsg = int.from_bytes(body[0:4], byteorder='little')
    hdrLength = int.from_bytes(body[4:8], byteorder='little')
    hdrBuf = body[8:8+hdrLength]
    msgBody = body[8+hdrLength:]
    if not rawEmsg & PROTO_MASK:
        raise ValueError(f"Received unexpected non-protobuf message {rawEmsg}")
    msg_proto_buf_header = decode( steammessages__base__pb2.CMsgProtoBufHeader(), hdrBuf)
    print('msg_proto_buf_header: ', msg_proto_buf_header)
    global client_session_id 
    if msg_proto_buf_header['clientSessionid'] and msg_proto_buf_header['clientSessionid'] != client_session_id:
        print(f'Got new client session id {msg_proto_buf_header["clientSessionid"]}');
        client_session_id = msg_proto_buf_header['clientSessionid']
    eMsg = (rawEmsg & ~PROTO_MASK)  
    if eMsg != Multi:
        print(f'Receive: { eMsg} ({msg_proto_buf_header.get("target_job_name")})')
    global jobs
    if msg_proto_buf_header.get('jobid_target') and jobs[msg_proto_buf_header.get('jobid_target')]:
        pass
    if eMsg == CLIENT_LOG_ON_RESPONSE: # 751时 换服务器
        log_on_response = decode( steammessages__clientserver__login__pb2.CMsgClientLogonResponse(), msgBody)
        print(f'Received ClientLogOnResponse with result: {log_on_response.get("eresult")}')
        return False
    elif eMsg == Multi:
        pass
    else:
        print(f'Received unexpected message: {eMsg}')
    return True

async def main():
    while True: # 换服务器
        cm = get_cm_server()
        while True: # 断线重连
            try:
                endpoint = cm["endpoint"]
                async with websockets.connect(f'wss://{endpoint}/cmsocket/') as websocket:
                    print(f'Connecting to {endpoint}')
                    msg_client_hello = {
                        'protocol_version': PROTOCOL_VERSION
                    }
                    encoded_msg_client_hello = encode( steammessages__clientserver__login__pb2.CMsgClientHello(), msg_client_hello)

                    targetName = 'Authentication.GetAuthSessionInfo#1';
                    # CAuthentication_GetAuthSessionInfo_Request
                    # CAuthentication_GetAuthSessionInfo_Response
                    encoded_msg_client_hello = encode( steammessages__clientserver__login__pb2.CMsgClientHello(), msg_client_hello)
                    
                    send_result = await send_message(websocket, CLIENT_HELLO, encoded_msg_client_hello, targetName)
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
                            handle_result = await handle_message(response)
                            if not handle_result:
                                break
                            return # 结束方法
                break
            except ConnectionRefusedError as e:
                print(e)
                global count
                # 重连3次
                if count == 3:  
                    break
                count += 1
                await asyncio.sleep(2)

asyncio.get_event_loop().run_until_complete(main())

