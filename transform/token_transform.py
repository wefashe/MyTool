

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


                recv_task = asyncio.create_task(message_handler.recv_message(ws))

                while True:
                    file_path = input("请输入文件路径: ")
                    if file_path.lower() == 'exit':
                        break
                    await message_handler.handle_file(ws, file_path)

                recv_task.cancel() 

        except websockets.ConnectionClosed as e:
            logging.ERROR(f"Disconnected from {endpoint}: {e.code} ({e.reason})")
        except Exception as e:
            logging.ERROR(f"Error in WebSocket with {endpoint}: {e}")

asyncio.run(connect_to_cm())