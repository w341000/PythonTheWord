#-*- coding=utf-8 -*-
import xlrd


def open_excel(file= 'file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(str(e))

def excel_table_byname(file='D:\\011111111111111111111111\\temp\\test.xls',colnameindex=1,by_index=0):#修改自己路径
     data = open_excel(file)
     table=data.sheet_by_index(by_index)
     # table = data.sheet_by_name(by_name) #获得表格
     nrows = table.nrows  # 拿到总共行数
     colnames = table.row_values(colnameindex)  # 某一行数据 ['姓名', '用户名', '联系方式', '密码']
     list = []
     for rownum in range(colnameindex+1, nrows): #也就是从Excel第二行开始，第一行表头不算
         row = table.row_values(rownum)
         if row:
             app = {}
             for i in range(len(colnames)):
                 app[colnames[i]] = row[i] #表头与数据对应
                 # print(row[i])
             list.append(app)
     return list

def main():
    tables = excel_table_byname()
    for row in tables:
       print(row)
if __name__ =="__main__":
    main()