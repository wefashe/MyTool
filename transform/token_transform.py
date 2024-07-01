
import time
import random
import asyncio
import logging

import websockets

import steam_api
import message_handler

from queue import Queue
from concurrent.futures import ThreadPoolExecutor,as_completed

logging.basicConfig(level=logging.ERROR)


async def connect_cm(cmList, batch, success_queue, failure_queue):
    endpoint = cmList[random.randint(0, min(20, len(cmList)) - 1)]["endpoint"]
    logging.info(f"开始连接 {endpoint} ")
    async with websockets.connect(f'wss://{endpoint}/cmsocket/') as ws:
        logging.info(f"成功连接 {endpoint} ")

        logging.info("开始发送认证包")
        await message_handler.send_hello(ws)
        logging.info("成功发送认证包")

        key = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0'

        for refresh in batch:
            await message_handler.send_token(ws, refresh[refresh.find(key):])
            accesss = await message_handler.recv_message(ws)
            if accesss:
                success_queue.put((refresh, refresh[0:refresh.find(key)] + accesss))           
            else:
                failure_queue.put(refresh)

def start_websocket_connection(cmList, batch, success_queue, failure_queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_cm(cmList, batch, success_queue, failure_queue))


file_path = r'transform/test.txt'

def process_file_in_batches(file_path, batch_size):
    with open(file_path, 'r') as file:
        while True:
            batch = [file.readline().strip() for _ in range(batch_size)]
            # 过滤掉空行
            batch = [line for line in batch if line]
            if not batch:
                break
            yield batch


def main():

    start_time_insert = time.time()

    batch_size = 100  # 每批处理的行数
    max_workers = 10  # 最大线程数

    cmList = steam_api.get_cm_list()
    if not cmList or len(cmList) == 0:
        raise ValueError('未获取到服务器列表')

    success_queue = Queue()
    failure_queue = Queue()

    completed_task_count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for batch in process_file_in_batches(file_path, batch_size):
            future = executor.submit(start_websocket_connection, cmList, batch, success_queue, failure_queue)
            futures.append(future)
        for future in as_completed(futures):
            future.result()
            completed_task_count += 1
            print("已经完成 "+ str(completed_task_count))

    success_accesss_file_path = "临时成功.txt"
    success_refresh_file_path = "有效ey.txt"
    failure_refresh_file_path = "失败ey.txt"

    # 写入成功和失败的数据到文件
    with open(success_accesss_file_path, 'w') as success_accesss_file, \
        open(success_refresh_file_path, 'w') as success_refresh_file, \
            open(failure_refresh_file_path, 'w') as failure_refresh_file:
        while not success_queue.empty():
            refresh, accesss = success_queue.get()
            success_accesss_file.write(accesss+'\n')
            success_refresh_file.write(refresh+'\n')
        
        while not failure_queue.empty():
            refresh = failure_queue.get()
            failure_refresh_file.write(refresh+'\n')

    end_time_insert = time.time()
    insert_time = end_time_insert - start_time_insert
    print(f'转换完成, 耗时{insert_time:.6f}秒')
main()