#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
提取文件夹里所有带password的txt文件, 提取里面是邮箱的账户名和密码
'''

import os
import glob
import time
import hashlib
import colorama

# 解决exe打包后，颜色打印乱码问题
colorama.init(autoreset=True)

try:
    while True:
        try:
            # 输入地址
            work_path = input("\033[1;32m请输入需要提取的正确文件目录: \033[0m").strip('"').strip('&').strip().strip("'").strip()
        except KeyboardInterrupt:
            # 键盘中断操作，防止报错
            result = input("\n您真的要退出吗?(y/n): ")
            if result.lower() == 'y':
                break
            continue
        except Exception as e:
            print(f'\033[31m输入的文件目录有误, 请重新输入: {e}\033[0m')
            continue
        # 对路径的校验
        if not work_path:continue
        if not os.path.isdir(work_path):continue
        start_time = time.time()
        # 转为绝对地址，防止相对地址引发的路径错误
        work_path = os.path.abspath(work_path)
        print(f'\033[32m实际提取的文件目录：{work_path}\033[0m')     
        # 统计路径，返回迭代器
        files_iterator  = glob.iglob(os.path.join(glob.escape(work_path), "**", "*password*.txt") , recursive=True)
        # 创建结果文件
        root_path = os.getcwd()
        output_txt_path = os.path.join(root_path, "output.txt")
        output_txt = open(output_txt_path, mode='a+', encoding="UTF-8")
        # 开始提取处理
        file_count = 0
        user_count = 0
        for input_file in files_iterator:
            # 处理长路径问题。在 Windows 文件系统中，对于一些特别长的路径，可能会超出系统的路径长度限制，路径的最大长度为 260 个字符，
            if len(input_file) > 260:
                if input_file.startswith(u"\\\\"):
                    # 检查路径是否以 \\ 开头，判断是否是网络路径（UNC 路径）。
                    # 如果路径是 UNC 路径，使用 path=u"\\\\?\\UNC\\"+path[2:] 来添加前缀 \\\\?\\UNC\\。这个前缀告诉系统使用更长的路径。
                    input_file = u"\\\\?\\UNC\\" + input_file[2:]
                else:
                    # # 如果路径不是 UNC 路径，使用 path=u"\\\\?\\"+path 来添加前缀 \\\\?\。同样，这个前缀告诉系统使用更长的路径。
                    input_file = "\\\\?\\" + input_file
            with open(input_file, mode='r', encoding="UTF-8", errors='ignore') as file:
                while True:
                    line = file.readline()
                    # 读取完后跳出
                    if not line: break
                    # 跳过空行
                    if not line.strip(): continue
                    # 对账户的处理
                    users = line.split(':')
                    if len(users) != 2: continue
                    user_prefix = users[0].strip()
                    if user_prefix not in ('USER','Username'): continue
                    # 简单判断是否邮箱
                    user_name = users[1].strip()
                    if '@' not in user_name: continue
                    # 对密码的处理
                    line = file.readline()
                    passs = line.split(':')
                    if len(passs) != 2: continue
                    pass_prefix = passs[0].strip()
                    if pass_prefix not in ('PASS','Password'): continue
                    pass_word = passs[1].strip()
                    # 账户密码写入文件中
                    user_count += 1  
                    output_txt.write(f'{user_name}----{pass_word}\n')   
            file_count += 1
            print(f'\033[1;34m[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]: \033[0m第 {file_count} 个文件提取完成-> {input_file}')
        output_txt.close()
        end_time = time.time()
        print(f'\033[32m本次提取结果保存到文件: {output_txt_path}, 提取文件: {file_count}个, 提取结果: {user_count}个, 提取耗时: {(end_time - start_time):.2f}秒\033[0m', '\n') 

        # 去重处理
        result = input(f"您需要对上面 {os.path.basename(output_txt_path)} 文件进行去重吗?(y/n): ")
        if result.lower() != 'y':
            continue
        # 总文件数
        total_count = 0
        # 重复个数
        distinct_count = 0
        # set集合 不重复元素集
        md5_line_set = set()
        start_time = time.time()
        output_distinct_txt_path = os.path.join(os.path.dirname(output_txt_path), "output_distinct.txt")
        with open(output_txt_path, 'r', encoding='UTF-8', errors='ignore') as output_file, open(output_distinct_txt_path, 'w', encoding='UTF-8', errors='ignore') as output_distinct_file:
            for line in output_file:
                total_count += 1
                # 该行数据的md5
                md5_line = hashlib.md5(line.strip().encode("UTF-8")).hexdigest()
                # 该md5是否已经存在
                if md5_line not in md5_line_set:
                    md5_line_set.add(md5_line)
                    output_distinct_file.write(line)
                else:
                    distinct_count += 1
                    print(f'\033[1;34m[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]: \033[0m第 {total_count} 行数据重复-> {line.strip()}')
        end_time = time.time()
        print(f'\033[32m本次去重后结果保存到文件: {output_distinct_txt_path}, 原始个数: {total_count}个, 重复个数: {distinct_count}个, 去重耗时: {(end_time - start_time):.2f}秒\033[0m', '\n') 
except Exception as e:
    print(f'\033[31m第 {e.__traceback__.tb_lineno} 行代码执行产生了错误, 请联系开发者解决: {e}\033[0m')
finally:
    # 判断文件存在且文件已经打开
    if 'output_txt' in dir() and not output_txt.closed: 
        output_txt.close()
os.system('pause')
