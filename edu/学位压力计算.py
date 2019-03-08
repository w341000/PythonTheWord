# -*- coding: utf-8 -*-
import pandas as pd
from pandas import DataFrame
import cx_Oracle
from sqlalchemy import create_engine
from util import db_util
from pandas import Series
from edu import schoolarea_person_count


def get_primary_degree():
	"""
	小学学位计算
	:return:
	"""
	sql = "SELECT * FROM T_JY_SCHOOL_CLASSINFO WHERE schooltype='小学'"
	df = db_util.execute2Dataframe(sql)
	result = []
	for index, row in df.iterrows():
		school_fullname = row['SCHOOL_FULLNAME']
		schooltype = row['SCHOOLTYPE']
		grade_six_person = int(row['GRADE_SIX_PERSON'])
		grade_five_person = int(row['GRADE_FIVE_PERSON'])
		grade_four_person = int(row['GRADE_FOUR_PERSON'])
		grade_three_person = int(row['GRADE_THREE_PERSON'])
		grade_two_person = int(row['GRADE_TWO_PERSON'])
		grade_one_person = int(row['GRADE_ONE_PERSON'])
		data = {'SCHOOL_FULLNAME': school_fullname, 'SCHOOLTYPE': schooltype}
		# 2016提供的学位
		degree_2016 = grade_three_person
		data['degree_2016'] = degree_2016 * 0.75
		# 2017提供的学位
		degree_2017 = grade_two_person
		data['degree_2017'] = degree_2017 * 0.77
		# 2018提供学位
		degree_2018 = grade_one_person
		data['degree_2018'] = degree_2018 * 0.68
		# 2019提供学位
		if grade_six_person == 0:
			degree_2019 = grade_one_person * 0.95
		else:
			degree_2019 = grade_six_person * 0.9
		data['degree_2019'] = degree_2019
		# 2020提供学位
		if grade_five_person == 0:
			degree_2020 = grade_one_person * 0.95
		else:
			degree_2020 = round(grade_five_person * 0.82)
		data['degree_2020'] = degree_2020
		# 2021提供学位
		if grade_four_person == 0:
			degree_2021 = grade_one_person * 0.95
		else:
			degree_2021 = round(grade_four_person * 0.86)
		data['degree_2021'] = degree_2021
		# 2022 提供学位
		if grade_three_person == 0:
			degree_2022 = grade_one_person * 0.95
		else:
			degree_2022 = round(grade_three_person * 0.86)
		data['degree_2022'] = degree_2022
		# 2023提供学位
		if grade_two_person == 0:
			degree_2023 = grade_one_person
		else:
			degree_2023 = round(grade_two_person * 0.88)
		data['degree_2023'] = degree_2023
		result.append(data)

	return DataFrame(result)


def get_middle_degree():
	"""
	中学学位计算
	:return:
	"""
	sql = "SELECT * FROM T_JY_SCHOOL_CLASSINFO WHERE schooltype='初中'"
	df = db_util.execute2Dataframe(sql)
	result = []
	for index, row in df.iterrows():
		school_fullname = row['SCHOOL_FULLNAME']
		schooltype = row['SCHOOLTYPE']
		grade_seven_person = float(row['GRADE_SEVEN_PERSON'])
		grade_eight_person = float(row['GRADE_EIGHT_PERSON'])
		grade_nine_person = float(row['GRADE_NINE_PERSON'])
		data = {'SCHOOL_FULLNAME': school_fullname, 'SCHOOLTYPE': schooltype}
		# 2016提供的学位
		degree_2016 = grade_nine_person
		data['degree_2016'] = degree_2016
		# 2017提供的学位
		degree_2017 = grade_eight_person
		data['degree_2017'] = degree_2017
		# 2018提供学位
		degree_2018 = grade_seven_person
		data['degree_2018'] = degree_2018*0.97
		# 2019提供学位
		data['degree_2019'] = grade_nine_person*1.1
		# 2020提供学位
		data['degree_2020'] = grade_eight_person
		# 2021提供学位
		degree_2021 = grade_seven_person*0.95
		data['degree_2021'] = degree_2021
		# 2022 提供学位
		degree_2022 = grade_nine_person*1.05
		data['degree_2022'] = degree_2022
		# 2023提供学位
		degree_2023 = grade_eight_person * 1.07
		data['degree_2023'] = degree_2023
		result.append(data)

	return DataFrame(result)


def get_primary_degree_pressure(degree_df: DataFrame):
	"""
	小学学位缺口计算使用户籍和流动人口()
	:param degree_df:
	:return:
	"""
	global rkxs_2018
	try:
		bmrssql = "SELECT A.SCHOOL_FULLNAME,b.schoolname AS SCHOOLNAME, A.LQRS_2016,A.BMRS_2016,A.LQRS_2017,\
			A.BMRS_2017,\
			A.LQRS_2018,\
			A.BMRS_2018,\
			'小学' AS SCHOOLTYPE\
			FROM \
			(SELECT * FROM T_JY_SCHOOL_ENROLLMENT WHERE SCHOOLTYPE='小学') A \
			FULL JOIN  \
			(SELECT * FROM T_JY_SCHOOLAREA WHERE SCHOOLTYPE='小学')\
			B ON A.SCHOOL_FULLNAME = B.SCHOOL_FULLNAME "
		# sql = "SELECT b.SCHOOLNAME,b.SCHOOL_FULLNAME,a.AGE,sum(num) NUM FROM T_JY_SCHOOL_PEOPLE a LEFT JOIN T_JY_SCHOOLAREA b ON a.school=b.SCHOOLNAME WHERE a.age>0 AND b.schooltype ='小学' GROUP BY b.SCHOOLNAME,b.SCHOOL_FULLNAME,a.AGE ORDER BY b.SCHOOLNAME ,a.age"
		# df = db_util.execute2Dataframe(sql)
		df = schoolarea_person_count.request_area_building()
		bmrs_df = db_util.execute2Dataframe(bmrssql)
		bmrs_df['BMRS_2016'].fillna(0, inplace=True)
		bmrs_df['BMRS_2017'].fillna(0, inplace=True)
		bmrs_df['BMRS_2018'].fillna(0, inplace=True)
		# bmrs_df['BMRS_2016'].fillna(bmrs_df['BMRS_2016'].mean(), inplace=True)
		# bmrs_df['BMRS_2017'].fillna(bmrs_df['BMRS_2017'].mean(), inplace=True)
		# bmrs_df['BMRS_2018'].fillna(bmrs_df['BMRS_2018'].mean(), inplace=True)
		degree_pressure_list = []
		count = 0
		for index, row in bmrs_df.iterrows():
			school_fullname = row['SCHOOL_FULLNAME']
			schoolname = row['SCHOOLNAME']
			schooltype = row['SCHOOLTYPE']
			bmrs_2016 = row['BMRS_2016']
			bmrs_2017 = row['BMRS_2017']
			bmrs_2018 = row['BMRS_2018']
			school_person_hjrk = df[(df.SCHOOLNAME == schoolname) & (df.RKXZ == '深圳户籍人口')]
			school_person_ldrk = df[(df.SCHOOLNAME == schoolname) & (df.RKXZ == '流动人口')]
			school_degree = degree_df[degree_df.SCHOOL_FULLNAME == school_fullname]
			school_degree_data = {'SCHOOL_FULLNAME': school_fullname, 'SCHOOLNAME': schoolname,'SCHOOLTYPE':schooltype}
			degree_pressure_list.append(school_degree_data)
			try:
				degree_2016 = int(school_degree['degree_2016'])
				degree_2017 = int(school_degree['degree_2017'])
				degree_2018 = int(school_degree['degree_2018'])
				degree_2019 = int(school_degree['degree_2019'])
				degree_2020 = int(school_degree['degree_2020'])
				degree_2021 = int(school_degree['degree_2021'])
				degree_2022 = int(school_degree['degree_2022'])
				degree_2023 = int(school_degree['degree_2023'])
			except Exception as e:
				print(schoolname, '获取学位信息失败', e)
			school_degree_data['ZSRS_2016'] = degree_2016
			school_degree_data['ZSRS_2017'] = degree_2017
			school_degree_data['ZSRS_2018'] = degree_2018
			school_degree_data['ZSRS_2019'] = degree_2019
			school_degree_data['ZSRS_2020'] = degree_2020
			school_degree_data['ZSRS_2021'] = degree_2021
			school_degree_data['ZSRS_2022'] = degree_2022
			school_degree_data['ZSRS_2023'] = degree_2023

			school_degree_data['BMRS_2016'] = bmrs_2016
			school_degree_data['BMRS_2017'] = bmrs_2017
			school_degree_data['BMRS_2018'] = bmrs_2018
			if school_degree.empty:
				continue
			if not school_person_hjrk.empty:
				try:
					ldrk_2018 = int(school_person_ldrk[school_person_ldrk.AGE == 6]['NUM'])
					rk_2018 = int(school_person_hjrk[school_person_hjrk.AGE == 6]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 6]['NUM'])
					rkxs_2018 = (int(school_person_hjrk[school_person_hjrk.AGE == 6]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 6]['NUM'])) / (bmrs_2018 * 1.04)
					rkxs_2017 = (int(school_person_hjrk[school_person_hjrk.AGE == 7]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 7]['NUM'])) / (bmrs_2017 * 1.04)
					rkxs_2016 = (int(school_person_hjrk[school_person_hjrk.AGE == 8]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 8]['NUM'])) / (bmrs_2016 * 1.04)
					rkxs = (rkxs_2018 + rkxs_2017 + rkxs_2016) / 3  # 综合前三年人口占报名人数比例得到人口系数
				except Exception as e:
					print(e, '取2018年的人口系数')
					rkxs = rkxs_2018  # 取2018年的人口系数
				bmrs_2019 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 5]['NUM']) + ldrk_2018 * 0.8455399) / rkxs*0.99
				bmrs_2020 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 4]['NUM']) + ldrk_2018 * 0.9358372) / rkxs*0.99
				bmrs_2021 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 3]['NUM']) + ldrk_2018 * 0.8276212) / rkxs*0.99
				bmrs_2022 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 2]['NUM']) + ldrk_2018 * 1.0738654) / rkxs*0.99
				bmrs_2023 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 1]['NUM']) + ldrk_2018 * 0.9680751) / rkxs*0.99
				count = count + bmrs_2019
				degree_pressure_2018_test = rk_2018 / rkxs * 0.925 - degree_2018
				# school_degree_data['degree_pressure_2018_test'] = degree_pressure_2018_test
				school_degree_data['BMRS_2016'] = int(bmrs_2016)
				school_degree_data['BMRS_2017'] = int(bmrs_2017)
				school_degree_data['BMRS_2018'] = int(bmrs_2018)
				school_degree_data['BMRS_2019'] = int(bmrs_2019)
				school_degree_data['BMRS_2020'] = int(bmrs_2020)
				school_degree_data['BMRS_2021'] = int(bmrs_2021)
				school_degree_data['BMRS_2022'] = int(bmrs_2022)
				school_degree_data['BMRS_2023'] = int(bmrs_2023)

				school_degree_data['degree_pressure_2016'] = int(bmrs_2016) - int(degree_2016)
				school_degree_data['degree_pressure_2017'] = int(bmrs_2017) - int(degree_2017)
				school_degree_data['degree_pressure_2018'] = int(bmrs_2018) - int(degree_2018)
				school_degree_data['degree_pressure_2019'] = int(bmrs_2019) - int(degree_2019)
				school_degree_data['degree_pressure_2020'] = int(bmrs_2020) - int(degree_2020)
				school_degree_data['degree_pressure_2021'] = int(bmrs_2021) - int(degree_2021)
				school_degree_data['degree_pressure_2022'] = int(bmrs_2022) - int(degree_2022)
				school_degree_data['degree_pressure_2023'] = int(bmrs_2023) - int(degree_2023)
		degree_pressure_df = DataFrame(degree_pressure_list)
		degree_pressure_df['BMRS_2016'].fillna(0, inplace=True)
		degree_pressure_df['BMRS_2017'].fillna(0, inplace=True)
		degree_pressure_df['BMRS_2018'].fillna(int(degree_pressure_df['BMRS_2018'].mean()), inplace=True)
		degree_pressure_df['BMRS_2020'].fillna(int(degree_pressure_df['BMRS_2019'].mean()), inplace=True)
		degree_pressure_df['BMRS_2021'].fillna(int(degree_pressure_df['BMRS_2020'].mean()), inplace=True)
		degree_pressure_df['BMRS_2022'].fillna(int(degree_pressure_df['BMRS_2021'].mean()), inplace=True)
		degree_pressure_df['BMRS_2023'].fillna(int(degree_pressure_df['BMRS_2022'].mean()), inplace=True)
		degree_pressure_df['BMRS_2019'].fillna(int(degree_pressure_df['BMRS_2023'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2016'].fillna(0, inplace=True)
		degree_pressure_df['ZSRS_2017'].fillna(0, inplace=True)
		degree_pressure_df['ZSRS_2018'].fillna(int(degree_pressure_df['ZSRS_2018'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2019'].fillna(int(degree_pressure_df['ZSRS_2019'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2020'].fillna(int(degree_pressure_df['ZSRS_2020'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2021'].fillna(int(degree_pressure_df['ZSRS_2021'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2022'].fillna(int(degree_pressure_df['ZSRS_2022'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2023'].fillna(int(degree_pressure_df['ZSRS_2023'].mean()), inplace=True)

		# degree_pressure_df['degree_pressure_2018_test'].fillna(degree_pressure_df['degree_pressure_2018_test'].mean(),
		# 													   inplace=True)
		# degree_pressure_df['degree_pressure_2018_test'] = degree_pressure_df['degree_pressure_2018_test'].astype(int)
		degree_pressure_df['degree_pressure_2016'] = degree_pressure_df['BMRS_2016'] - degree_pressure_df['ZSRS_2016']
		degree_pressure_df['degree_pressure_2017'] = degree_pressure_df['BMRS_2017'] - degree_pressure_df['ZSRS_2017']
		degree_pressure_df['degree_pressure_2018'] = degree_pressure_df['BMRS_2018'] - degree_pressure_df['ZSRS_2018']
		degree_pressure_df['degree_pressure_2019'] = degree_pressure_df['BMRS_2019'] - degree_pressure_df['ZSRS_2019']
		degree_pressure_df['degree_pressure_2020'] = degree_pressure_df['BMRS_2020'] - degree_pressure_df['ZSRS_2020']
		degree_pressure_df['degree_pressure_2021'] = degree_pressure_df['BMRS_2021'] - degree_pressure_df['ZSRS_2021']
		degree_pressure_df['degree_pressure_2022'] = degree_pressure_df['BMRS_2022'] - degree_pressure_df['ZSRS_2022']
		degree_pressure_df['degree_pressure_2023'] = degree_pressure_df['BMRS_2023'] - degree_pressure_df['ZSRS_2023']
		print(degree_pressure_df[degree_pressure_df.degree_pressure_2016 > 0]['degree_pressure_2016'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2017 > 0]['degree_pressure_2017'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2018 > 0]['degree_pressure_2018'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2019 > 0]['degree_pressure_2019'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2020 > 0]['degree_pressure_2020'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2021 > 0]['degree_pressure_2021'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2022 > 0]['degree_pressure_2022'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2023 > 0]['degree_pressure_2023'].sum())
		# print('test2018:',degree_pressure_df[degree_pressure_df.degree_pressure_2018_test > 0]['degree_pressure_2018_test'].sum())
		print(degree_pressure_df[degree_pressure_df.degree_pressure_2017 > 0]['degree_pressure_2017'].sum())
		print('学位信息')
		print(degree_pressure_df['ZSRS_2016'].sum(), degree_pressure_df['ZSRS_2017'].sum(),
			  degree_pressure_df['ZSRS_2018'].sum())
		print(degree_pressure_df['ZSRS_2019'].sum(), degree_pressure_df['ZSRS_2020'].sum(),
			  degree_pressure_df['ZSRS_2021'].sum())
		print(degree_pressure_df['ZSRS_2022'].sum(), degree_pressure_df['ZSRS_2023'].sum())
		return degree_pressure_df
	except Exception as e:
		print(e)


def get_middle_degree_pressure(degree_df: DataFrame):
	"""
	初中学位缺口计算使用户籍和流动人口()
	:param degree_df:
	:return:
	"""
	global rkxs_2018
	try:
		bmrssql = "SELECT A.SCHOOL_FULLNAME,b.schoolname AS SCHOOLNAME, A.LQRS_2016,A.BMRS_2016,A.LQRS_2017,\
			A.BMRS_2017,\
			A.LQRS_2018,\
			A.BMRS_2018,\
			'初中' AS SCHOOLTYPE\
			FROM \
			(SELECT * FROM T_JY_SCHOOL_ENROLLMENT WHERE SCHOOLTYPE='初中') A \
			right JOIN  \
			(SELECT * FROM T_JY_SCHOOLAREA WHERE SCHOOLTYPE='初中')\
			B ON A.SCHOOL_FULLNAME = B.SCHOOL_FULLNAME "
		# sql = "SELECT b.SCHOOLNAME,b.SCHOOL_FULLNAME,a.AGE,sum(num) NUM FROM T_JY_SCHOOL_PEOPLE a LEFT JOIN T_JY_SCHOOLAREA b ON a.school=b.SCHOOLNAME WHERE a.age>0 AND b.schooltype ='小学' GROUP BY b.SCHOOLNAME,b.SCHOOL_FULLNAME,a.AGE ORDER BY b.SCHOOLNAME ,a.age"
		# df = db_util.execute2Dataframe(sql)
		df = schoolarea_person_count.request_area_building()
		bmrs_df = db_util.execute2Dataframe(bmrssql)
		bmrs_df['BMRS_2016'].fillna(int(bmrs_df['BMRS_2016'].mean()), inplace=True)
		bmrs_df['BMRS_2017'].fillna(int(bmrs_df['BMRS_2017'].mean()), inplace=True)
		bmrs_df['BMRS_2018'].fillna(int(bmrs_df['BMRS_2018'].mean()), inplace=True)
		# bmrs_df['BMRS_2016'].fillna(bmrs_df['BMRS_2016'].mean(), inplace=True)
		# bmrs_df['BMRS_2017'].fillna(bmrs_df['BMRS_2017'].mean(), inplace=True)
		# bmrs_df['BMRS_2018'].fillna(bmrs_df['BMRS_2018'].mean(), inplace=True)
		degree_pressure_list = []
		count = 0
		for index, row in bmrs_df.iterrows():
			school_fullname = row['SCHOOL_FULLNAME']
			schoolname = row['SCHOOLNAME']
			schooltype = row['SCHOOLTYPE']
			bmrs_2016 = row['BMRS_2016']
			bmrs_2017 = row['BMRS_2017']
			bmrs_2018 = row['BMRS_2018']
			school_person_hjrk = df[(df.SCHOOLNAME == schoolname) &(df.SCHOOLTYPE=='初中')& (df.RKXZ == '深圳户籍人口')]
			school_person_ldrk = df[(df.SCHOOLNAME == schoolname) &(df.SCHOOLTYPE=='初中')& (df.RKXZ == '流动人口')]
			school_degree = degree_df[degree_df.SCHOOL_FULLNAME == school_fullname]
			school_degree_data = {'SCHOOL_FULLNAME': school_fullname, 'SCHOOLNAME': schoolname,'SCHOOLTYPE':schooltype}
			degree_pressure_list.append(school_degree_data)
			try:
				degree_2016 = int(school_degree['degree_2016'])
				degree_2017 = int(school_degree['degree_2017'])
				degree_2018 = int(school_degree['degree_2018'])
				degree_2019 = int(school_degree['degree_2019'])
				degree_2020 = int(school_degree['degree_2020'])
				degree_2021 = int(school_degree['degree_2021'])
				degree_2022 = int(school_degree['degree_2022'])
				degree_2023 = int(school_degree['degree_2023'])
			except Exception as e:
				print(schoolname, '获取学位信息失败', e)
			school_degree_data['ZSRS_2016'] = degree_2016
			school_degree_data['ZSRS_2017'] = degree_2017
			school_degree_data['ZSRS_2018'] = degree_2018
			school_degree_data['ZSRS_2019'] = degree_2019
			school_degree_data['ZSRS_2020'] = degree_2020
			school_degree_data['ZSRS_2021'] = degree_2021
			school_degree_data['ZSRS_2022'] = degree_2022
			school_degree_data['ZSRS_2023'] = degree_2023

			school_degree_data['BMRS_2016'] = bmrs_2016
			school_degree_data['BMRS_2017'] = bmrs_2017
			school_degree_data['BMRS_2018'] = bmrs_2018

			ldrk_2018 = int(school_person_ldrk[school_person_ldrk.AGE == 12]['NUM'])
			ldrk_2019 = int(school_person_ldrk[school_person_ldrk.AGE == 11]['NUM'])
			ldrk_2020 = int(school_person_ldrk[school_person_ldrk.AGE == 10]['NUM'])
			ldrk_2021 = int(school_person_ldrk[school_person_ldrk.AGE == 9]['NUM'])
			ldrk_2022 = int(school_person_ldrk[school_person_ldrk.AGE == 8]['NUM'])
			ldrk_2023 = int(school_person_ldrk[school_person_ldrk.AGE == 7]['NUM'])
			if school_degree.empty:
				continue
			if not school_person_hjrk.empty:
				try:
					rk_2016 = int(school_person_hjrk[school_person_hjrk.AGE == 14]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 14]['NUM'])
					rk_2017 = int(school_person_hjrk[school_person_hjrk.AGE == 13]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 13]['NUM'])
					rk_2018 = int(school_person_hjrk[school_person_hjrk.AGE == 12]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 12]['NUM'])
					rkxs_2018 = (int(school_person_hjrk[school_person_hjrk.AGE == 12]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 12]['NUM'])) / (bmrs_2018*1.12)
					rkxs_2017 = (int(school_person_hjrk[school_person_hjrk.AGE == 13]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 13]['NUM'])) / (bmrs_2017*1.12)
					rkxs_2016 = (int(school_person_hjrk[school_person_hjrk.AGE == 14]['NUM']) + int(
						school_person_ldrk[school_person_ldrk.AGE == 14]['NUM'])) / (bmrs_2016*1.12)
					rkxs = (rkxs_2018 + rkxs_2017 + rkxs_2016) / 3  # 综合前三年人口占报名人数比例得到人口系数
				except Exception as e:
					print(e, '取2018年的人口系数')
					rkxs = rkxs_2018  # 取2018年的人口系数
				bmrs_2019 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 11]['NUM']) + ldrk_2019) / rkxs * 0.75
				bmrs_2020 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 10]['NUM']) + ldrk_2020) / rkxs * 0.75
				bmrs_2021 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 9]['NUM']) + ldrk_2021) / rkxs * 0.75
				bmrs_2022 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 8]['NUM']) + ldrk_2022) / rkxs * 0.75
				bmrs_2023 = (int(
					school_person_hjrk[school_person_hjrk.AGE == 7]['NUM']) + ldrk_2023) / rkxs * 0.75
				count = count + bmrs_2019
				degree_pressure_2018_test = rk_2016 / rkxs * 0.9 - degree_2018
				# school_degree_data['degree_pressure_2018_test'] = degree_pressure_2018_test
				school_degree_data['BMRS_2016'] = int(bmrs_2016)
				school_degree_data['BMRS_2017'] = int(bmrs_2017)
				school_degree_data['BMRS_2018'] = int(bmrs_2018)
				school_degree_data['BMRS_2019'] = int(bmrs_2019)
				school_degree_data['BMRS_2020'] = int(bmrs_2020)
				school_degree_data['BMRS_2021'] = int(bmrs_2021)
				school_degree_data['BMRS_2022'] = int(bmrs_2022)
				school_degree_data['BMRS_2023'] = int(bmrs_2023)

				school_degree_data['degree_pressure_2016'] = int(bmrs_2016) - int(degree_2016)
				school_degree_data['degree_pressure_2017'] = int(bmrs_2017) - int(degree_2017)
				school_degree_data['degree_pressure_2018'] = int(bmrs_2018) - int(degree_2018)
				school_degree_data['degree_pressure_2019'] = int(bmrs_2019) - int(degree_2019)
				school_degree_data['degree_pressure_2020'] = int(bmrs_2020) - int(degree_2020)
				school_degree_data['degree_pressure_2021'] = int(bmrs_2021) - int(degree_2021)
				school_degree_data['degree_pressure_2022'] = int(bmrs_2022) - int(degree_2022)
				school_degree_data['degree_pressure_2023'] = int(bmrs_2023) - int(degree_2023)
		degree_pressure_df = DataFrame(degree_pressure_list)
		degree_pressure_df['BMRS_2016'].fillna(int(degree_pressure_df['BMRS_2016'].mean()), inplace=True)
		degree_pressure_df['BMRS_2017'].fillna(int(degree_pressure_df['BMRS_2017'].mean()), inplace=True)
		degree_pressure_df['BMRS_2018'].fillna(int(degree_pressure_df['BMRS_2018'].mean()), inplace=True)
		degree_pressure_df['BMRS_2020'].fillna(int(degree_pressure_df['BMRS_2019'].mean()), inplace=True)
		degree_pressure_df['BMRS_2021'].fillna(int(degree_pressure_df['BMRS_2020'].mean()), inplace=True)
		degree_pressure_df['BMRS_2022'].fillna(int(degree_pressure_df['BMRS_2021'].mean()), inplace=True)
		degree_pressure_df['BMRS_2023'].fillna(int(degree_pressure_df['BMRS_2022'].mean()), inplace=True)
		degree_pressure_df['BMRS_2019'].fillna(int(degree_pressure_df['BMRS_2023'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2016'].fillna(int(degree_pressure_df['ZSRS_2016'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2017'].fillna(int(degree_pressure_df['ZSRS_2017'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2018'].fillna(int(degree_pressure_df['ZSRS_2018'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2019'].fillna(int(degree_pressure_df['ZSRS_2019'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2020'].fillna(int(degree_pressure_df['ZSRS_2020'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2021'].fillna(int(degree_pressure_df['ZSRS_2021'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2022'].fillna(int(degree_pressure_df['ZSRS_2022'].mean()), inplace=True)
		degree_pressure_df['ZSRS_2023'].fillna(int(degree_pressure_df['ZSRS_2023'].mean()), inplace=True)

		# degree_pressure_df['degree_pressure_2018_test'].fillna(degree_pressure_df['degree_pressure_2018_test'].mean(),
		# 													   inplace=True)
		# degree_pressure_df['degree_pressure_2018_test'] = degree_pressure_df['degree_pressure_2018_test'].astype(int)
		degree_pressure_df['degree_pressure_2016'] = degree_pressure_df['BMRS_2016'] - degree_pressure_df['ZSRS_2016']
		degree_pressure_df['degree_pressure_2017'] = degree_pressure_df['BMRS_2017'] - degree_pressure_df['ZSRS_2017']
		degree_pressure_df['degree_pressure_2018'] = degree_pressure_df['BMRS_2018'] - degree_pressure_df['ZSRS_2018']
		degree_pressure_df['degree_pressure_2019'] = degree_pressure_df['BMRS_2019'] - degree_pressure_df['ZSRS_2019']
		degree_pressure_df['degree_pressure_2020'] = degree_pressure_df['BMRS_2020'] - degree_pressure_df['ZSRS_2020']
		degree_pressure_df['degree_pressure_2021'] = degree_pressure_df['BMRS_2021'] - degree_pressure_df['ZSRS_2021']
		degree_pressure_df['degree_pressure_2022'] = degree_pressure_df['BMRS_2022'] - degree_pressure_df['ZSRS_2022']
		degree_pressure_df['degree_pressure_2023'] = degree_pressure_df['BMRS_2023'] - degree_pressure_df['ZSRS_2023']
		print(degree_pressure_df[degree_pressure_df.degree_pressure_2016 > 0]['degree_pressure_2016'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2017 > 0]['degree_pressure_2017'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2018 > 0]['degree_pressure_2018'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2019 > 0]['degree_pressure_2019'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2020 > 0]['degree_pressure_2020'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2021 > 0]['degree_pressure_2021'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2022 > 0]['degree_pressure_2022'].sum(),
			  degree_pressure_df[degree_pressure_df.degree_pressure_2023 > 0]['degree_pressure_2023'].sum())
		# print('test2018:',degree_pressure_df[degree_pressure_df.degree_pressure_2018_test > 0]['degree_pressure_2018_test'].sum())
		print(degree_pressure_df[degree_pressure_df.degree_pressure_2017 > 0]['degree_pressure_2017'].sum())
		print('学位信息')
		print(degree_pressure_df['ZSRS_2016'].sum(), degree_pressure_df['ZSRS_2017'].sum(),
			  degree_pressure_df['ZSRS_2018'].sum())
		print(degree_pressure_df['ZSRS_2019'].sum(), degree_pressure_df['ZSRS_2020'].sum(),
			  degree_pressure_df['ZSRS_2021'].sum())
		print(degree_pressure_df['ZSRS_2022'].sum(), degree_pressure_df['ZSRS_2023'].sum())
		return degree_pressure_df
	except Exception as e:
		print(e)


def compute():
	primary_degree_pressure=get_primary_degree_pressure(get_primary_degree())
	middle_degree_pressure=get_middle_degree_pressure(get_middle_degree())
	primary_degree_pressure.to_excel('D:\\pypy\\pythonresult\\教育学位\\预测小一学位缺口.xls', index=False)
	middle_degree_pressure.to_excel('D:\\pypy\\pythonresult\\教育学位\\预测初一学位缺口.xls',index=False)
	df=DataFrame()
	df=df.append(primary_degree_pressure)
	df=df.append(middle_degree_pressure)
	datas=[]
	for index,row in df.iterrows():
		schoolname = row['SCHOOLNAME']
		schooltype = row['SCHOOLTYPE']
		school_fullname = row['SCHOOL_FULLNAME']
		for i in range(2016,2024):
			year=i
			zsrs='ZSRS_'+str(i)
			bmrs='BMRS_'+str(i)
			degree_pressure='degree_pressure_'+str(i)
			data = {'schoolname':schoolname,'schooltype':schooltype,'school_fullname':school_fullname,'year':year,'zsrs':row[zsrs],'bmrs':row[bmrs],'degree_pressure':row[degree_pressure]}
			datas.append(data)
	formatDf=DataFrame(datas)
	# print(formatDf)

	formatDf.to_excel('D:\\pypy\\pythonresult\\教育学位\\小一初一学位缺口预警.xls',index=False)
	conn_str='oracle+cx_oracle://WWYJFX:m123@localhost:1521/orcl'
	engine=create_engine(conn_str)
	db_util.delete('delete from T_JY_SCHOOL_DEGREE_PRESSURE')
	formatDf.to_sql('T_JY_SCHOOL_DEGREE_PRESSURE',con=engine,if_exists='append',index=False)
	# print(degree_pressure_df)


if __name__ == '__main__':
	# df = DataFrame(get_middle_degree())
	# print(df['degree_2016'].sum(), df['degree_2017'].sum(),
	# 	  df['degree_2018'].sum())
	# print(df['degree_2019'].sum(), df['degree_2020'].sum(),
	# 		  df['degree_2021'].sum())
	# print(df['degree_2022'].sum(), df['degree_2023'].sum())
	compute()
