# -*- coding: utf-8 -*-
from selenium import webdriver

browser = webdriver.Chrome()
# browser.implicitly_wait(2)

def toPage(page):
	browser.get('http://qy1.sfda.gov.cn/datasearch/face3/base.jsp?tableId=116&tableName=TABLE116&title=%E7%9C%81%E7%BA%A7%E9%A3%9F%E5%93%81%E5%AE%89%E5%85%A8%E7%9B%91%E7%9D%A3%E6%8A%BD%E6%A3%80%EF%BC%88%E4%B8%8D%E5%90%88%E6%A0%BC%E4%BA%A7%E5%93%81%EF%BC%89&bcId=146891547897939037369111531667')
	# browser.get("http://qy1.sfda.gov.cn/datasearch/face3/base.jsp?tableId=114&tableName=TABLE114&title=%B9%FA%BC%D2%CA%B3%C6%B7%B0%B2%C8%AB%BC%E0%B6%BD%B3%E9%BC%EC%A3%A8%B2%BB%BA%CF%B8%F1%B2%FA%C6%B7%A3%A9&bcId=143106776907834761101199700381")
	input = browser.find_element_by_id('goInt')
	# time.sleep(5)
	# tds=browser.find_elements_by_css_selector('#tr0p5 table td')
	# tds[2].click()
	# selector = Select(browser.find_element_by_id("ta"))
	# selector.select_by_index(5)
	input.click()
	input.clear()
	input.send_keys(page)
	browser.find_element_by_css_selector('input[src="images/dataanniu_11.gif"]').click()
	return browser

toPage(1)