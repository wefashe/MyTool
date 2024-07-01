import os
import json
import gzip
import base64
import random
import asyncio
import logging
import requests
import websockets
import token_decode

from emsg_enum import EMsg
from eresult_enum import EResult

import steammessages_clientserver_login_pb2
import steammessages_base_pb2
import steammessages_auth_pb2

logging.basicConfig(level=logging.DEBUG)

def get_cm_list():
    # 获取 CM (Connection Manager) 服务器列表 用于 Steam 帐户登录认证、好友在线状态、聊天和游戏邀请等等方面 
    # cellid 地区相关id， format 格式, vdf js xml
    # https://api.steampowered.com/ISteamDirectory/GetCMList/v0001/?cellid=0&format=js
    # https://api.steampowered.com/ISteamDirectory/GetCMList/v1/?cellid=148&steamrealm=steamchina
    url = 'https://api.steampowered.com/ISteamDirectory/GetCMListForConnect/v0001/?cellid=0&format=js'
    headers = {
        'user-agent': 'Valve/Steam HTTP Client 1.0',
        'accept-charset': 'ISO-8859-1,utf-8,*;q=0.7',
        'accept': 'text/html,*/*;q=0.9'
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    resp_json = resp.json()
    cmList = resp_json['response']['serverlist']
    cmList = [server for server in cmList if server['type'] =='websockets' and server['realm'] == 'steamglobal']
    cmList = sorted(cmList, key=lambda x: x["wtd_load"])
    # print(json.dumps(cmList, ensure_ascii=False, indent=2))
    return cmList

cmList = get_cm_list()

PROTO_MASK = 0x80000000
jobs = []

async def send_message(ws, emsg:EMsg, body):
    proto_buf_header_builder = steammessages_base_pb2.CMsgProtoBufHeader()
    proto_buf_header_builder.steamid = 0
    proto_buf_header_builder.client_sessionid = 0
    if emsg == EMsg.ServiceMethodCallFromClientNonAuthed:
        jobIdBuffer = bytearray(os.urandom(8))
        jobIdBuffer[0] &= 0x7F
        jobId = int.from_bytes(jobIdBuffer, byteorder='big', signed=False)
        jobs.append(jobId)
        proto_buf_header_builder.jobid_source = jobId
        proto_buf_header_builder.target_job_name = 'Authentication.GenerateAccessTokenForApp#1'
        proto_buf_header_builder.realm = 1
    proto_buf_header_body = proto_buf_header_builder.SerializeToString()
    header = bytearray(8)
    header[:4] = (emsg.value | PROTO_MASK).to_bytes(4, byteorder='little', signed=False)
    header[4:] = len(proto_buf_header_body).to_bytes(4, byteorder='little', signed=False)
    await ws.send(header + proto_buf_header_body + body)

def handle_message(body):
    rawEmsg = int.from_bytes(body[0:4], byteorder='little')
    hdrLength = int.from_bytes(body[4:8], byteorder='little')
    hdrBuf = body[8:8+hdrLength]
    msgBody = body[8+hdrLength:]
    if not rawEmsg & PROTO_MASK:
        raise ValueError(f"Received unexpected non-protobuf message {rawEmsg}")
    proto_buf_header = steammessages_base_pb2.CMsgProtoBufHeader()
    proto_buf_header.ParseFromString(hdrBuf)
    eMsg:EMsg = EMsg(rawEmsg & ~PROTO_MASK)
    if proto_buf_header.jobid_target in jobs:
        jobs.remove(proto_buf_header.jobid_target) 
        result:EResult = EResult(proto_buf_header.eresult)
        if result == EResult.OK:
            accesstoken_response = steammessages_auth_pb2.CAuthentication_AccessToken_GenerateForApp_Response()
            accesstoken_response.ParseFromString(msgBody)
            print('access_token:', accesstoken_response.access_token)
            print('cookie:','steamLoginSecure='+ token_decode.get_cookie(accesstoken_response.access_token))
        else:
            error_message = proto_buf_header.error_message
            print(result, error_message)
        return
    if eMsg == EMsg.ClientLogOnResponse:
        logon_response = steammessages_clientserver_login_pb2.CMsgClientLogonResponse()
        result:EResult = EResult(logon_response.eresult)
        if result == EResult.OK:
            pass
        elif result == EResult.TryAnotherCM or result == EResult.ServiceUnavailable:
            print(result)
    elif eMsg == EMsg.Multi:
        process_multi_msg(msgBody)
    else:
        print(f'Received unexpected message: {eMsg}')

def process_multi_msg(body):
    multi = steammessages_base_pb2.CMsgMulti()
    multi.ParseFromString(body)
    payload = multi.message_body
    if multi.size_unzipped > 0:
        payload = gzip.decompress(payload)
    while len(payload) > 0:
        chunkSize = int.from_bytes(payload[0:4], byteorder='little')
        handle_message(payload[4:4+chunkSize])
        payload = payload[4+chunkSize:]

def decode_jwt(jwt: str) -> dict:
    parts = jwt.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid JWT')
    standard_base64 = parts[1].replace('-', '+').replace('_', '/')
    padded_base64 = standard_base64 + '=' * (4 - len(standard_base64) % 4)
    decoded_bytes = base64.b64decode(padded_base64)
    decoded_str = decoded_bytes.decode('utf-8')
    return json.loads(decoded_str)


async def connect_to_cm():
    while True:
        cm = cmList[random.randint(0, min(20, len(cmList)) - 1)]
        endpoint = cm["endpoint"]
        logging.debug(f"Received message: {endpoint}")
        try:
            async with websockets.connect(f'wss://{endpoint}/cmsocket/') as ws:

                logging.debug(f"Connected to {endpoint}")

                PROTOCOL_VERSION = 65580
                client_hello_builder = steammessages_clientserver_login_pb2.CMsgClientHello()
                client_hello_builder.protocol_version = PROTOCOL_VERSION
                client_hello_body = client_hello_builder.SerializeToString()

                await send_message(ws, EMsg.ClientHello, client_hello_body)

                while True:
                    refreshToken = input("\nrefresh_token: ")
                    if refreshToken.lower() == 'exit':
                        break
                    # refreshToken = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInN0ZWFtIiwgInN1YiI6ICI3NjU2MTE5OTE3NjgzMjExOCIsICJhdWQiOiBbICJjbGllbnQiLCAid2ViIiwgInJlbmV3IiwgImRlcml2ZSIgXSwgImV4cCI6IDE3MjgxNzkxODUsICJuYmYiOiAxNjg4NTk1MzA0LCAiaWF0IjogMTY5NzIzNTMwNCwgImp0aSI6ICIxNDU1XzIzNTBDMUJBX0UwQTA5IiwgIm9hdCI6IDE2OTcyMzUzMDQsICJnZW4iOiAxLCAicGVyIjogMSwgImlwX3N1YmplY3QiOiAiODIuMTEuMTU0LjUwIiwgImlwX2NvbmZpcm1lciI6ICI4Mi4xMS4xNTQuNTAiIH0.GDKSalpYq1c3f9NdPHqwxj3-QY_Jgx8by6GCAy1ftGraOK91b4TdQx9PGADTIc0U00K5JX3-GLsShO5xgXepDw'
                    accesstoken_request_builder = steammessages_auth_pb2.CAuthentication_AccessToken_GenerateForApp_Request()
                    accesstoken_request_builder.refresh_token = refreshToken
                    accesstoken_request_builder.steamid = int(decode_jwt(refreshToken)['sub'])
                    accesstoken_request_body = accesstoken_request_builder.SerializeToString()
                    await send_message(ws, EMsg.ServiceMethodCallFromClientNonAuthed, accesstoken_request_body)
                    try:
                        while True:
                            body = await ws.recv()
                            if not isinstance(body, bytes):
                                continue
                            handle_message(body)
                            break
                    except websockets.exceptions.ConnectionClosedError as e:
                        logging.debug(f"recv Disconnected from {endpoint}: {e.code} ({e.reason})")
                    except Exception as e:
                        logging.debug(f"recv Error in WebSocket with {endpoint}: {e}")   
                    refreshToken = None  
        except websockets.ConnectionClosed as e:
            logging.debug(f"Disconnected from {endpoint}: {e.code} ({e.reason})")
        except Exception as e:
            logging.debug(f"Error in WebSocket with {endpoint}: {e}")

asyncio.run(connect_to_cm())