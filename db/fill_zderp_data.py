# coding=gbk
"""
��һ���е�ERP�����Excel���ݣ��������е�����������Ϣ��
�������� ���ϱ��롢������������λ��
"""

import sqlite3
from tkinter import filedialog, Tk
import xlrd
import datetime
import sys
import os

root = Tk()
root.withdraw()
source_file = filedialog.askopenfilename( title='һ�����е�ERP�������ļ�', filetypes=[("EXCEL�ļ�", ".xls")] )
if not source_file:
    print( 'û��ѡ���ļ���' )
    sys.exit( 0 )

database_file = 'zd_erp.db'
if os.path.exists( database_file ):
    os.remove( database_file )

conn = sqlite3.connect( database_file )
cur = conn.cursor()

cur.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type=\'table\' AND name=\'part_info\'' )
rs = cur.fetchone()
if rs[0] == 0:
    print( '���� part_info ��...' )
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
    print( '���� version ��...' )
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

print( '������������...' )
for i in range( 1, n_rows ):
    r = w_sheet.row_values( i, 1, 6 )
    print( r )
    cur.execute( f'INSERT INTO part_info VALUES (\'{r[0]}\', \'{r[2]}\', \'{r[4]}\')' )

print( '����汾����...' )
cur.execute( f'INSERT INTO version VALUES (\'{str( datetime.date.today() )}\')' )

print( '��ɡ�' )
conn.commit()
cur.close()
conn.close()
