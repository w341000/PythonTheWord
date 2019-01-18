# -*- coding: utf-8 -*-
from util import spider_util
from bs4 import BeautifulSoup
from pandas import DataFrame
from os.path import join
import time


main_economic_indicators = []  # 主要经济指标
profitability = []  # 盈利能力
solvency = []  # 偿债能力
cost = []  # 成本费用
datas = [main_economic_indicators, profitability, solvency, cost]  # 所有数据

# 表格标签映射 索引顺序代表分类，二维表格索引顺序代表列
table_maping = [['类别\年份', '营业收入)', '营业利润', '利润总额', '净利润', '资产总计', '负债合计', '股东权益合计', 'StockCode']
	, ['类别\年份', '销售毛利率（%)', '营业利润率（%)', '总资产利润率（%)', '净资产收益率（%)', '存货周转率', '应收账款周转率（次)', '总资产周转率（次)', 'StockCode']
	, ['类别\年份', '资产负债率（%)', '股东权益比率（%)', '流动比率', '速动比率', 'StockCode']
	, ['类别\年份', '营业成本', '销售费用', '管理费用', '财务费用', 'StockCode']]


def doRequest(StockCode=''):
	url = f'http://s.askci.com/stock/financialanalysis/{StockCode}'
	bsobj = spider_util.open_url_return_bsobj(url)
	title_tags = bsobj.select('.right_f_c_tltie')
	table_tags = bsobj.select('.right_f_d_table.mg_tone table')
	for i, title_tag in enumerate(title_tags):
		title = title_tag.get_text().strip()
		table_tag = table_tags[i]
		table_handle(table_tag, i, StockCode)


def table_handle(table_tag: BeautifulSoup, i: int, StockCode: str):
	"""
	表格标签处理
	:param StockCode: 股票代码
	:param table_tag: 表格标签
	:param i: 表格顺序 0：为主要经济指标 1：盈利能力分析 2：偿债能力分析 3：成本费用分析
	:return:
	"""
	tr_tags = table_tag.select('tr')
	for tr_tag in tr_tags[1:]:
		td_tags = tr_tag.select('td')
		data = []
		for column_idx, td_tag in enumerate(td_tags):
			text = td_tag.get_text().strip()
			data.append(text)
		data.append(StockCode)
		datas[i].append(data)


def main():
	directory = 'D:\\pypy\\pythonresult\\上市企业\\'
	companies, csvHead = spider_util.readCSV2List(join(directory, '上市企业信息.csv'))
	for i, company in enumerate(companies):
		stockType = company['stockType']
		StockCode = company['StockCode']
		doRequest(StockCode)
		time.sleep(0.2)
		spider_util.log_progress(i, len(companies), start_from_zero=True)
	DataFrame(main_economic_indicators).to_csv(join(directory, '主要经济指标.csv'), header=table_maping[0], index=False)
	DataFrame(profitability).to_csv(join(directory, '盈利能力.csv'), header=table_maping[1], index=False)
	DataFrame(solvency).to_csv(join(directory, '偿债能力.csv'), header=table_maping[2], index=False)
	DataFrame(cost).to_csv(join(directory, '成本费用.csv'), header=table_maping[3], index=False)


if __name__ == '__main__':
	main()
