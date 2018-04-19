# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 16:02:07 2018

@author: admin
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame,Series
html = urlopen("http://quotes.money.163.com/f10/zycwzb_600639.html#01c02")
bsObj = BeautifulSoup(html, "html.parser")

#表1的字典
table1_dict = {}
#表1的索引
table1_index = bsObj.find("table", {"class":"table_bg001 border_box limit_sale"}).findAll("tr") 
table1_index_list = []
for name in table1_index:
    index = name.get_text(strip=True)
    table1_index_list.append(index)
    table1_dict[index]=0
    
table1_index_list

table1_values = bsObj.find("table", {"class":"table_bg001 border_box limit_sale scr_table"}).findAll("tr") 
i=0
for values in table1_values:
    value_list = values.get_text("|", strip=True).split("|")
    table1_dict[table1_index_list[i]]=value_list
    i+=1

table1_dict


table1_df = DataFrame(table1_dict,columns=table1_index_list)
#print(table1_df)



#其他表的字典
table_dict2=[]
tables = bsObj.find_all("table", {"class":"table_bg001 border_box fund_analys"})
for nortable in tables:
    nortable_dict={}
    nortable_tr_list=nortable.find_all("tr")#所有行信息
    #获取每个表格的表头信息
    i=0
    for tr in nortable_tr_list:
        if(i is 0):
            nortable_dict["时间"]=tr.get_text("|", strip=True).split("|")
        else:
            text = tr.get_text("|", strip=True).split("|")[0]
            value_list= tr.get_text("|", strip=True).split("|")[1:]
            nortable_dict[text]=value_list
        i+=1
    table_dict2.append(nortable_dict)

for table in table_dict2:
    table1_df = DataFrame(table)
    print(table1_df)
