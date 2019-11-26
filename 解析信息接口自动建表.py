# -*- coding: utf-8 -*-
import time
from os import path

from selenium import webdriver

from util import captcha_util
from util import pinyin_util
from util import spider_util

browser = webdriver.Chrome()
browser.implicitly_wait(3)


def login():
	browser.get("http://10.190.65.21/LIRE/LEAP/Login/440304/FTCMSERVICESYS/Login.html?lid=AJ24kr5d")
	username = browser.find_element_by_id('txt_flag')
	username.send_keys('中电科')
	password = browser.find_element_by_id('txt_pwd')
	password.send_keys('ABCabc123')
	time.sleep(1)
	resove_captcha()


def resove_captcha():
	image_path = 'D:\\011111111111111111111111\\temp.jpg'
	count = 0
	while count < 10:
		JSESSIONID = browser.get_cookie('JSESSIONID')
		headers = {'Cookie': 'JSESSIONID=' + JSESSIONID['value']}
		spider_util.download('http://10.190.65.21/LIRE/logic/va/', image_path, headers=headers)
		captcha = captcha_util.get_image_text(image_path)
		print('验证码:', captcha)
		browser.find_element_by_id('txt_vc').clear()
		browser.find_element_by_id('txt_vc').send_keys(captcha)
		browser.find_element_by_id('btn_login').click()
		time.sleep(3)
		try:
			alert = browser.switch_to.alert
			text = browser.switch_to.alert.text
			if '验证码错误' in text or '登陆失败' in text:
				print(text)
				browser.switch_to.alert.accept()
				count += 1
				continue
		except Exception as e:
			pass
		break


def change_to_interface():
	browser.find_elements_by_css_selector('.tree li .tree_item_title')[-1].click()
	time.sleep(1)


def get_interface_sql(name='应急物资储备库信息查询接口'):
	field_arr = []
	elements = browser.find_elements_by_css_selector('.table-title-withtab span')
	title = ''
	for ele in elements:
		if name in ele.text:
			ele.click()
			title = ele.text
			break
	trs = browser.find_elements_by_css_selector('tbody[ut="parameters"] tr')[1:]
	for tr in trs:
		tds = tr.find_elements_by_css_selector('td')
		comment = tds[0].text
		field = tds[1].text
		field_arr.append({"field": field, "comment": comment})

	sql=get_sql(title, field_arr)
	return sql


def get_sql(title, field_arr=[]):
	table = pinyin_util.PinYin().hanzi2pinyin_split(title, "", True).upper()
	table = "T_SJZX_" + table
	sql = ""
	sql = sql + "drop table " + table + ";\n"
	sql = sql + "create table " + table + "(\n"
	for field in field_arr:
		sql = sql + field["field"] + " varchar2(200), \n"
	sql = sql + "WRITETIME date DEFAULT SYSDATE); \n"
	for field in field_arr:
		sql = sql + "COMMENT ON COLUMN 	" + table + " .	" + field["field"] + "	is	'" + field[
			"comment"] + "';\n"
	sql = sql + "COMMENT ON TABLE	" + table + "  	is	'信息中心-" + title + "';\n/"
	return sql


def main():
	interfaces=['高龄老人津贴发放信息查询接口']
	login()
	change_to_interface()
	for interface in interfaces:
		sql=get_interface_sql(interface)
		with open(file=path.join('D:\\011111111111111111111111', interface+'.sql'), mode="w+", encoding="utf-8") as file:
			file.write(sql)
			print('生成'+interface+'sql文件')
	browser.close()


if __name__ == '__main__':
	main()
