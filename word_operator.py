# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-：

from docx import Document
from pandas import DataFrame


#解析docx表格中的人才数据
def parse_docx(f):
  info_arr={}
  # 读取docx，返回姓名和行业
  d = Document(f)
  t = d.tables[0]
  rows=t.rows
  head_cells=rows[1].cells
  for cell in head_cells:
    info_arr[cell.text]=[]
  for row in rows[2:]:#跳过第一行标题行
    cells=row.cells
    for i in range(len(cells)):
      cell=cells[i].text
      field_cell=head_cells[i].text
      info_arr[field_cell].append(cell)
  return info_arr
''' 上述函数主要实现文件的读取 '''
if __name__ == "__main__":
  docx_file='D:\\011111111111111111111111\\temp\\1123.docx'
  #从docx文件读取表格信息
  info_arr=parse_docx(docx_file)
  table1_df = DataFrame(info_arr)
  table1_df.to_csv("D:\\011111111111111111111111\\temp\\1123.csv", index=False, sep=',')
  # print(table1_df)