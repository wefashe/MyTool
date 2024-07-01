

import random
import asyncio
import logging

import websockets

import steam_api
import message_handler


logging.basicConfig(level=logging.DEBUG)

cmList = steam_api.get_cm_list()
if not cmList or len(cmList) == 0:
    raise ValueError('未获取到服务器列表')

async def connect_to_cm():
    while True:
        try:
            endpoint = cmList[random.randint(0, min(20, len(cmList)) - 1)]["endpoint"]
            logging.info(f"开始连接 {endpoint} ")
            async with websockets.connect(f'wss://{endpoint}/cmsocket/') as ws:
                logging.info(f"成功连接 {endpoint} ")

                logging.info("开始发送认证包")
                await message_handler.send_hello(ws)
                logging.info("成功发送认证包")

                while True:
                    refreshToken = input("\nrefresh_token: ")
                    if refreshToken.lower() == 'exit':
                        break
                    # refreshToken = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInN0ZWFtIiwgInN1YiI6ICI3NjU2MTE5OTE3NjgzMjExOCIsICJhdWQiOiBbICJjbGllbnQiLCAid2ViIiwgInJlbmV3IiwgImRlcml2ZSIgXSwgImV4cCI6IDE3MjgxNzkxODUsICJuYmYiOiAxNjg4NTk1MzA0LCAiaWF0IjogMTY5NzIzNTMwNCwgImp0aSI6ICIxNDU1XzIzNTBDMUJBX0UwQTA5IiwgIm9hdCI6IDE2OTcyMzUzMDQsICJnZW4iOiAxLCAicGVyIjogMSwgImlwX3N1YmplY3QiOiAiODIuMTEuMTU0LjUwIiwgImlwX2NvbmZpcm1lciI6ICI4Mi4xMS4xNTQuNTAiIH0.GDKSalpYq1c3f9NdPHqwxj3-QY_Jgx8by6GCAy1ftGraOK91b4TdQx9PGADTIc0U00K5JX3-GLsShO5xgXepDw'
                    await message_handler.send_token(ws, refreshToken)
                    try:
                        while True:
                            body = await ws.recv()
                            if not isinstance(body, bytes):
                                continue
                            message_handler.handle_message(body)
                            break
                    except websockets.exceptions.ConnectionClosedError as e:
                        logging.ERROR(f"recv Disconnected from {endpoint}: {e.code} ({e.reason})")
                    except Exception as e:
                        logging.ERROR(f"recv Error in WebSocket with {endpoint}: {e}")   
                    refreshToken = None  
        except websockets.ConnectionClosed as e:
            logging.ERROR(f"Disconnected from {endpoint}: {e.code} ({e.reason})")
        except Exception as e:
            logging.ERROR(f"Error in WebSocket with {endpoint}: {e}")

asyncio.run(connect_to_cm())