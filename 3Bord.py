# -*- coding: utf-8 -*-
import os
import urllib.request
import pandas as pd
import time


# 获得重点企业股票代码

def get_code(path):
	df = pd.read_excel(path, header=None, names=['code'])
	df = df[df['code'].notnull()]  # 股票代码非空的记录
	df[['code']] = df[['code']].applymap(lambda x: "%.0f" % x)  # 去掉小数
	df[['code']] = df[['code']].applymap(lambda x: x.rjust(6, '0'))  # 6位字符串，不足前面补0
	code_list = df['code']
	return (code_list)
#显示下载进度
def schedule(a,b,c):
    #a:已下载的数据块 b:数据块的大小 c:远程文件的大小
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    print ('%.2f%%' % per)
#url="http://quotes.money.163.com/service/zycwzb_600639.html?type=report&part=ylnl"
#url = "http://quotes.money.163.com/service/zycwzb_"+code+".html?type=report"+part[i]
#urllib.request.urlretrieve(url , dest_dir)
# period : 报告周期
# 按报告期 ：http://quotes.money.163.com/service/zycwzb_600639.html?type=report
# 按年段：http://quotes.money.163.com/service/zycwzb_600639.html?type=year
# 按单季度：http://quotes.money.163.com/service/zycwzb_600639.html?type=season
# url_prefix : url前缀
# code : 企业股票代码
# http://basic.10jqka.com.cn/api/stock/export.php?export=main&type=report&code=837015
# dest_dir : 下载文件存放目录
def download(export,period,url_prefix,code,dest_dir):
    for i in range(len(period)):
            url = url_prefix+"?export="+export+"&type="+period[i]+"&code="+code
            full_path = dest_dir+code+"_"+period[i]+"_"+".xls"
            #file_dir_list.append(full_path)
            urllib.request.urlretrieve(url , full_path)
            print("url:"+url)
            print('finished-' + code + "_" + period[i] + "_")


code_file = 'E:\\brand3.xlsx'#股票代码文档目录
dest_dir = 'D:/enterprise/brand3/' #下载文档保存目录

period = ['report','year','simple']
url_prefix = "http://basic.10jqka.com.cn/api/stock/export.php"
export="main"
code_list = get_code(code_file)
time_start=time.time()
print('downloading ...')
failed_code = []
for code in code_list:
    try:
        download(export,period,url_prefix,code,dest_dir)
    except Exception as e:
        print(e)
        print(code+' failed')
        failed_code.append(code)
    time.sleep(1)


time_end=time.time()
print('finished in {0:.1f} minutes'.format((time_end-time_start)/60)) #格式化输出，保存1位小数