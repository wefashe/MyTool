
import os
import json
import time
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

async def send_message(ws, type):

    global client_sessionid
    proto_header = steammessages_base_pb2.CMsgProtoBufHeader()
    proto_header.steamid = 0
    proto_header.client_sessionid = client_sessionid
    proto_header_encoded = proto_header.SerializeToString() 

    if type == CLIENT_HELLO:

        proto_data = steammessages_clientserver_login_pb2.CMsgClientHello()
        proto_data.protocol_version = PROTOCOL_VERSION
        proto_data_encoded = proto_data.SerializeToString() 
        

    if type == SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED:
        refresh_token = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEVGMl8yNDM2MjkyOV9CNEFGRiIsICJzdWIiOiAiNzY1NjExOTkwMTIzODIwNzQiLCAiYXVkIjogWyAiY2xpZW50IiwgIndlYiIgXSwgImV4cCI6IDE3MTYwMTA1MTYsICJuYmYiOiAxNzA3MjgzNDMzLCAiaWF0IjogMTcxNTkyMzQzMywgImp0aSI6ICIxODA1XzI0NkVERDhBXzg5NTVBIiwgIm9hdCI6IDE3MTI0OTg3ODAsICJydF9leHAiOiAxNzMwNjIyNTM2LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTg5LjEwNy4yMS41OSIsICJpcF9jb25maXJtZXIiOiAiMTg5LjEwNy4yMS41OSIgfQ.toPmNGeTtidvFbKPdGb2RDwSnBxZKCKJGny5QO0Za7OszFhR_tbWN4x6iq6_w9dOjoVty5R0HqN7IlEaDFDBAA'
        parts = refresh_token.split('.')
        if len(parts) != 3:
            raise ValueError('Invalid JWT')
        standard_base64 = parts[1].replace('-', '+').replace('_', '/')
        data = json.loads(base64.b64decode(standard_base64 + '=' * (-len(standard_base64) % 4)).decode('utf-8'))

        proto_data = steammessages_auth_pb2.CAuthentication_AccessToken_GenerateForApp_Request()
        proto_data.refresh_token = refresh_token
        proto_data.steamid = int(data['sub'])
        proto_data_encoded = proto_data.SerializeToString() 

        targetName = 'Authentication.GenerateAccessTokenForApp#1';

        job_id_buffer = bytearray(os.urandom(8))
        job_id_buffer[0] &= 0x7f  
        job_id = int.from_bytes(job_id_buffer, 'big')

        proto_header.jobid_source = job_id
        proto_header.target_job_name = targetName
        proto_header.realm = 1

    header_encoded = bytearray(8)
    header_encoded[:4] = (type | PROTO_MASK).to_bytes(4, byteorder='little', signed=False)
    header_encoded[4:] = len(proto_header_encoded).to_bytes(4, byteorder='little', signed=False)
    await ws.send(header_encoded + proto_header_encoded + proto_data_encoded)

async def rece_message(ws, type):
    message = await ws.recv()
    if not isinstance(message, bytes):
        return
    rawEmsg = int.from_bytes(message[0:4], byteorder='little')
    hdrLength = int.from_bytes(message[4:8], byteorder='little')
    hdrBuf = message[8:8+hdrLength]
    msgBody = message[8+hdrLength:]
    if not rawEmsg & PROTO_MASK:
        raise ValueError(f"Received unexpected non-protobuf message {rawEmsg}")
    
    proto_header = steammessages_base_pb2.CMsgProtoBufHeader()
    proto_header.ParseFromString(hdrBuf) 
    print(proto_header)

    global client_sessionid
    if proto_header.client_sessionid != client_sessionid:
        client_sessionid = proto_header.client_sessionid

    eMsg = (rawEmsg & ~PROTO_MASK)  
    if eMsg != Multi:
        print(f'Receive: { eMsg} ({proto_header.target_job_name})')
    global jobs
    if proto_header.jobid_target:
        pass
    if eMsg == CLIENT_LOG_ON_RESPONSE: # 751时 换服务器
        response = steammessages_clientserver_login_pb2.CMsgClientLogonResponse()
        response.ParseFromString(msgBody) 
        print(response)
        print(f'Received ClientLogOnResponse with result: {response.eresult}')
        return False
    elif eMsg == Multi:
        pass
    else:
        print(f'Received unexpected message: {eMsg}')
        # steammessages_auth_pb2.CAuthentication_AccessToken_GenerateForApp_Response()

async def ws():
    async with websockets.connect(f'wss://ext2-hkg1.steamserver.net:27020/cmsocket/') as websocket:
        await send_message(websocket, CLIENT_HELLO)  
        await rece_message(websocket, CLIENT_HELLO)
         
        await send_message(websocket, SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED) 
        await rece_message(websocket, SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED) 



asyncio.get_event_loop().run_until_complete(ws())
