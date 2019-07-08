# -*- coding: utf-8 -*-
from pandas import DataFrame

from util import office_util

file='D:/福田决策文件/其它/国民经济行业分类注释（2011版）.doc'
datas=[]
office_util.word_table_to_list(file, datas)
DataFrame(datas).to_csv("D:\\011111111111111111111111\\00临时文件\\hangyedaima.csv",
										index=False,
										sep=',')