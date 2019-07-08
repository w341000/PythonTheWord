# -*- coding: utf-8 -*-
import pandas as pd
import cx_Oracle
from sqlalchemy import create_engine
from pandas import DataFrame
user='lhdm'
password='lhdm#gov'
url='10.169.11.13:1521/orcl'


def execute2Dataframe(sql:str):
	"""
	执行sql,并将所有结果以DataFrame返回
	:param sql: 
	:return: 
	"""
	# return pd.read_sql(sql,getSqlalchemyEngine())
	db=cx_Oracle.connect(user,password,url)
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
	connectObj = cx_Oracle.connect(user, password, url)
	cr = connectObj.cursor()
	cr.execute(sql)
	connectObj.commit()


def getSqlalchemyEngine(url='oracle+cx_oracle://lhdm:lhdm#gov@10.169.11.13:1521/?service_name=orcL'):
	"""
	:param url: like 'oracle+cx_oracle://lhdm:lhdm#gov@10.169.11.13:1521/?service_name=orcl'
	:return:
	"""
	return create_engine(url)



