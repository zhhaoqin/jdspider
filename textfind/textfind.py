#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

import os
import re
import jieba
from operator import itemgetter
import mysql.connector


# 遍历文件夹得到子文件夹和文件,将结果保持到MySQL数据库
def savefile():
    conn = mysql.connector.connect(user='root', password='password', database='data_test')
    cursor = conn.cursor()
    cursor.execute('drop table if exists filenames')
    cursor.execute('create table filenames(filename varchar(100), path varchar(200))')
    ls = []
    for foldername, subfolders, filenames in os.walk('C:\\Python36'):  # 用os.walk遍历指定文件夹
        for subfolder in subfolders:
            ls.append([subfolder, foldername])
        for filename in filenames:
            ls.append([filename, foldername])  
     
    try:
        sql_insert = 'insert into filenames values(%s, %s)'
        cursor.executemany(sql_insert, ls)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
    cursor.close()
    conn.close()


# 从数据库提取文件夹的子文件夹和文件                
def getfile():
    conn = mysql.connector.connect(user='root', password='password', database='data_test')
    cursor = conn.cursor()
    cursor.execute('select * from filenames')
    lfile = cursor.fetchall()
    cursor.close()
    conn.close()
    return lfile
    

# 单个关键字检索
def onekeyfind(lf, ke):
    result = []
   
    for s in lf:  # 用re.findall对文件检索
        r = re.findall(ke.lower(),s[0].lower())
        if r:
            result.append([s, len(ke) * len(r) / len(s[0])])
    return result  # 返回赋值的检索结果


# 调用onekeyfind对多个关键词检索
def multiplekey(_list, lf):
    resultlist =[]
    for ke in _list:
        resultlist.append(onekeyfind(lf, ke))
    return resultlist  # 返回单个关键词检索结果的列表


# 用jieba.lcut(s)对输入文本进行分词
def segmentation(keys):
    k = jieba.lcut(keys)
    def not_empty(s):
        return s and s.strip()
    return list(filter(not_empty, k))


# 对检索结果进行合并排序输出
def print_save(resultlist,keys):
    rl =[]
    for ls in resultlist:  # 对多个关键词的检索结果合并
        for s in ls:
            if s[0] in [rl[i][0] for i in range(len(rl))]:
                for li in rl:
                    if li[0] == s[0] :
                        li[1] += s[1]
            else:
                rl.append(s)
                
    for s in rl:  # 对合并后的结果进行全文检索
        rs = re.findall(keys.lower(), s[0][0].lower())
        s[1] += len(rs)
    l_end = sorted(rl, key = itemgetter(1), reverse = True)  # 结果排序
    print('搜索结果:')
    for i in range(len(l_end)):
        print(l_end[i][0][0], '    ', l_end[i][0][1])  # 输出结果
        with open('result_' + keys + '.csv', 'a') as f:  # 结果保存到文件中
            f.write(l_end[i][0][0] + ', ' + l_end[i][0][1] + '\n')


def main():
    savefile()
    lf = getfile()
    while True:
        keys = input('请输入搜索内容：')
        _list = segmentation(keys)
        print_save(multiplekey(_list, lf), keys)
       
        
main()        
