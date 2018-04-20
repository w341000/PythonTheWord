# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-：
import urllib
import win32com,re
from win32com.client import Dispatch,constants
from docx import Document
import pandas as pd
import os
from pandas import DataFrame, Series




#删除文件
def  delete_file(f):
  if os.path.exists(f):
    # 删除文件，可使用以下两种方法。
    os.remove(f)
  else:
    pass
#解析docx表格中的人才数据
def parse_docx(f,person_info):
  # 读取docx，返回姓名和行业
  d = Document(f)
  t = d.tables[0]
  rows=t.rows
  for row in rows[1:]:#跳过第一行标题行
    cells=row.cells
    person_info["工作单位"].append(cells[1].text)
    person_info["姓名"].append(cells[2].text)
    person_info["认定级别"].append(cells[3].text)
    person_info["主要认定依据"].append(cells[4].text)

person_info={}
person_info["工作单位"]=[]
person_info["姓名"]=[]
person_info["认定级别"]=[]
person_info["主要认定依据"]=[]
''' 上述函数主要实现文件的读取 '''
if __name__ == "__main__":
  url='http://www.szhrss.gov.cn/ztfw/gccrc/xwgg/gccrc/201507/P020150721353707960017.doc'
  local = 'D:\\011111111111111111111111\\temp\\temp_rencai.doc'
  urllib.request.urlretrieve(url, local)#下载doc文件
  #将doc文件转为docx文件
  word =win32com.client.Dispatch('Word.Application')
  doc = word.Documents.Open(local)
  docx_file='D:\\011111111111111111111111\\temp\\temp_rencai.docx'
  doc.SaveAs(docx_file, 12, False, "", True, "", False, False, False, False)  # 转化后路径下的文件
  doc.Close()
  word.Quit()
  delete_file(local)
  #从docx文件读取表格信息
  parse_docx(docx_file,person_info)
  delete_file(docx_file)
  table1_df = DataFrame(person_info)
  print(table1_df)