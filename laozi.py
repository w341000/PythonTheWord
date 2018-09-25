# -*- coding: utf-8 -*
import re
from urllib import error
from bs4 import BeautifulSoup
from pandas import DataFrame

import spider_util


#爬取劳资纠纷公告信息

def get_infourl(url, pattern):
	"""
	获取公告对应的url链接
	:param url: 当前页面的链接地址
	:param pattern: 需要进行比较的正则表达式或正则表达式对象
	:param keyword: 标题中的关键字,只有含有关键字的链接才会被返回
	:return:
	"""
	html = spider_util.open_url(url, 5, 20)  # 20秒超时
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="UTF-8")
	liTags = bsObj.find("ul", {"class": "gl-list"}).find_all("li")
	url_arr = []
	# 获取当前url的目录地址
	offset = url.rfind("/")
	url_prefix = url[:offset + 1]
	# 只获取高层次专业人才认定公式公告
	for liTag in liTags:
		aTag = liTag.find("a")
		title = aTag.get_text().strip()
		if re.search(pattern, string=title) is not None:
			href = url_prefix + aTag.attrs["href"][2:]
			url_arr.append(href)
	return url_arr


def getInfo(url,datas):
	html = spider_util.open_url(url, 5, 20)  # 20秒超时
	bsObj = BeautifulSoup(html, "html.parser", from_encoding="UTF-8")
	title=bsObj.find('title').get_text().strip()
	time=bsObj.find('em').get_text().strip()
	p_tags=bsObj.find('div',{'class':'TRS_Editor'}).find_all('p')
	thecontent=bsObj.get_text().strip()
	content=re.search('var content = \".+\"',bsObj.get_text().strip())
	content=content.group()
	content=content[content.find('"')+1:content.rfind('"')]
	content=content.replace('<br/>','')
	content = content.replace('&nbsp;', '')
	content=content.strip()
	company=re.search('.+?：',content).group().strip()[:-1]
	print(content)
	data={}
	data['company']=company
	data['time']=time
	data['content']=content
	money=0
	arr=re.findall('(\d+\.?\d+元)', string=content)
	for i in range(len(arr)):
		money=money+float(arr[i][:-1])
	data['title']=title
	data['money']=money
	data['source'] = '人力资源局'
	data['type']='劳动仲裁'
	datas.append(data)


datas=[]
i=0
while True:
	if i==0:
		url='http://www.szft.gov.cn/bmxx/qrlzyj/rl_zwdt/zwdt_tzgg/index.htm'
	else:
		url = 'http://www.szft.gov.cn/bmxx/qrlzyj/rl_zwdt/zwdt_tzgg/index_' + str(i) + '.htm'
	try:
		url_arr=get_infourl(url,'深圳市福田区劳动人事争议仲裁委员会公告')
	except error.HTTPError as e:
		if e.code ==404:
			print("爬取福田区劳动仲裁公告结束")
			break
	for info_url in  url_arr:
		getInfo(info_url,datas)
	i=i+1

DataFrame(datas).to_csv("D:\\011111111111111111111111\\00临时文件\\laozi.csv",
										index=False,
										sep=',')