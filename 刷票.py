# -*- coding: utf-8 -*-
from util import  spider_util
import demjson
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
browser = webdriver.Chrome()
for i in range(2346):
	main='http://finance.sina.cn/zt_d/kcbbqb?from=wap'
	url='http://support.finance.sina.com.cn/service/api/openapi.php/VoteService.setVote?appid=kcbqy18&id=list2018kcb10364&wxflag=0&captcode=&roller_id=&uuid=d7896144d48b697d0bf5afd7f96397cf&_=1547202632629'
	browser.delete_all_cookies()
	browser.get(main)
	browser.get(url)
	html = browser.page_source
	soup = BeautifulSoup(html, 'lxml')
	cc = soup.select('pre')[0].get_text()
	print(demjson.decode(cc))
browser.close()
