#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import pymysql
import numpy as np
import configparser

'''
导入TA文件
'''

TA_FILE_PATH = 'OFD_99_25_20210514_52.TXT'
IGNORE_LINE = 109
file_type = TA_FILE_PATH[TA_FILE_PATH.rfind('_') + 1 : TA_FILE_PATH.rfind('.')]

CONFIG_PATH = 'config.ini'
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(__file__,'..',CONFIG_PATH)),encoding='utf-8')

file_type_sections = [section for section in config.sections() if section.startswith(file_type + '_')]
if len(file_type_sections) == 0:
    exit()
print(file_type_sections)    
file_type_section = file_type_sections[0]    
table_name = file_type_section[file_type_section.find('_') + 1:]
if not table_name:
   exit()

host, user, password, database = config['mysql'].values()
conn = pymysql.connect( host=host,
                    user=user,
                    password=password,
                    database=database)
cursor = conn.cursor()

encoding = 'gbk'
with open(os.path.abspath(os.path.join(__file__,'..',TA_FILE_PATH)),'r',encoding = encoding) as file:
    lines = file.readlines()
    lines = lines[IGNORE_LINE : -1]
    if len(lines) == 0:
        exit()
    fields = []
    values = []
    for line in lines:
        line_byte = line.encode(encoding)
        value = []
        pos_from = pos_to =  0
        options = config.options(file_type_section)
        for option in options:
            items = config.get(file_type_section, option).split(',')
            # items[0] 字段类型
            data_type = items[0]
            if data_type == 'C' or data_type == 'A':
                default_value = ' '
            if data_type == 'N':
                default_value = 0            
            # items[6] 默认值
            if len(items) == 7:
                default_value = items[6]
            # items[1] 内容对应长度 
            length = items[1]
            if length == '' or length == '0':
                field_value = default_value
            else:
                pos_to = pos_from + int(length)
                field_value_byte = line_byte[pos_from: pos_to] 
                pos_from = pos_to
                field_value = field_value_byte.decode(encoding, errors='ignore').strip()
                if not field_value:
                    field_value = default_value
                if data_type == 'N':
                    # items[2] 小数位数
                    places = items[2]
                    if not places:
                        places = '0'
                    field_value = aa = "{:.{}f}".format(float(field_value), places)
            # items[5] 是否需要导入 0 否，1 是，默认是
            if len(items) == 6 and items[5] == '0':
                continue
            # items[4] 表里对应字段
            field = items[4]
            if field not in fields:
                fields.append(field)    
            value.append(field_value)
        values.append(tuple(value))
        print('解析第 ' + str(len(values)) + ' 行数据成功!')
    sql = 'insert into ' + table_name + ' (' + ','.join(fields)	+') values ('+','.join(np.full(len(fields), '%s'))+')'
    cursor.executemany(sql, values)
    conn.commit()
    print(table_name + ' 表成功新增 '+ str(cursor.rowcount)+ ' 条数据！')
cursor.close()
conn.close()