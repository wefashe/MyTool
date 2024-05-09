#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
提取文件夹里所有带password的txt文件, 提取里面是邮箱的账户名和密码
pyinstaller -F extract_email.py
'''

import os
import re
import glob

work_path = r'C:\Users\wenfs39551\Desktop\MyTool\demo'


work_path_name = os.path.join(glob.escape(work_path), "**",'[cCtT]o[nk][fe][in][gs].[tv][xd][tf]')
files_iterator  = glob.iglob( work_path_name, recursive=True)

result_path = os.path.join(os.getcwd(), 'result')
if not os.path.exists(result_path):
    os.makedirs(result_path)
config_666_path = os.path.join(result_path, "config_666.txt")
config_666_file = open(config_666_path, mode='a+', encoding="UTF-8")
tokens_666_path = os.path.join(result_path, "tokens_666.txt")
tokens_666_file = open(tokens_666_path, mode='a+', encoding="UTF-8")

config_pos_path = os.path.join(result_path, "config_pos.txt")
config_pos_file = open(config_pos_path, mode='a+', encoding="UTF-8")
tokens_pos_path = os.path.join(result_path, "tokens_pos.txt")
tokens_pos_file = open(tokens_pos_path, mode='a+', encoding="UTF-8")

config_count = 0
config_exist_count = 0
tokens_count = 0
tokens_exist_count = 0
failed_count = 0
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
        print(f'第 {config_count + tokens_count} 个文件提取到 {size} 个-> {file_path}')
    except Exception as e:
        failed_count += 1
        print(f'第 {config_count + tokens_count} 个文件提取失败-> {file_path}, 第 {e.__traceback__.tb_lineno} 行代码执行错误: {e}')
print(f'共找到 {config_count + tokens_count} 个文件, {config_count} 个config.vdf文件, {config_exist_count} 个存在数据, \
{tokens_count} 个tokens.txt文件, {tokens_exist_count} 个存在数据, 生成的文件保存在{result_path}')

tokens_pos_file.close()
tokens_666_file.close()
config_pos_file.close()
config_666_file.close()
os.system('pause')