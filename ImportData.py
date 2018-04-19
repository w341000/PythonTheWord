# -*- coding: utf-8 -*-
import os
import urllib.request
from functools import reduce
import os
import cx_Oracle
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import re
import datetime
import numpy as np
#获得重点企业股票代码
def get_code(path):
    df = pd.read_excel(path,header =None,names=['name','code','homepage'])
    df = df[df['code'].notnull()] #股票代码非空的记录
    df[['code']]=df[['code']].applymap(lambda x:"%.0f" % x)#去掉小数
    df[['code']]=df[['code']].applymap(lambda x:x.rjust(6,'0'))#6位字符串，不足前面补0
    code_list = df['code']
    return(code_list)


path="E:\\1000enterprise_code.xlsx"
code_list=get_code(path)
d={1:1,2:2,3:3}
print(d)
print(code_list)


def read_csv_to_dataframe(file_dir_list, reportType_tuple, append_columns, rename_columns):
    print("reading ...")
    df_tup = ([], [], [], [], [])
    for dest_dir in file_dir_list:
        df = pd.read_csv(dest_dir, encoding='gb2312', header=None)  # gb2312读中文，header=None不要表头
        if df.shape == (1, 1): continue
        df = df.set_index(df[0])  # 设置索引
        df = df.drop([0], axis=1)  # 删除
        df1 = df.T  # 转置
        df1 = df1.dropna()  # 删掉空值
        df1 = df1.replace('--', np.nan)  # 原始的“--”符号替换成空值
        df1 = df1.set_index(np.arange(len(df1)))  # 重设索引

        ##增加字段
        df1['企业名称'] = np.nan
        df1['统一信用代码'] = np.nan

        pattern1 = "\\d+"  # 匹配股票代码
        matchObj1 = re.search(re.compile(pattern1), dest_dir)
        df1['股票代码'] = matchObj1.group()

        pattern2 = "(?<=_)[a-z]+(?=_)"  # 匹配报告周期
        matchObj2 = re.search(re.compile(pattern2), dest_dir)
        df1['报告周期'] = matchObj2.group()

        pattern3 = "(?<=\=)[a-z]+(?=.)"  # 匹配不同表
        matchObj3 = re.search(re.compile(pattern3), dest_dir)
        table_str = ""
        if matchObj3:
            table_str = matchObj3.group()
        else:
            table_str = "report"  # 主要财务指标
        df1['报告类型'] = reportType_dic[table_str]
        df1['报告类型英文'] = table_str

        now = datetime.datetime.now()  # 写入时间
        df1['更新时间'] = now.strftime('%Y-%m-%d %H:%M:%S')

        if table_str == reportType_tuple[0]:
            df_tup[0].append(df1)
        elif table_str == reportType_tuple[1]:
            df_tup[1].append(df1)
        elif table_str == reportType_tuple[2]:
            df_tup[2].append(df1)
        elif table_str == reportType_tuple[3]:
            df_tup[3].append(df1)
        else:
            df_tup[4].append(df1)
        # df_list.append(df1)
    result = append_columns(df_tup, rename_columns)
    print("finished")
    return (result)


def open_dir(path):
    file_list = os.listdir(path)
    file_list = list(map(lambda x: path + x, file_list))
    return file_list


def append_columns(df_tup, rename_columns):
    result = []
    for i in range(len(df_tup)):
        dataframe = reduce(lambda x, y: x.append(y), df_tup[i])  # 拼接相同类型的表
        # 修改字段名
        if i == 0:
            dataframe.rename(columns=rename_columns[0], inplace=True)
        elif i == 4:
            dataframe.rename(columns=rename_columns[1], inplace=True)
        result.append(dataframe)
    return result
# 存入oracle接口
def write_into_oracle(df_list,reportType_tuple):
    try:
        #connection = cx_Oracle.connect('wwyjfx','Fxyj#17W*2w','10.190.41.13/coreora')
        print("writing ...")
        oracle_db = create_engine('oracle+cx_oracle://wwyjfx:m123@localhost:1521/?service_name=orcl')
        connection = oracle_db.connect()
        for i in range(len(df_list)):
            columns = list(df_list[i].columns)#指定字段类型
            col_dict = {}
            for col in columns:
                col_dict[col] = sqlalchemy.types.NVARCHAR(length=20)
            df_list[i].to_sql('wycbsj_'+reportType_tuple[i],connection,if_exists='append',index=False,chunksize=2000,dtype=col_dict)
        connection.close()
        print("finished")
    except Exception as e:
        print(e)

path =  'D:\\enterprise\\' #下载文件存放目录

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'#正常显示中文
reportType_dic = {'report':'主要财务指标','ylnl':'盈利能力','chnl':'偿还能力','cznl':'成长能力','yynl':'营运能力'}
reportType_tuple = ('report','ylnl','chnl','cznl','yynl')
#oracle字段名长度限制
rename_columns = [{'每股经营活动产生的现金流量净额(元)':'每股现金流量净额(元)',
                   '净利润(扣除非经常性损益后)(万元)':'净利润(扣除后)(万元)',
                  '经营活动产生的现金流量净额(万元)':'现金流量净额(万元)',
                  '股东权益不含少数股东权益(万元)':'股东权益(万元)'},
                 {'经营现金净流量对销售收入比率(%)':'经营现金净流量对销售收入(%)',
                 '经营现金净流量与净利润的比率(%)':'经营现金净流量与净利润(%)'}]

file_list = open_dir(path)
#df_list = read_csv_to_dataframe(file_list)
df_list = read_csv_to_dataframe(file_list,reportType_tuple,append_columns,rename_columns)
write_into_oracle(df_list,reportType_tuple)

