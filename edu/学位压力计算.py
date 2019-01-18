# -*- coding: utf-8 -*-
import pandas as pd
from pandas import DataFrame
import cx_Oracle
from sqlalchemy import create_engine
from util import db_util
from pandas import Series
from edu import schoolarea_person_count


def get_primary_degree():
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
		data['degree_2016'] = degree_2016 * 0.76
		# 2017提供的学位
		degree_2017 = grade_two_person
		data['degree_2017'] = degree_2017 * 0.77
		# 2018提供学位
		degree_2018 = grade_one_person
		data['degree_2018'] = degree_2018 * 0.66
		# 2019提供学位
		if grade_six_person == 0:
			degree_2019 = grade_one_person*0.83
		else:
			degree_2019 = grade_six_person * 0.88
		data['degree_2019'] = degree_2019
		# 2020提供学位
		if grade_five_person == 0:
			degree_2020 = grade_one_person*0.8
		else:
			degree_2020 = round(grade_five_person * 0.83)
		data['degree_2020'] = degree_2020
		# 2021提供学位
		if grade_four_person == 0:
			degree_2021 = grade_one_person*0.8
		else:
			degree_2021 = round(grade_four_person * 0.88)
		data['degree_2021'] = degree_2021
		# 2022 提供学位
		if grade_three_person == 0:
			degree_2022 = grade_one_person*0.8
		else:
			degree_2022 = round(grade_three_person * 0.85)
		data['degree_2022'] = degree_2022
		# 2023提供学位
		if grade_two_person == 0:
			degree_2023 = grade_one_person
		else:
			degree_2023 = round(grade_two_person * 0.8 + grade_one_person * 0.1)
		data['degree_2023'] = degree_2023
		result.append(data)

	return result


def get_middle_degree():
	sql = "SELECT * FROM T_JY_SCHOOL_CLASSINFO WHERE schooltype='初中'"
	df = db_util.execute2Dataframe(sql)
	result = []
	for index, row in df.iterrows():
		school_fullname = row['SCHOOL_FULLNAME']
		schooltype = row['SCHOOLTYPE']
		grade_seven_person = int(row['GRADE_SEVEN_PERSON'])
		grade_eight_person = int(row['GRADE_EIGHT_PERSON'])
		grade_nine_person = int(row['GRADE_NINE_PERSON'])
		data = {'SCHOOL_FULLNAME': school_fullname, 'SCHOOLTYPE': schooltype}
		# 2016提供的学位
		degree_2016 = grade_nine_person
		data['degree_2016'] = degree_2016
		# 2017提供的学位
		degree_2017 = grade_eight_person
		data['degree_2017'] = degree_2017
		# 2018提供学位
		degree_2018 = grade_seven_person
		data['degree_2018'] = degree_2018
		# 2019提供学位
		if grade_nine_person == 0:
			degree_2019 = grade_seven_person*0.8
		else:
			degree_2019 = round(grade_nine_person)
		data['degree_2019'] = degree_2019
		# 2020提供学位
		if grade_eight_person == 0:
			degree_2020 = grade_seven_person
		else:
			degree_2020 = round(grade_eight_person * 0.95 + grade_seven_person * 0.05)
		data['degree_2020'] = degree_2020 * 1.15
		# 2021提供学位
		degree_2021 = grade_seven_person
		data['degree_2021'] = degree_2021 * 1.15
		# 2022 提供学位
		if grade_eight_person == 0:
			degree_2022 = grade_seven_person
		else:
			degree_2022 = round(grade_eight_person * 0.9 + grade_seven_person * 0.12)
		data['degree_2022'] = degree_2022 * 1.15
		# 2023提供学位
		if grade_nine_person == 0:
			degree_2023 = grade_seven_person
		else:
			degree_2023 = round(grade_nine_person * 0.9 + grade_seven_person * 0.2)
		data['degree_2023'] = degree_2023 * 1.15
		result.append(data)

	print(result['degree_2018'].sum())
	return result


def get_primary_degree_pressure(degree_df: DataFrame):
	bmrssql = "SELECT * FROM T_JY_SCHOOL_ENROLLMENT WHERE SCHOOLTYPE='小学'"
	# sql = "SELECT b.SCHOOLNAME,b.SCHOOL_FULLNAME,a.AGE,sum(num) NUM FROM T_JY_SCHOOL_PEOPLE a LEFT JOIN T_JY_SCHOOLAREA b ON a.school=b.SCHOOLNAME WHERE a.age>0 AND b.schooltype ='小学' GROUP BY b.SCHOOLNAME,b.SCHOOL_FULLNAME,a.AGE ORDER BY b.SCHOOLNAME ,a.age"
	# df = db_util.execute2Dataframe(sql)
	df = schoolarea_person_count.request_area_building()
	bmrs_df = db_util.execute2Dataframe(bmrssql)
	bmrs_df['BMRS_2016'].fillna(0, inplace=True)
	bmrs_df['BMRS_2017'].fillna(0, inplace=True)
	bmrs_df['BMRS_2018'].fillna(0, inplace=True)
	degree_pressure_list = []
	for index, row in bmrs_df.iterrows():
		schoolname = row['SCHOOLNAME']
		school_fullname = row['SCHOOL_FULLNAME']
		schooltype = row['SCHOOLTYPE']
		bmrs_2016 = int(row['BMRS_2016'])
		bmrs_2017 = int(row['BMRS_2017'])
		bmrs_2018 = int(row['BMRS_2018'])
		if bmrs_2016 == 0 or bmrs_2017 == 0 or bmrs_2018 == 0:
			continue
		school_person = df[df.SCHOOLNAME == schoolname]
		school_degree = degree_df[degree_df.SCHOOL_FULLNAME == school_fullname]
		school_degree_data = {'school_fullname': school_fullname}
		degree_pressure_list.append(school_degree_data)
		if not school_person.empty:
			try:
				rk_2018=int(school_person[school_person.AGE == 6]['NUM'])
				rkxs_2018 = int(school_person[school_person.AGE == 6]['NUM']) / bmrs_2018
				rkxs_2017 = int(school_person[school_person.AGE == 7]['NUM']) / bmrs_2017
				rkxs_2016 = int(school_person[school_person.AGE == 8]['NUM']) / bmrs_2016
				rkxs = (rkxs_2018 + rkxs_2017 + rkxs_2016 ) / 3*0.87  # 综合前三年人口占报名人数比例得到人口系数
				bmrs_2019 = int(school_person[school_person.AGE == 5]['NUM']) * rkxs
				bmrs_2020 = int(school_person[school_person.AGE == 4]['NUM']) * rkxs
				bmrs_2021 = int(school_person[school_person.AGE == 3]['NUM']) * rkxs
				bmrs_2022 = int(school_person[school_person.AGE == 2]['NUM']) * rkxs
				bmrs_2023 = int(school_person[school_person.AGE == 1]['NUM']) * rkxs
				degree_2016 = int(school_degree['degree_2016'])
				degree_2017 = int(school_degree['degree_2017'])
				degree_2018 = int(school_degree['degree_2018'])
				degree_2019 = int(school_degree['degree_2019'])
				degree_2020 = int(school_degree['degree_2020'])
				degree_2021 = int(school_degree['degree_2021'])
				degree_2022 = int(school_degree['degree_2022'])
				degree_2023 = int(school_degree['degree_2023'])
				degree_pressure_2018_test=rk_2018*rkxs-degree_2018
				school_degree_data['degree_pressure_2018_test'] = degree_pressure_2018_test
				school_degree_data['degree_pressure_2016'] = bmrs_2016 - degree_2016
				school_degree_data['degree_pressure_2017'] = bmrs_2017 - degree_2017
				school_degree_data['degree_pressure_2018'] = bmrs_2018 - degree_2018
				school_degree_data['degree_pressure_2019'] = bmrs_2019 - degree_2019
				school_degree_data['degree_pressure_2020'] = bmrs_2020 - degree_2020
				school_degree_data['degree_pressure_2021'] = bmrs_2021 - degree_2021
				school_degree_data['degree_pressure_2022'] = bmrs_2022 - degree_2022
				school_degree_data['degree_pressure_2023'] = bmrs_2023 - degree_2023

				print(school_fullname+','+bmrs_2019+','+degree_2019+','+str((bmrs_2019- degree_2019)))
			except Exception as e:
				print(e)

	degree_pressure_df = DataFrame(degree_pressure_list)
	degree_pressure_df['degree_pressure_2016'].fillna(degree_pressure_df['degree_pressure_2016'].mean(), inplace=True)
	degree_pressure_df['degree_pressure_2017'].fillna(degree_pressure_df['degree_pressure_2017'].mean(), inplace=True)
	degree_pressure_df['degree_pressure_2018'].fillna(degree_pressure_df['degree_pressure_2018'].mean(), inplace=True)
	degree_pressure_df['degree_pressure_2019'].fillna(degree_pressure_df['degree_pressure_2019'].mean(), inplace=True)
	degree_pressure_df['degree_pressure_2020'].fillna(degree_pressure_df['degree_pressure_2020'].mean(), inplace=True)
	degree_pressure_df['degree_pressure_2021'].fillna(degree_pressure_df['degree_pressure_2021'].mean(), inplace=True)
	degree_pressure_df['degree_pressure_2022'].fillna(degree_pressure_df['degree_pressure_2022'].mean(), inplace=True)
	degree_pressure_df['degree_pressure_2023'].fillna(degree_pressure_df['degree_pressure_2023'].mean(), inplace=True)
	print(degree_pressure_df['degree_pressure_2016'].sum(),degree_pressure_df['degree_pressure_2017'].sum(),degree_pressure_df['degree_pressure_2018'].sum(), degree_pressure_df['degree_pressure_2019'].sum(), degree_pressure_df['degree_pressure_2020'].sum(),
		  degree_pressure_df['degree_pressure_2021'].sum(), degree_pressure_df['degree_pressure_2022'].sum())
	print('test2018:',degree_pressure_df['degree_pressure_2018_test'].sum())
	print(degree_pressure_df[degree_pressure_df.degree_pressure_2016>0]['degree_pressure_2022'].sum())


def get_degree():
	primary_degree_list = get_primary_degree()
	return DataFrame(primary_degree_list)


def compute():
	sql = 'SELECT a.SCHOOLNAME,a.SCHOOL_FULLNAME,a.schooltype FROM T_JY_SCHOOLAREA a LEFT JOIN T_JY_SCHOOL_CLASSINFO b ON a.SCHOOL_FULLNAME=b.SCHOOL_FULLNAME '
	df = db_util.execute2Dataframe(sql)
	degree_df = get_degree()
	get_primary_degree_pressure(degree_df)


if __name__ == '__main__':
	df=get_degree()
	print(df['degree_2016'].sum())
	print(df['degree_2017'].sum())
	print(df['degree_2018'].sum())
	print(df['degree_2019'].sum())
	print(df['degree_2020'].sum())
	print(df['degree_2021'].sum())
	print(df['degree_2022'].sum())
	compute()
