# -*- coding: utf-8 -*-
from pandas import DataFrame
from selenium import webdriver

browser = webdriver.Chrome()


def toPage(page):
	browser.get("http://219.135.157.143:2002/gzwz/gdyj/sjwz/yp/sjwzYpScqyList.faces")
	input = browser.find_element_by_css_selector('.dr-table-footer .commonTextInput01')
	# input.click()
	input.clear()
	input.send_keys(page)
	browser.find_element_by_css_selector('.dr-table-footer input[type="submit"]').click()
	return browser


def totalElement():
	atags = browser.find_elements_by_css_selector('.dr-table>tbody td a')
	return len(atags)


def openElement(current):
	# actions = ActionChains(browser)
	atags = browser.find_elements_by_css_selector('.dr-table>tbody td a')
	count = len(atags)
	curInfo = atags[current]
	curInfo.click()


def getCompanyInfo(companies=[]):
	# label=browser.find_element_by_css_selector('#sjwzYpScqyForm:qymc')
	trs = browser.find_elements_by_css_selector('#tb_sjwzBjpPzss_table tr')
	info = {}
	for tr in trs[:-1]:
		try:
			key = tr.find_element_by_css_selector('.rich-table-sixrow6').text
			value = tr.find_element_by_css_selector('.rich-table-fiverow6').text
			info[key] = value
		except Exception as e:
			print('发生异常')
			print(e)
	print(info)
	companies.append(info)
	return info


def getTotalPage():
	return 58


companies = []
try:
	for i in range(1, getTotalPage() + 1):
		toPage(i)
		total = totalElement()
		for x in range(total):
			openElement(x)
			getCompanyInfo(companies)
			browser.back()

	print(companies)
	df = DataFrame(companies)
	df.to_excel('D:\\pypy\\pythonresult\\食品药品\\食品药品相关公司.xlsx', index=False)
except RuntimeError as e:
	print(e)
finally:
	browser.close()
