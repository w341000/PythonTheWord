# -*- coding=utf-8 -*-
import xlrd
from urllib.request import urlopen
import win32com, re
import urllib
from util import spider_util
from docx import Document


def word_table_to_list(f='', data_arr=[],table_index=0,colnameindex=0, extra=None):
	"""
	将word表格中的数据读取到list中返回
	:param f: word文件路径,如果文件为doc格式,则会先转换为docx格式读取,此操作不会影响到原文件
	:param data_arr: 需要保存数据的列表
	:param table_index: 表格索引,默认为0
	:param colnameindex: 标题行索引,默认为0,标题行中应包含每列的字段信息
	:param extra: 要添加到该word表格数据的额外信息,表格中的每一行都会添加该数据
	:return:
	"""
	ext = f[f.rfind('.'):]
	if ext == '.doc':
		# 将doc文件转为docx文件
		word = win32com.client.Dispatch('Word.Application')
		doc = word.Documents.Open(f)
		file = temp_docx_file = 'D:\\011111111111111111111111\\temp\\office_temp_file.docx'
		doc.SaveAs(temp_docx_file, 12, False, "", True, "", False, False, False, False)  # 转化后路径下的文件
		doc.Close()
		word.Quit()
	else:
		file=f
	# 读取docx中的表格数据到数据列表中
	d = Document(file)
	t = d.tables[table_index]
	rows = t.rows
	header_cells = rows[colnameindex].cells
	for row in rows[colnameindex+1:]:  # 跳过标题行
		cells = row.cells
		data = {}
		for i in range(len(cells)):
			field = header_cells[i].text
			field = re.sub('\s+', '', field)  # 替换空格为空
			data[field] = cells[i].text
		if extra is not None and isinstance(extra, dict):  # 添加额外信息
			for key in extra:
				data[key] = extra[key]
		data_arr.append(data)
	if ext == 'doc':
		spider_util.delete_file(temp_docx_file)


def open_excel(file='file.xls'):
	try:
		data = xlrd.open_workbook(file)
		return data
	except Exception as e:
		print(str(e))


def get_colnames(table,colnameindex=0):
	colnames = table.row_values(colnameindex)  # 某一行数据 ['姓名', '用户名', '联系方式', '密码']
	for name in colnames:
		if name != '':
			return colnames
	return None


def excel_table_byname(file='',data_arr=[], colnameindex=0, sheet=0, extra=None):  # 修改自己路径
	"""
	读取excel中的表格并返回数据列表
	:param data_arr: 需要保存到的数据列表
	:param file: excel文件路径
	:param colnameindex: 标题行的索引
	:param sheet: 单元簿索引
	:param extra:额外字段,将会被添加到excel记录中的每一行,格式为{'key':'value'}数组中的每一个元素为表头及对应值的对象
	:return:
	"""
	data = open_excel(file)
	table = data.sheet_by_index(sheet) #获得表格
	nrows = table.nrows  # 拿到总共行数
	for i in range(colnameindex,nrows):
		colnames=get_colnames(table,i)#获取标题行,如果该标题行为空行则选择下一行,直到找到有字符的一行为止
		if colnames is not None:
			break
	for rownum in range(colnameindex + 1, nrows):  # 也就是从Excel第二行开始，第一行表头不算
		row = table.row_values(rownum)
		if row:
			app = {}
			for i in range(len(colnames)):
				app[colnames[i]] = row[i]  # 表头与数据对应
			if extra is not None and isinstance(extra,dict):
				for key in extra:
					value=extra[key]
					app[key]=value
			data_arr.append(app)


def main():
	pass


if __name__ == "__main__":
	main()
