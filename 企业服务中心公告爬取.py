# -*- coding: utf-8 -*-
import os
import re
from os import path
from urllib import parse
from urllib import request

from selenium import webdriver

browser = webdriver.Chrome()
# browser.implicitly_wait(3)
#下载pdf
def downloadpdf(url, directory):
	"""

	:param url:
	:param directory:
	:return:
	"""
	try:
		browser.get(url)
		a_tags =browser.find_elements_by_css_selector('a[class="updatecss"]')
		time=re.search('\d{4}-\d{2}-\d{2}',browser.find_element_by_css_selector('h6 label em').text).group()
		for a_tag in a_tags:
			filename=a_tag.text
			filename='('+time+')'+filename
			href=a_tag.get_attribute('href')
			if re.search(".*\.pdf",href) is None :
				continue
			pdfurl=parse.urljoin(url,href)
			if not path.exists(directory):
				os.makedirs(directory)
			request.urlretrieve(pdfurl,path.join(directory,filename))
	except Exception as e:
		print('从'+url+'下载pdf失败:'+pdfurl)
		return





def get_infourl(url, pattern):
	"""
	获取公告对应的url链接
	:param url: 当前页面的链接地址
	:param pattern: 需要进行比较的正则表达式或正则表达式对象
	:param keyword: 标题中的关键字,只有含有关键字的链接才会被返回
	:return:
	"""
	# html = spider_util.open_url(url, 5, 20)  # 20秒超时
	# bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
	# tags = bsObj.select(".dropbox ul a")
	status=request.urlopen(url).code
	if status is 404:
		browser.close()
		raise RuntimeError('404错误')
	browser.get(url)
	tags=browser.find_elements_by_css_selector('.gl-list li a')
	url_arr = []
	# 只获取高层次专业人才认定公式公告
	for tag in tags:
		href=tag.get_attribute("href")
		title = tag.text;
		# tag.get_attribute("title")
		if '拟' in title:
			continue
		if re.search(pattern, string=title) is not None:
			infourl = parse.urljoin(url,href)
			url_arr.append(infourl)
	return url_arr


def main():
	url_prefix = "http://www.szft.gov.cn/bmxx/qqyfzfwzx/tzgg/"
	table_dict = {}
	i=0
	while True:
		if i==0:
			suffix='index.htm'
		else:
			suffix='index_'+str(i)+'.htm'
		url=url_prefix+suffix
		print("从url：" + url + "获取所有详细信息地址，当前第" + str(i + 1) + "页")
		urlarr=get_infourl(url,"项目公告|项目公示")
		for url_time in urlarr:
			downloadpdf(url_time, 'd:/pythonresult')
		i+=1



if __name__ == "__main__":
	main()
