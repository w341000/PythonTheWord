# -*- coding: utf-8 -*-
import csv
import re
from urllib.request import urlopen

from bs4 import BeautifulSoup
from pandas import DataFrame


# 获取土地交易信息数据
def get_land_info(url, table1_dict,time):
	html = urlopen(url)
	bsObj = BeautifulSoup(html, "html.parser")
	grids = bsObj.find("main").find_all("div", {"class": "ym-g33 ym-gr"})[1].find_all("div", {"class": "ym-grid"})
	# 正则过滤标题土地编号
	pattern1 = "[0-9a-zA-Z\-\(\)]+"
	# 放入土地编号
	codeArr = table1_dict.get("土地编号")
	if (codeArr == None):
		codeArr = table1_dict["土地编号"] = []
	timeArr = table1_dict.get("交易日期")
	if (timeArr == None):
		timeArr = table1_dict["交易日期"] = []
	# trs = bsObj.find("main").find_all("div", {"class": "ym-g66 ym-gl"})[1].find("table").find("table").find_all("tr")
	# time = ""
	# for tr in trs:
	# 	if "竞买申请截止" in tr.get_text().strip():
	# 		time = tr.find("td").get_text().strip()
	# 	if "竞价开始" in tr.get_text().strip():
	# 		tempTime = tr.find("td").get_text().strip()
	# 		if "" != tempTime and tempTime is not None:
	# 			time = tempTime
	# 		break
	heads = grids[1:7]
	idx = 8
	infos = []
	while (idx < len(grids)):
		info = grids[idx:idx + 11]
		infos.append(info)
		idx = idx + 11
	for info in infos:
		# 先放入交易人相关信息
		for head in heads:
			headkey = head.find("div", {"class": "ym-g33 ym-gl"}).get_text().strip()
			headValue = head.find("div", {"class": "ym-g66 ym-gr"}).get_text().strip()
			headArr = table1_dict.get(headkey)
			if (headArr == None):
				headArr = table1_dict[headkey] = []
			headArr.append(headValue)
		# 放入土地编码
		code = re.search(re.compile(pattern1), info[0].get_text().strip())
		codeArr.append(code.group())
		# 放入交易日期
		timeArr.append(time)
		# 再放入土地信息
		for infoField in info[2:]:
			fieldKey = infoField.find("div", {"class": "ym-g33 ym-gl"}).get_text().strip()
			fieldValue = infoField.find("div",
										{"class": {"ym-g66 ym-gr", "ym-g66 ym-gr get_district"}}).get_text().strip()
			fieldArr = table1_dict.get(fieldKey)
			if (fieldArr == None):
				fieldArr = table1_dict[fieldKey] = []
			fieldArr.append(fieldValue)


# table1_dict.pop("出价记录")
# return table1_dict


def get_infourl_and_time(url):
	html = urlopen(url)
	bsObj = BeautifulSoup(html, "html.parser")
	trTags = bsObj.find("main").find("table").find_all("tr")
	add = False
	url_time_arr = []
	# 获取当前url的目录地址
	offset = url.rfind("/")
	url_prefix = url[:offset + 1]
	# 过滤尚未结束的交易
	for trtag in trTags:
		# print(trtag.get_text().strip()=="已结束交易")
		if add == True:
			if "竞得人" in trtag.get_text().strip():
				time=trtag.find("span",{"class":"afterToday"}).get_text().strip()
				#拼接url
				href = url_prefix + trtag.find("a").get("href")[2:]
				url_time_arr.append({"href" : href,"time" : time})
		if trtag.get_text().strip() == "已结束交易":
			add = True
	return url_time_arr


# 功能：将一个二重列表写入到csv文件中
# 输入：文件名称，数据列表
def createListCSV(fileName="", datadict={}):
	with open(fileName, "w", encoding='utf-8') as csvFile:
		csvWriter = csv.writer(csvFile)
		head = list(datadict.keys())
		# 先写入标题
		csvWriter.writerow(head)
		for h in head:
			data = datadict.get
			csvWriter.writerow(data)
		csvFile.close()


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



#对土地交易中多个公司拍同个地进行处理
def filter_land(readfile,writefile):
	with open(readfile, newline='',
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
			content['竞得人'] = strinfo.sub('', content['竞得人'])
			cominfos = re.split(pattern, content['竞得人'])
			for comInfo in cominfos:
			  newContent=content.copy()
			  newContent["公司名称"]=comInfo
			  table_list.append(newContent)
			print(content['竞得人'] + "------切分后-------" + cominfos[0])
		for content in table_list:
			print(content["竞得人"]+" ---公司名称== "+content['公司名称'])
		csvHead.append("公司名称")
		createListCSV(writefile,table_list,csvHead)

def main():
	url_prefix = "http://www.sz68.com/land/?s="
	table_dict = {}
	for i in range(56):
		url = url_prefix + str(i)
		print("从url：" + url + "获取所有详细信息地址，当前第" + str(i + 1) + "页")
		url_time_arr = get_infourl_and_time(url)
		for url_time in url_time_arr:
			get_land_info(url_time.get("href"), table_dict,url_time.get("time"))

		table1_df = DataFrame(table_dict)

	table1_df = DataFrame(table_dict)
	land='D:\\011111111111111111111111\\00临时文件\\land.csv'
	table1_df.to_csv(land, index=False, sep=',')
	filter_land(land,land)
	print(table1_df)


if __name__ == "__main__":
	#main()
	land='D:\\011111111111111111111111\\00临时文件\\land.csv'
	filter_land(land, land)