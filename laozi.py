# -*- coding: utf-8 -*
import re

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
	content=''
	company=p_tags[0].get_text().strip()
	for p_tag in p_tags[:-2]:
		content=content+p_tag.get_text().strip()
	data={}
	company=company[:company.rfind(':')]
	data['company']=company
	data['time']=time
	data['content']=content
	data['title']=title
	datas.append(data)


datas=[]
for i in range(23):
	if i==0:
		url='http://www.szft.gov.cn/bmxx/qrlzyj/rl_zwdt/zwdt_tzgg/index.htm'
	else:
		url = 'http://www.szft.gov.cn/bmxx/qrlzyj/rl_zwdt/zwdt_tzgg/index_' + str(i) + '.htm'
	url_arr=get_infourl(url,'深圳市福田区劳动人事争议仲裁委员会公告')
	for info_url in  url_arr:
		getInfo(info_url,datas)

DataFrame(datas).to_csv("D:\\011111111111111111111111\\00临时文件\\laozi.csv",
										index=False,
										sep=',')