# coding=gbk
""" ��ԭ�е����ݿ��ļ��������ִ����� """

import sqlite3
from tkinter import filedialog, Tk
import xlrd
import datetime
import sys
from db.MssqlHandler import MssqlHandler

root = Tk()
root.withdraw()
db_file = 'produce_datas.db'

conn = sqlite3.connect( db_file )
cur = conn.cursor()

cur.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type=\'table\' AND name=\'storage_part\'' )
rs = cur.fetchone()
if rs[0] == 0:
    print( '����storage_part��...' )
    create_table_sql = """
    CREATE TABLE storage_part
        (
            part_id INT NOT NULL,
            position TEXT NOT NULL,
            stock_1 REAL NOT NULL DEFAULT 0.0,
            lock_stock_1 REAL NOT NULL DEFAULT 0.0,
            update_time_1 DATETIME,
            stock_3 REAL NOT NULL DEFAULT 0.0,
            update_time_3 DATETIME,
            CONSTRAINT pk_storage_part PRIMARY KEY (part_id, position)
        )
    """
    cur.execute( create_table_sql )
    conn.commit()
    print( '���storage_part�Ĵ�����' )

s = input( '�Ƿ����ԭ�еĿ�����ݣ�Y or N��' )
try:
    if s.upper() == 'Y':
        cur.execute( 'DELETE FROM storage_part WHERE part_id>0' )
        conn.commit()
    elif s.upper() == 'N':
        pass
    else:
        raise Exception( '��Чѡ��' )
except Exception as e:
    print( e )
    sys.exit( 1 )

print( '�����ֳ��������ݵ���д...' )
x_file = filedialog.askopenfilename( title='ѡ�������ļ�', filetypes=[("EXCEL�ļ�", ".xls")] )
if x_file:
    print( 'ѡ���ˣ�{0}'.format( x_file ) )
    x = xlrd.open_workbook( x_file )
    for the_sheet in x.sheets():
        n_rows = the_sheet.nrows
        if n_rows < 2:
            continue
        print( f'�������ݱ�{the_sheet.name}...' )
        for i in range( 1, n_rows ):
            one_row = the_sheet.row_values( i, 0, 4 )
            print( one_row )
            the_part_id = int( one_row[0] )
            the_position = one_row[1]
            the_stock = one_row[2]
            the_update_time = one_row[3]
            cur.execute(
                'SELECT * FROM storage_part WHERE part_id={0} AND position=\'{1}\''.format( the_part_id,
                                                                                            the_position ) )
            rs = cur.fetchall()
            do_update = False
            if len( rs ) > 0:
                do_update = True
                the_stock += rs[0][2]
            if str.isspace( the_update_time ) or len( the_update_time ) < 1:
                the_update_time = str( datetime.date.today() )
            if do_update:
                cur.execute(
                    'UPDATE storage_part SET stock_1={0}, update_time_1=\'{1}\' '
                    'WHERE part_id={2} AND position=\'{1}\''.format( the_stock, the_update_time, the_part_id,
                                                                     the_position ) )
            else:
                cur.execute( 'INSERT INTO storage_part VALUES '
                             '({0}, \'{1}\', {2}, 0.0, \'{3}\', 0.0, NULL)'.format( the_part_id,
                                                                                    the_position,
                                                                                    the_stock,
                                                                                    the_update_time ) )
    conn.commit()
print( '����ֳ��������ݵ���д��' )

print( '���вֿ���ÿ������������д...' )
mssql_db = MssqlHandler( '191.1.6.103', 'Greatoo_JJ_Database', 'sa', '8893945' )
x_files = filedialog.askopenfilenames( title='ѡ�������ļ�', filetypes=[("EXCEL�ļ�", ".xls")] )
for x_file in x_files:
    print( 'ѡ����: {0}'.format( x_file ) )
    x = xlrd.open_workbook( x_file )
    the_sheet = x.sheet_by_index( 2 )
    n_rows = the_sheet.nrows
    for i in range( 1, n_rows ):
        one_row = the_sheet.row_values( i, 11, 23 )
        print( one_row )
        erp_id = one_row[0]
        the_stock = float( one_row[5] )
        the_update_time = one_row[11]
        rs = mssql_db.get_tags( name=erp_id, parent_id=2064 )
        if len( rs ) < 1:
            continue
        the_parts = mssql_db.get_parts_2_tag( tag_id=rs[0][0] )
        if len( rs ) < 1:
            continue
        the_part_id = the_parts[0][0]
        cur.execute( 'SELECT * FROM storage_part WHERE part_id={0}'.format( the_part_id ) )
        rs = cur.fetchall()
        if len( rs ) > 0:
            cur.execute( 'UPDATE storage_part SET stock_3={0}, update_time_3=\'{1}\' WHERE part_id={2}'.format(
                the_stock, the_update_time, the_part_id
            ) )
        else:
            cur.execute( 'INSERT INTO storage_part VALUES ({0}, \'T\', 0.0, 0.0, NULL, {1}, \'{2}\')'.format(
                the_part_id, the_stock, the_update_time ) )
conn.commit()
print( '��ɲֿ���ÿ���������䡣' )

mssql_db.close()
cur.close()
conn.close()

"""
�±��

�����ƻ���
CREATE TABLE [produce_plan_list](
  [list_id] TEXT PRIMARY KEY NOT NULL, 
  [plan_status] TEXT NOT NULL DEFAULT '������', 
  [description] TEXT NOT NULL, 
  [finish_date] DATE, 
  CHECK([plan_status] = '������' OR  [plan_status] = '�����'));

�����ƻ�����Ŀ
CREATE TABLE [produce_plan_item](
  [item_id] INT PRIMARY KEY, 
  [index] INT NOT NULL, 
  [plan_list_id] TEXT NOT NULL REFERENCES [produce_plan_list]([list_id]), 
  [description] TEXT NOT NULL, 
  [status] TEXT NOT NULL DEFAULT '������', 
  [finish_date] DATE, 
  CHECK([status] = '������' OR  [status] = '�����'));
  
�����ƻ�����Ŀ�ļƻ����
CREATE TABLE [plan_item_target_material](
  [item_id] INT NOT NULL REFERENCES [produce_plan_item]([item_id]), 
  [index] INT NOT NULL, 
  [part_id] INT NOT NULL, 
  [qty] REAL NOT NULL DEFAULT (1.0), 
  [comment] TEXT, 
  PRIMARY KEY([item_id], [index]));

���ϵ�
CREATE TABLE [pick_item](
  [list_id] INT, 
  [zd_erp_id] TEXT NOT NULL, 
  [qty] REAL NOT NULL, 
  [is_finished] BOOL DEFAULT FALSE, 
  [in_come] REAL NOT NULL DEFAULT (0.0), 
  [_when] DATE NOT NULL, 
  [index] TINYINT NOT NULL, 
  [contract_no] TEXT, 
  [plan_list_id] TEXT NOT NULL REFERENCES [produce_plan_list]([list_id]), 
  PRIMARY KEY([list_id], [index]));

"""
