# -*- coding: utf-8 -*-
import pandas as pd
from pandas import DataFrame, Series
import re
import csv

# 输入：文件名称，数据列表
def createListCSV(fileName="", table_list=[],head=[]):
	with open(fileName, "w", encoding='utf-8',newline='') as csvFile:
		csvWriter = csv.writer(csvFile)

		# 先写入标题
		csvWriter.writerow(head)
		for table in table_list:
			data=[]
			for field in head:
				data.append(table[field])
			csvWriter.writerow(data)
		csvFile.close()

with open('D:\\011111111111111111111111\\LAND_EXCHANGE.csv', newline='',
		  encoding='utf-8') as csvfile:  # 此方法:当文件不用时会自动关闭文件
	csvReader = csv.DictReader(csvfile)
	reader = csv.reader(csvfile)
	csvHead = csvReader.fieldnames
	print(csvHead)
	pattern = '(?<=公司)[,；\s 、/]'
	strinfo = re.compile('(?<=公司)[\s]*(?=\()')
	table_list=[]
	for content in csvReader:
		# print(content['JDR'])
		content['JDR'] = strinfo.sub('', content['JDR'])
		cominfos = re.split(pattern, content['JDR'])
		for comInfo in cominfos:
		  newContent=content.copy()
		  newContent["GSMC"]=comInfo
		  table_list.append(newContent)
		print(content['JDR'] + "------切分后-------" + cominfos[0])
	for content in table_list:
		print(content["JDR"]+" ---公司名称== "+content['GSMC'])
	csvHead.append("GSMC")
	createListCSV('D:\\011111111111111111111111\\LAND.csv',table_list,csvHead)
