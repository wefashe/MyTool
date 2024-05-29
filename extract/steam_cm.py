
import os
import json
import base64
import asyncio
import websockets
import steammessages_auth_pb2
import steammessages_base_pb2
import steammessages_clientserver_login_pb2
from google.protobuf import json_format



def encode(proto, obje): # 编码
    return json_format.Parse(json.dumps(obje), proto).SerializeToString()
def decode(proto, msge): # 解码
    proto.ParseFromString(msge)
    return json.loads(json_format.MessageToJson(proto))



PROTO_MASK = 0x80000000
Multi = 1
CLIENT_HELLO = 9805
SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED = 9804
CLIENT_LOG_ON_RESPONSE = 751

async def send_message(ws):
    refresh_token = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEVGMl8yNDM2MjkyOV9CNEFGRiIsICJzdWIiOiAiNzY1NjExOTkwMTIzODIwNzQiLCAiYXVkIjogWyAiY2xpZW50IiwgIndlYiIgXSwgImV4cCI6IDE3MTYwMTA1MTYsICJuYmYiOiAxNzA3MjgzNDMzLCAiaWF0IjogMTcxNTkyMzQzMywgImp0aSI6ICIxODA1XzI0NkVERDhBXzg5NTVBIiwgIm9hdCI6IDE3MTI0OTg3ODAsICJydF9leHAiOiAxNzMwNjIyNTM2LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTg5LjEwNy4yMS41OSIsICJpcF9jb25maXJtZXIiOiAiMTg5LjEwNy4yMS41OSIgfQ.toPmNGeTtidvFbKPdGb2RDwSnBxZKCKJGny5QO0Za7OszFhR_tbWN4x6iq6_w9dOjoVty5R0HqN7IlEaDFDBAA'
    parts = refresh_token.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid JWT')
    standard_base64 = parts[1].replace('-', '+').replace('_', '/')
    data = json.loads(base64.b64decode(standard_base64 + '=' * (-len(standard_base64) % 4)).decode('utf-8'))

    proto_data = {
        'refresh_token': refresh_token,
        'steamid': data['sub'],
        'renewal_type': 0
    }

    proto_data_encoded = encode(steammessages_auth_pb2._CAUTHENTICATION_ACCESSTOKEN_GENERATEFORAPP_REQUEST(), proto_data)

    targetName = 'Authentication.GenerateAccessTokenForApp#1';

    job_id_buffer = bytearray(os.urandom(8))
    job_id_buffer[0] &= 0x7f  
    job_id = int.from_bytes(job_id_buffer, 'big')

    proto_header = {
        'steamid': '0',
        'client_sessionid': '0',
        'jobid_source': job_id,
        'target_job_name': targetName,
        'realm': 1
    }
    proto_header_encoded = encode(steammessages_base_pb2.CMsgProtoBufHeader(), proto_header)

    header_encoded = bytearray(8)
    header_encoded[:4] = (SERVICE_METHOD_CALL_FROM_CLIENT_NON_AUTHED | PROTO_MASK).to_bytes(4, byteorder='little', signed=False)
    header_encoded[4:] = len(proto_header_encoded).to_bytes(4, byteorder='little', signed=False)
    await ws.send(header_encoded + proto_header_encoded + proto_data_encoded)

async def rece_message(message):
    if not isinstance(message, bytes):
        return
    rawEmsg = int.from_bytes(message[0:4], byteorder='little')
    hdrLength = int.from_bytes(message[4:8], byteorder='little')
    hdrBuf = message[8:8+hdrLength]
    msgBody = message[8+hdrLength:]
    if not rawEmsg & PROTO_MASK:
        raise ValueError(f"Received unexpected non-protobuf message {rawEmsg}")
    msg_proto_buf_header = decode( steammessages_base_pb2.CMsgProtoBufHeader(), hdrBuf)
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
        log_on_response = decode( steammessages_clientserver_login_pb2.CMsgClientLogonResponse(), msgBody)
        print(f'Received ClientLogOnResponse with result: {log_on_response.get("eresult")}')
        return False
    elif eMsg == Multi:
        pass
    else:
        print(f'Received unexpected message: {eMsg}')
        steammessages_auth_pb2._CAUTHENTICATION_ACCESSTOKEN_GENERATEFORAPP_RESPONSE()

async def ws():
    async with websockets.connect(f'wss://ext4-hkg1.steamserver.net:27024/cmsocket/') as websocket:
         await send_message(websocket)
         message = await asyncio.wait_for(websocket.recv(), timeout=10)      
         await rece_message(message)    


asyncio.get_event_loop().run_until_complete(ws())
