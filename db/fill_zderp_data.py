# coding=gbk
"""
从一个中德ERP输出的Excel数据，导入其中的物料描述信息。
仅包括： 物料编码、物料描述、单位。
"""

import sqlite3
import pymssql
from tkinter import filedialog, Tk
import xlrd
import datetime
import sys
import os

mode = 0  # mode=1：sqlite3模式，mode=0：在线mssql模式

root = Tk()
root.withdraw()
source_file = filedialog.askopenfilename( title='一个从中德ERP导出的文件', filetypes=[("EXCEL文件", ".xls")] )
if not source_file:
    print( '没有选择文件。' )
    sys.exit( 0 )

if mode == 1:
    database_file = 'zd_erp.db'
    if os.path.exists( database_file ):
        os.remove( database_file )

    conn = sqlite3.connect( database_file )
    cur = conn.cursor()

    cur.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type=\'table\' AND name=\'part_info\'' )
    rs = cur.fetchone()
    if rs[0] == 0:
        print( '创建 part_info 表...' )
        create_table_sql = """
        CREATE TABLE part_info
        (
            erp_id TEXT NOT NULL,
            description TEXT NOT NULL,
            unit TEXT NOT NULL,
            CONSTRAINT pk_part_info PRIMARY KEY (erp_id)
        )
        """
        cur.execute( create_table_sql )
        conn.commit()

    cur.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type=\'table\' AND name=\'version\'' )
    rs = cur.fetchone()
    if rs[0] == 0:
        print( '创建 version 表...' )
        create_table_sql = """
        CREATE TABLE version
        (
            the_date DATETIME NOT NULL,
            CONSTRAINT pk_version PRIMARY KEY (the_date)
        )
        """
        cur.execute( create_table_sql )
        conn.commit()

    w_book = xlrd.open_workbook( source_file )
    w_sheet = w_book.sheet_by_index( 0 )
    n_rows = w_sheet.nrows

    print( '插入物料数据...' )
    for i in range( 1, n_rows ):
        r = w_sheet.row_values( i, 1, 6 )
        print( r )
        cur.execute( f'INSERT INTO part_info VALUES (\'{r[0]}\', \'{r[2]}\', \'{r[4]}\')' )

    print( '插入版本数据...' )
    cur.execute( f'INSERT INTO version VALUES (\'{str( datetime.date.today() )}\')' )
else:
    server = '191.1.6.103'
    database = 'Greatoo_JJ_Database'
    user = 'sa'
    password = '8893945'
    conn = pymssql.connect( server=server, user=user, password=password, database=database,
                            login_timeout=10 )
    cur = conn.cursor()
    w_book = xlrd.open_workbook( source_file )
    w_sheet = w_book.sheet_by_index( 0 )
    n_rows = w_sheet.nrows

    print( '插入物料数据...' )
    for i in range( 1, n_rows ):
        r = w_sheet.row_values( i, 1, 6 )
        cur.execute( f'SELECT * FROM JJPart.ZdErp WHERE ErpId=\'{r[0]}\'' )
        rs = cur.fetchall()
        if len( rs ) > 0:
            if r[2] != rs[0][1]:
                cur.execute(f'UPDATE [JJPart].[ZdErp] SET [Description]=\'{r[2]}\' WHERE [ErpId]=\'{r[0]}\'')
                print(f'更新了：{r[0]} {r[2]} {r[4]}。')
        else:
            print( f'添加了：{r[0]} {r[2]} {r[4]}。' )
            cur.execute( f'INSERT INTO JJPart.ZdErp VALUES (\'{r[0]}\', \'{r[2]}\', \'{r[4]}\')' )

print( '完成。' )
nothing = input('按任意键退出……')
conn.commit()
cur.close()
conn.close()
