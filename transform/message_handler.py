import os
import gzip
import asyncio
import logging
import websockets

from emsg_enum import EMsg
from eresult_enum import EResult

import token_decode

import steammessages_clientserver_login_pb2
import steammessages_base_pb2
import steammessages_auth_pb2

logging.basicConfig(level=logging.DEBUG)

PROTO_MASK = 0x80000000
jobs = []

async def send_message(ws, emsg:EMsg, body):
    try:
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
    except websockets.ConnectionClosed as e:
        logging.ERROR(f"连接关闭，状态码: {e.code}, 原因: {e.reason}")
    except Exception as e:
        logging.ERROR(f"发送错误: {e}")

async def send_hello(ws):
    PROTOCOL_VERSION = 65580
    client_hello_builder = steammessages_clientserver_login_pb2.CMsgClientHello()
    client_hello_builder.protocol_version = PROTOCOL_VERSION
    client_hello_body = client_hello_builder.SerializeToString()

    await send_message(ws, EMsg.ClientHello, client_hello_body)

async def send_token(ws, token):
    accesstoken_request_builder = steammessages_auth_pb2.CAuthentication_AccessToken_GenerateForApp_Request()
    accesstoken_request_builder.refresh_token = token
    accesstoken_request_builder.steamid = int(token_decode.get_token_info(token)['sub'])
    accesstoken_request_body = accesstoken_request_builder.SerializeToString()
    await send_message(ws, EMsg.ServiceMethodCallFromClientNonAuthed, accesstoken_request_body)

async def read_file_lines(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()[7:]

async def handle_file(ws, file_path):
    tasks = []
    async for line in read_file_lines(file_path):
        obj = token_decode.get_token_info(line)
        print(obj['exp'])
        task = asyncio.create_task(send_token(ws, line))
        tasks.append(task)
        await asyncio.sleep(0.1)  # 控制发送速度
    await asyncio.gather(*tasks)  # 确保所有任务完成


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

def handle_message(message):
    rawEmsg = int.from_bytes(message[0:4], byteorder='little')
    hdrLength = int.from_bytes(message[4:8], byteorder='little')
    hdrBuf = message[8:8+hdrLength]
    msgBody = message[8+hdrLength:]
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
        
async def recv_message(ws):
    try:
        while True:
            message = await ws.recv()
            if not isinstance(message, bytes):
                continue
            handle_message(message)
    except websockets.ConnectionClosed as e:
        logging.ERROR(f"连接关闭，状态码: {e.code}, 原因: {e.reason}")
    except Exception as e:
        logging.ERROR(f"接收错误: {e}")

async def send_heart(ws, interval):
    await ws.send("PING")
    await asyncio.sleep(interval)