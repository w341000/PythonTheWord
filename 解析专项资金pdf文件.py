# -*- coding: utf-8 -*-
import pdfplumber
import pandas as pd
from pandas import DataFrame
import os
import re

def readpdf(filname, datas):
	# 你想对文件的操作
	time=re.search('\d{4}-\d{2}-\d{2}',filname).group()
	matchpbj=re.search('年(.*专项资金)((.*)分项)*',filname)
	type=''
	if matchpbj is not None:
		for group in matchpbj.groups():
			if group is not None:
				type=group
	with pdfplumber.open(filname) as pdf:
		for page in pdf.pages:
			for table in page.extract_tables():
				for row in table:
					if not isDataRow(row):
						continue
					# row=[]
					if row[1] is None :
						continue
					if len(row)>3 and row[3] is not None and not row[3] == '':
						temp=row[2]
						row[2]=row[3]
						row[3]=temp
					row.pop(0)
					row.insert(0,time)
					row.insert(0,type)
					datas.append(row)


def isDataRow(row=[]):
	"""
	判断数组中是否包含数字或个人信息
	:param row:
	:return:
	"""
	isData=False
	for item in row:
		if re.search('个[\s\S]*人',str(item)) is not None:
			isData= False
			break
		if str(item).isdigit():
			isData=True
	return isData

def main():
	rootdir = 'D:\\pythonresult'
	files = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
	datas = []
	for i in range(0, len(files)):
		path = os.path.join(rootdir, files[i])
		if os.path.isfile(path):
			readpdf(path, datas)
	df = DataFrame(datas)
	df.to_csv('D:\\pythonresult\\data.csv',index=False)


if __name__ == "__main__":
	main()
