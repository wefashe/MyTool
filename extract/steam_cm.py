
import os
import json
import base64
import asyncio
import websockets
import steammessages_auth_pb2
import steammessages_base_pb2
import steammessages_clientserver_login_pb2
from google.protobuf import json_format

PROTOCOL_VERSION = 65580
PROTO_MASK = 0x80000000
Multi = 1
CLIENT_HELLO = 9805
SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED = 9804
CLIENT_LOG_ON_RESPONSE = 751

client_sessionid = 0

async def send_message(ws, send_type):

    global client_sessionid
    proto_header = steammessages_base_pb2.CMsgProtoBufHeader()
    proto_header.steamid = 0
    proto_header.client_sessionid = client_sessionid
    if send_type == CLIENT_HELLO:

        proto_data = steammessages_clientserver_login_pb2.CMsgClientHello()
        proto_data.protocol_version = PROTOCOL_VERSION
        proto_data_buffer = proto_data.SerializeToString() 
        

    if send_type == SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED:
        refresh_token = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEVGMl8yNDM2MjkyOV9CNEFGRiIsICJzdWIiOiAiNzY1NjExOTkwMTIzODIwNzQiLCAiYXVkIjogWyAiY2xpZW50IiwgIndlYiIgXSwgImV4cCI6IDE3MTYwMTA1MTYsICJuYmYiOiAxNzA3MjgzNDMzLCAiaWF0IjogMTcxNTkyMzQzMywgImp0aSI6ICIxODA1XzI0NkVERDhBXzg5NTVBIiwgIm9hdCI6IDE3MTI0OTg3ODAsICJydF9leHAiOiAxNzMwNjIyNTM2LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTg5LjEwNy4yMS41OSIsICJpcF9jb25maXJtZXIiOiAiMTg5LjEwNy4yMS41OSIgfQ.toPmNGeTtidvFbKPdGb2RDwSnBxZKCKJGny5QO0Za7OszFhR_tbWN4x6iq6_w9dOjoVty5R0HqN7IlEaDFDBAA'
        parts = refresh_token.split('.')
        if len(parts) != 3:
            raise ValueError('Invalid JWT')
        standard_base64 = parts[1].replace('-', '+').replace('_', '/')
        data = json.loads(base64.b64decode(standard_base64 + '=' * (-len(standard_base64) % 4)).decode('utf-8'))

        proto_data = steammessages_auth_pb2.CAuthentication_AccessToken_GenerateForApp_Request()
        proto_data.refresh_token = refresh_token
        proto_data.steamid = int(data['sub'])
        proto_data_buffer = proto_data.SerializeToString() 

        targetName = 'Authentication.GenerateAccessTokenForApp#1';

        # 生成包含 8 个随机字节的缓冲区
        job_id_buffer = bytearray(os.urandom(8))
        job_id_buffer[0] &= 0x7f  
        job_id = int.from_bytes(job_id_buffer, 'big')

        proto_header.jobid_source = job_id
        proto_header.target_job_name = targetName
        proto_header.realm = 1

    proto_header_buffer = proto_header.SerializeToString() 
    # 创建一个包含 8 个字节的缓冲区，并将所有字节的值初始化为 0
    header_buffer = bytearray(8)
    header_buffer[0:4] = (send_type | PROTO_MASK).to_bytes(4, byteorder='little', signed=False)
    header_buffer[4:8] = len(proto_header_buffer).to_bytes(4, byteorder='little', signed=False)
    await ws.send(header_buffer + proto_header_buffer + proto_data_buffer)

async def recv_message(ws, recv_type):
    message = await ws.recv()
    if not isinstance(message, bytes):
        return
    # 读取字节数组前4位
    msg_type = int.from_bytes(message[0:4], byteorder='little', signed=False) & (~PROTO_MASK)
    # 读取字节数组4到8位
    header_length = int.from_bytes(message[4:8], byteorder='little', signed=False)
    # 数组8位到8+hdrLength位
    header_buffer = message[8: 8+header_length]
    # 数组8+hdrLength位之后
    proto_data_buffer = message[8 + header_length:]
    
    print('msg_type: ', msg_type)
    proto_header = steammessages_base_pb2.CMsgProtoBufHeader()
    proto_header.ParseFromString(header_buffer) 
    print(proto_header)

    global client_sessionid
    if proto_header.client_sessionid != client_sessionid:
        client_sessionid = proto_header.client_sessionid

    proto_data = steammessages_auth_pb2.CAuthentication_AccessToken_GenerateForApp_Response()
    proto_data.ParseFromString(proto_data_buffer) 
    print(proto_data)
    
    response = steammessages_clientserver_login_pb2.CMsgClientLogonResponse()
    response.ParseFromString(proto_data_buffer) 
    print(response)

    

async def ws():
    async with websockets.connect(f'wss://ext6-hkg1.steamserver.net:27037/cmsocket/') as websocket:
        await send_message(websocket, CLIENT_HELLO)  
        await recv_message(websocket, CLIENT_HELLO)
         
        await send_message(websocket, SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED) 
        await recv_message(websocket, SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED) 



asyncio.get_event_loop().run_until_complete(ws())
