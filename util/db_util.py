# -*- coding: utf-8 -*-
import pandas as pd
import cx_Oracle


user='WWYJFX'
password='m123'
url='localhost:1521/orcl'


def execute2Dataframe(sql:str):
	"""
	执行sql,并将所有结果以DataFrame返回
	:param sql: 
	:return: 
	"""
	db=cx_Oracle.connect('WWYJFX','m123','localhost:1521/orcl')
	cr = db.cursor()
	cr.execute(sql)
	rs = cr.fetchall()
	col = cr.description
	columns = []
	for filed in col:
		columns.append(filed[0])
	df = pd.DataFrame(rs, columns=columns)
	db.close()
	return df


def delete(sql):
	connectObj = cx_Oracle.connect('WWYJFX', 'm123', 'localhost:1521/orcl')
	cr = connectObj.cursor()
	cr.execute(sql)
	connectObj.commit()


