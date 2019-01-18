# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
browser = webdriver.Chrome()
browser.get("https://www.aqistudy.cn/historydata/monthdata.php?city=%E6%B7%B1%E5%9C%B3")
browser.implicitly_wait(10)
table=browser.find_element_by_css_selector(".table.table-condensed.table-bordered.table-striped.table-hover.table-responsive")
elements=table.find_elements_by_tag_name("td")
for element in elements:
	print(element.text)
print(table.get_attribute('class'))
browser.close()