# -*- coding: utf-8 -*-
from util import db_util
from pandas import DataFrame
import pandas as pd
import numpy as np
import jieba
from numpy import *
import time
from PIL import Image
from wordcloud import WordCloud
from util import  AssociationRulesUtil
from jieba import analyse

def baseinfo():
	sql = """
	SELECT DISTINCT a.DWMC ,b.cjzs,b.zjzs,c.total_wqzs,d.tdjycs,d.zjtdjyrq,
	CASE WHEN e.stockcode IS NOT NULL THEN '已上市' ELSE '' END AS isListed,
	e.stockcode,e.stockname,e.companylistingdate,e.phone,e.employeenum,
	CASE WHEN f.qymc IS NOT NULL THEN '准备上市' ELSE '' END AS PREPARELIST,
	f.*
	FROM ENTERPRISE_INFO_ZDGZ  a
	LEFT JOIN 
	(SELECT qymc,sum(cjzs) cjzs,sum(zjzs) zjzs FROM  ENT_DX_CZJXX GROUP BY qymc) b ON a.dwmc=b.qymc
	LEFT JOIN
	(SELECT qymc,sum(TOTAL_WQZS) TOTAL_WQZS FROM  ENT_DX_WQXX GROUP BY qymc ) c ON a.dwmc=c.qymc
	LEFT JOIN 
	(SELECT gsmc,count(*) TDJYCS,max(jyrq) ZJTDJYRQ FROM LAND_EXCHANGE GROUP BY gsmc)d ON a.dwmc=d.gsmc
	LEFT JOIN ent_listed_company e ON a.dwmc=e.COMPANYNAME
	LEFT JOIN ENT_IPO f ON a.dwmc=f.qymc
	WHERE b.cjzs IS NOT NULL OR b.zjzs IS NOT NULL OR c.total_wqzs IS NOT NULL OR d.tdjycs IS NOT NULL 
	OR d.zjtdjyrq IS NOT NULL OR f.qymc IS NOT NULL
	"""
	df = db_util.execute2Dataframe(sql)

	# 统计公司社保缴纳情况
	# s = """
	# select a.dwmc,c.YJNY,count(*) JNRS from ENTERPRISE_INFO_ZDGZ a inner join T_SJZX_RKSBXX b
	# on a.dwmc=b.UNIT_NAME inner JOIN T_SJZX_SBMXXX_2017TO2018 c on b.SI_NO=c.shbxh
	# GROUP BY a.dwmc,c.YJNY
	# order by c.YJNY
	# """
	s = """
	SELECT
		a.dwmc ,yjny,count(*) JNRS
	FROM
		ENTERPRISE_INFO_ZDGZ A
	INNER JOIN LGL_UNITSOCIAL_SECURITY b ON A .dwmc = b.DWMC
	INNER JOIN T_SJZX_SBMXXX_2017TO2018 c ON b.dwbm=c.sbdwbh
	GROUP BY a.dwmc,yjny
	ORDER BY yjny
	"""

	qysb_df = db_util.execute2Dataframe(s)
	qysb_dict = {}
	for index, row in qysb_df.iterrows():
		dwmc = row['DWMC']

		dw_data = qysb_dict.get(dwmc)
		if dw_data is None:
			dw_data = []
			qysb_dict[dwmc] = dw_data
		dw_data.append(row['JNRS'])

	company_list = []
	for k, v in qysb_dict.items():
		v = v[:-1]
		if len(v) == 0:
			continue
		v_serise = pd.Series(v)
		std = v_serise.std()
		mean = v_serise.mean()
		entent = '上升'
		isdown = False
		if v[-1] - mean < 0:
			entent = '下降'
			isdown = True
		if v[-1] - mean == 0:
			entent = '不变'
		cov = std / mean
		# if isdown and cov>0.1 and mean>10:

		company_data = {'DWMC': k, 'SBJNRS': round(mean), 'ZJFD': entent, 'cov': cov}
		company_list.append(company_data)
		if isdown:
			print(k, '数据：', v, '标准差:', std, '均值:', mean, '变异系数：', cov, '增减幅度:', entent)

	company_df = DataFrame(company_list)
	merge_df = df.merge(company_df, how='left', left_on='DWMC', right_on='DWMC')
	print(merge_df)

	merge_df.to_excel('D:\\python\\企业社保信息.xlsx')


def get_stopWords():
	filepath = 'stopwords.txt'
	stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
	stopwords.extend(['企业','公司','深圳','我司','年','福田区','希望','区政府','提供','给与','影响','深圳市','政府','区','部门','申请'
					  '建设','建议','福田','相关','月','给予','司','区政','协调','高','增加','导致','需求','经营','正常','解决','支持','发展','政策','没有','比如','能够',
					  '问题','相关',''])
	return stopwords


# 构建所有词的列表
def fenci():
	sql="""
	select qymc,sqnr,dfnr from ENT_REQUIRENTMENT
	"""
	df = db_util.execute2Dataframe(sql)
	# df = DataFrame(pd.read_excel("E:\\svn仓库\\svnrepo\\python\\03data\\data\\各委办局直接过来的数据\\外迁企业相关数据\\企业诉求\\2018-4.xlsx"))
	wordsCount = {}
	wordsList = []
	stopwords = get_stopWords()
	for index, row in df.iterrows():

		qymc = row['QYMC']
		question = row['SQNR']
		answer = row['DFNR']

		seg_list = jieba.cut(question, cut_all=True)
		for word in seg_list:
			if word.strip() == '':
				continue
			if word in stopwords:
				continue
			if wordsCount.get(word) is None:
				wordsCount[word] = 0
			wordsCount[word] += 1
	for k, v in wordsCount.items():
		wordsList.append({'单词': k, '出现次数': v})
	result = DataFrame(wordsList).sort_values(by='出现次数', na_position='first')
	gen_word_cloud(wordsCount)
	print(result)


def gen_word_cloud(frequencies):
	alice_mask = np.array(Image.open("E:\\svn仓库\\svnrepo\\python\\03data\\data\\各委办局直接过来的数据\\外迁企业相关数据\\企业诉求\\mask.jpg"))
	wordCloud=WordCloud(font_path='C:/Windows/Fonts/simkai.ttf', width=1920,height=1080,background_color='white', max_words=500, max_font_size=80,random_state=40, mask=alice_mask,scale=4)
	wordCloud.generate_from_frequencies(frequencies)
	image = wordCloud.to_image()
	image.show()
	image.save('d://cloud.png')

# 将文本转化为词袋模型
def bagOfWords2Vec(vocabList: list, inputSet: list):
	returnVec = [0] * len(vocabList)  # 构造一个默认为0的数组
	for word in inputSet:
		if word in vocabList:
			returnVec[vocabList.index(word)] += 1
		else:
			print("the word: %s is not in my Vocabulary!" % word)
	return returnVec


def main():
	fenci()


#逆向文件频率
def idf(lines:[]):
	all_dict = {}
	total=0
	for line in lines:
		temp_dict = {}
		total += 1
		cut_line = jieba.cut(line, cut_all=False)
		for word in cut_line:
			temp_dict[word] = 1
		for key in temp_dict:
			num = all_dict.get(key, 0)
			all_dict[key] = num + 1
	for key in all_dict:
		w = key#.encode('utf-8')
		p = '%.10f' % (math.log10(total / (all_dict[key] + 1)))
		print(w,p)

# 生成数据集
def loadSimpDat():
	# simpDat = [['r', 'z', 'h', 'j', 'p'],
	#            ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
	#            ['z'],
	#            ['r', 'x', 'n', 'o', 's'],
	#            ['y', 'r', 'x', 'z', 'q', 't', 'p'],
	#            ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]

	# sql = """
	#    select a.qymc,a.sqnr,a.dfnr,b.hydm from ENT_REQUIRENTMENT a left join T_SJZX_SSZTJBXX b on a.qymc=b.qymc
	#    """
	sql="""
	select a.qymc,a.sqnr,a.dfnr,c.GBHY from ENT_REQUIRENTMENT a inner join T_YW_ZZ_FR b on a.qymc=b.jgmc 
		inner join OPENDATA_SY_INFO c on b.TYSHXYDM =c.TYSHXYDM
	"""
	simpDat=[]
	df = db_util.execute2Dataframe(sql)
	# df = DataFrame(pd.read_excel("E:\\svn仓库\\svnrepo\\python\\03data\\data\\各委办局直接过来的数据\\外迁企业相关数据\\企业诉求\\2018-4.xlsx"))
	wordsCount = {}
	wordsList = []
	stopwords = get_stopWords()
	# 引入TF-IDF关键词抽取接口
	textrank = analyse.textrank

	for index, row in df.iterrows():
		hydm = row['GBHY']
		qymc = row['QYMC']
		question = row['SQNR']
		answer = row['DFNR']
		# 基于TF-IDF算法进行关键词抽取
		keywords = textrank(question,topK=10)
		print('关键词:')
		# 输出抽取出的关键词
		print('/'.join(keywords))
		seg_list = jieba.cut(question, cut_all=True)
		keywordsFilter=[]
		for word in keywords:
			if word.strip() == '':
				continue
			if word in stopwords:
				continue
			keywordsFilter.append(word)
		if hydm is not None:
			keywordsFilter.append(hydm)
			simpDat.append(keywordsFilter)
		for word in seg_list:
			if word.strip() == '':
				continue
			if word in stopwords:
				continue
			if wordsCount.get(word) is None:
				wordsCount[word] = 0
			wordsCount[word] += 1
	for k, v in wordsCount.items():
		wordsList.append({'单词': k, '出现次数': v})
	result = DataFrame(wordsList).sort_values(by='出现次数', na_position='first')
	gen_word_cloud(wordsCount)

	top100Df=result[-20:]
	top100List=top100Df['单词'].tolist()

	# for index, row in df.iterrows():
	# 	keywords = []
	# 	hydm = row['GBHY']
	# 	question = row['SQNR']
	# 	answer = row['DFNR']
	# 	seg_list = jieba.cut(question, cut_all=True)
	# 	for word in seg_list:
	# 		if word.strip() == '':
	# 			continue
	# 		if word in stopwords:
	# 			continue
	# 		if word in top100List:
	# 			if word in keywords:
	# 				continue
	# 			keywords.append(word)
	# 	if len(keywords)!=0 and hydm is not None:
	# 		keywords.append(hydm)
	# 		simpDat.append(keywords)
	return simpDat




if __name__ == "__main__":
	sql="""
	select GBHY from OPENDATA_SY_INFO GROUP BY gbhy 
	"""
	df = db_util.execute2Dataframe(sql)
	gbhylist=df["GBHY"].tolist()
	dataSet=loadSimpDat()
	L, suppData = AssociationRulesUtil.apriori(dataSet, minSupport=0.02)
	print('频繁项:',L)

	filterItems=[]
	for items in L:
		for frozenset in items:
			for item in frozenset:
				if len(frozenset)>1 and item in gbhylist:
					filterItems.append(frozenset)
					break
	print('过滤项',filterItems)
	# main()
