# -*- coding: utf-8 -*-
# 比较列表与网页名单的数据
from urllib.request import urlopen
from urllib import parse, request
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame, Series
import re


def get_values(bsObj,values):
	__VIEWSTATE=bsObj.find('input',{'id':'__VIEWSTATE'})['value']
	__EVENTVALIDATION=bsObj.find('input',{'id':'__EVENTVALIDATION'})['value']
	values['__VIEWSTATE']=__VIEWSTATE
	values['__EVENTVALIDATION']=__EVENTVALIDATION
	values['ScriptManager1']='UpdatePanel1|turnPageBar$lbtnNextPage'
	values['__VIEWSTATEGENERATOR'] = '2BA185F2'
	values['__EVENTTARGET']='turnPageBar$lbtnNextPage'


def get_infotitle(bsObj,values):

	ddTags = bsObj.find_all("dd")
	title_arr = []
	for ddTag in ddTags:
		title = ddTag.find("a").get_text().strip()
		title_arr.append(title)
	return title_arr


def readCSV2List(filePath):
	try:
		file = open(filePath, 'r', encoding="utf-8")  # 读取以utf-8
		context = file.read()  # 读取成str
		list_result = context.split("\n")  # 以回车符\n分割成单独的行
		# 每一行的各个元素是以【,】分割的，因此可以
		length = len(list_result)
		for i in range(length):
			list_result[i] = list_result[i].split(",")[0][1:-1]
		return list_result
	except Exception:
		print("文件读取转换失败，请检查文件路径及文件编码是否正确")
	finally:
		file.close();  # 操作完成一定要关闭


headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
url = 'https://www.szcredit.org.cn/web/GSPT/CreditRiskList.aspx'
comlist =[]
values = {}
for i in range(139):
	break
	print('当前第'+str(i)+'页')
	values['turnPageBar$txtPageSize']= 25
	values['turnPageBar$txtPageNum']=i
	data = parse.urlencode(values).encode('utf-8')
	req = request.Request(url=url, data=data, headers=headers)
	html = request.urlopen(req)
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
	get_values(bsObj,values)
	title_arr = get_infotitle(bsObj, 'https://www.szcredit.org.cn/web/GSPT/')
	list=readCSV2List('D:/011111111111111111111111/00临时文件/ENTERPRISE_INFO_ZDGZ.csv')
	for title in title_arr:
		if title in list:
			comlist.append(title)
#comlist=['深圳市天威视讯股份有限公司', '深圳市顺电连锁股份有限公司', '众诚汽车保险股份有限公司深圳分公司', '深圳市国美电器有限公司', '中国联合网络通信有限公司深圳市分公司', '中国太平洋人寿保险股份有限公司深圳分公司', '星巴克咖啡（深圳）有限公司', '深圳市居众装饰设计工程有限公司', '中国太平洋财产保险股份有限公司深圳分公司', '深圳沃尔玛百货零售有限公司香蜜湖分店', '中国人民人寿保险股份有限公司深圳市分公司', '深圳市苏宁云商销售有限公司', '深圳英辅语言培训有限公司', '深圳中海地产有限公司', '中国电信股份有限公司深圳分公司', '深圳市天麒房地产发展有限公司东海朗廷酒店', '深圳市茂业百货华强北有限公司', '深圳市至尊汽车租赁有限公司', '博士眼镜连锁股份有限公司', '太平财产保险有限公司深圳分公司', '深圳市金立通信设备有限公司', '深圳链家房地产经纪有限公司', '平安壹钱包电子商务有限公司', '中国人寿保险股份有限公司深圳市分公司', '中国移动通信集团广东有限公司深圳分公司', '太平人寿保险有限公司深圳分公司', '深圳市天音科技发展有限公司', '华夏人寿保险股份有限公司深圳分公司', '平安养老保险股份有限公司深圳分公司', '深圳市福田农产品批发市场有限公司', '深圳市深银联易办事金融服务有限公司', '深圳市盛迪嘉房地产开发有限公司', '深圳市汇天源机电设备有限公司', '深圳市深圳通有限公司', '金茂深圳酒店投资有限公司金茂深圳万豪酒店', '深圳瑞银信信息技术有限公司', '平安付科技服务有限公司', '深圳市燃气集团股份有限公司', '深圳宝源行汽车销售服务有限公司', '深圳家乐福商业有限公司', '中国平安财产保险股份有限公司深圳分公司', '前海人寿保险股份有限公司深圳分公司', '中国平安人寿保险股份有限公司深圳分公司', '安盛天平财产保险股份有限公司深圳分公司', '雄伟房地产开发（深圳）有限公司', '天安财产保险股份有限公司深圳分公司', '深圳沃尔玛百货零售有限公司山姆会员商店', '深圳市创浩通房地产开发有限公司', '深圳市鹏峰汽车有限公司', '深圳走秀网络科技有限公司', '深圳岁宝连锁商业发展有限公司', '永诚财产保险股份有限公司深圳分公司']
for comm in comlist:
	print(comm)
# st='|0|hiddenField|__EVENTTARGET||0|hiddenField|__EVENTARGUMENT||740|hiddenField|__VIEWSTATE|/wEPDwUKMTk5Mjc1NjE4Nw9kFgICAw9kFgQCAw9kFgJmD2QWBAIBDxYCHgtfIUl0ZW1Db3VudAIDFgZmD2QWAmYPFQIgYjQzYjU5YjE4Njk5NGJhMDg0MTFjYWExZTI5ODlkOWEn5rex5Zyz5biC5Lic5a+M5rG96L2m6ZSA5ZSu5pyJ6ZmQ5YWs5Y+4ZAIBD2QWAmYPFQIgYzM5NDY0NDczOTMzNGYyZjg3OGZlYTYxNjFjYjRmZjQq5rex5Zyz5biC6auY6aOe5piT572R57uc56eR5oqA5pyJ6ZmQ5YWs5Y+4ZAICD2QWAmYPFQIgY2FiNmJmY2Y3ZGNkNDk5M2E1YmU4MzNmYWMzNTZjOTEh5rex5Zyz5biC5rW355Sw6aWu5ZOB5pyJ6ZmQ5YWs5Y+4ZAIDD2QWFgIBDw8WAh4EVGV4dAUDMTM5ZGQCAg8PFgIfAQUCMjVkZAIDDw8WAh8BBQMxMzlkZAIEDw8WAh8BBSfjgI7pobXmrKExMzkvMTM56aG1IOWFsTM0NTPmnaHorrDlvZXjgI9kZAIHDw8WAh4HRW5hYmxlZGdkZAIJDw8WAh8CZ2RkAgsPDxYCHwJoZGQCDQ8PFgIfAmhkZAIPDw8WAh8CZ2RkAhEPDxYCHwJnZGQCEw8PFgIfAmdkZAIED2QWAmYPDxYCHwEFEzIuMC4xLjQgfCAyMDE4LzQvMThkZGTSiODeNOQTl3cqlVUw0JRLmGZ2xg==|8|hiddenField|__VIEWSTATEGENERATOR|2BA185F2|164|hiddenField|__EVENTVALIDATION|/wEdAAZqTXNLuaA8uvgC03VYI33dvcgCCuG0FrvFFyegC5OHwsDVoC8r2cHaUzOKlYFQA/bVmTNrAwEm0ze4dD+R6ooXHEnKRTqG/oip4EFZTDDAGVHU+LRSkBuna/moVswMpfNMcWYojl2fUlr2Av9xXd1cXEevng==|0|asyncPostBackControlIDs|||0|postBackControlIDs|||26|updatePanelIDs||tUpdatePanel1,UpdatePanel1|0|childUpdatePanelIDs|||25|panelsToRefreshIDs||UpdatePanel1,UpdatePanel1|2|asyncPostBackTimeout||90|21|formAction||./CreditRiskList.aspx|'
# st=st.strip()
#
# values = {'turnPageBar$txtPageSize': 25, 'turnPageBar$txtPageNum': 1,'ScriptManager1':'UpdatePanel1|turnPageBar$lbtnNextPage',
# 		  '__EVENTTARGET':'turnPageBar$lbtnNextPage','__VIEWSTATEGENERATOR':'2BA185F2'}
# headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
# data = parse.urlencode(values).encode('utf-8')
# req = request.Request(url=url, data=data, headers=headers)
# html = request.urlopen(req)
# bsObj = BeautifulSoup(html, "html.parser", from_encoding="gb18030")
# lastline=''
# lastline=bsObj.getText()
# line=st.split('\n')[-1]
#
# arrs=line.split('|')
# arrs=arrs[1:-1]
# head_dict={}
# key=''
# for i in range(len(arrs)):
# 	if i%2==0:
# 		key=arrs[i]
# 	else:
# 		head_dict[key]=arrs[i]
# print(head_dict)
#print(bsObj)