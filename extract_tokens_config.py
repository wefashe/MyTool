#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
提取文件夹里所有带password的txt文件, 提取里面是邮箱的账户名和密码
pyinstaller -F extract_email.py
'''

import os
import re
import glob
import time

while True:
    try:
        work_path = input('请输入要处理的文件夹: ').strip('"').strip('&').strip("'").strip()
    except KeyboardInterrupt:
        # 键盘中断操作，防止报错
        exit_choose = input("\n您真的要退出吗?(y/n): ")
        if exit_choose.lower() == 'y':
            exit()
        continue
    except Exception as e:
        print(f'输入的文件目录有误 {e}')
        continue
    if not work_path: continue
    if not os.path.exists(work_path):
        print(f'文件路径不存在 -> {work_path}')
        continue
    break

work_path_name = os.path.join(glob.escape(work_path), "**",'[cCtT]o[nk][fe][in][gs].[tv][xd][tf]')
files_iterator  = glob.iglob( work_path_name, recursive=True)

result_path = os.path.join(os.getcwd(), 'result')
if not os.path.exists(result_path):
    os.makedirs(result_path)

config_666_path = os.path.join(result_path, "config_666.txt")
tokens_666_path = os.path.join(result_path, "tokens_666.txt")
config_pos_path = os.path.join(result_path, "config_pos.txt")
tokens_pos_path = os.path.join(result_path, "tokens_pos.txt")

mode = 'a'
if os.path.exists(config_666_path) or os.path.exists(tokens_666_path) \
    or os.path.exists(config_pos_path) or os.path.exists(tokens_pos_path):
    exit_choose = input("文件已经存在, 是否要进行覆盖?(y/n): ")
    if exit_choose.lower() == 'y':
        mode = 'w'

with open(config_666_path, mode=mode, encoding="UTF-8") as config_666_file, \
     open(tokens_666_path, mode=mode, encoding="UTF-8") as tokens_666_file, \
     open(config_pos_path, mode=mode, encoding="UTF-8") as config_pos_file, \
     open(tokens_pos_path, mode=mode, encoding="UTF-8") as tokens_pos_file:

    config_count = 0
    config_exist_count = 0
    tokens_count = 0
    tokens_exist_count = 0
    failed_count = 0
    start_time = time.time()
    for file_path in files_iterator:
        file_name = os.path.basename(file_path)
        if 'config.vdf' != file_name.lower() and 'tokens.txt' != file_name.lower():
            continue
        try:
            with open(file_path, mode='r', encoding="UTF-8", errors='ignore') as file:
                context = file.read()
                if not context and not context.strip(): continue
                parent_path = os.path.dirname(file_path)
                rel_path = work_path
                if parent_path != work_path:
                    rel_path = os.path.relpath(parent_path, work_path)
                if 'config.vdf' == file_name.lower():
                    config_count += 1
                    matches = re.findall('\"eyAi([^\"]\S+)\"', context, re.DOTALL)
                    size =  len(matches) 
                    for matche in matches:
                        text = matche.strip('"').strip('\n')+ '\n'
                        config_666_file.write(f'666----{text}')   
                        config_666_file.flush()
                        config_pos_file.write(f'{rel_path}----{text}')   
                        config_pos_file.flush()
                    if size > 0 : config_exist_count += 1
                if 'tokens.txt' == file_name.lower():
                    tokens_count += 1
                    matches = re.findall('\seyAi([^\s]\S+)\s', context, re.DOTALL)
                    size =  len(matches) 
                    for matche in matches:
                        text = matche.strip(' ').strip('\n')+ '\n'
                        tokens_666_file.write(f'666----{text}')   
                        tokens_666_file.flush()
                        tokens_pos_file.write(f'{rel_path}----{text}')   
                        tokens_pos_file.flush()
                    if size > 0 : tokens_exist_count += 1
            print(f'第 {config_count + tokens_count} 个文件提取到 {size} 条数据-> {file_path}')
        except Exception as e:
            failed_count += 1
            print(f'第 {config_count + tokens_count} 个文件提取数据失败-> {file_path}, 第 {e.__traceback__.tb_lineno} 行代码执行错误: {e}')

    if config_count + tokens_count == 0:
        print(f'该文件夹中未找到 config.vdf 或 tokens.txt 文件 -> {work_path}')
    else:
        end_time = time.time()
        print(f'耗时 {(end_time - start_time):.2f} 秒, 共找到 {config_count + tokens_count} 个文件, 其中 {config_count} 个config.vdf文件, {config_exist_count} 个存在数据, \
{tokens_count} 个tokens.txt文件, {tokens_exist_count} 个存在数据。 生成的文件保存在{result_path}')

os.system('pause')