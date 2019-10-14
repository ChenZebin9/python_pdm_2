# coding=gbk
""" 向原有的数据库文件，填充如仓储数据 """

import sqlite3
from tkinter import filedialog, Tk
import xlrd
import datetime
import sys
from db.MssqlHandler import MssqlHandler

root = Tk()
root.withdraw()
db_file = filedialog.askopenfilename( title='选择数据库文件', filetypes=[("SQLite文件", ".db")] )
if not db_file:
    print( '没有选择文件。' )
    exit( 0 )
print( '选择了：{0}'.format( db_file ) )

conn = sqlite3.connect( db_file )
cur = conn.cursor()

cur.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type=\'table\' AND name=\'storage_part\'' )
rs = cur.fetchone()
if rs[0] == 0:
    print( '创建storage_part表...' )
    create_table_sql = """
    CREATE TABLE storage_part
        (
            part_id INT REFERENCES part (id) NOT NULL,
            position TEXT NOT NULL,
            stock_1 REAL,
            update_time_1 DATETIME,
            stock_3 REAL,
            update_time_3 DATETIME,
            CONSTRAINT pk_storage_part PRIMARY KEY (part_id, position)
        )
    """
    cur.execute( create_table_sql )
    conn.commit()
    print( '完成storage_part的创建。' )

s = input( '是否清空原有的库存数据？Y or N？' )
try:
    if s.upper() == 'Y':
        cur.execute( 'DELETE FROM storage_part WHERE part_id>0' )
        conn.commit()
    elif s.upper() == 'N':
        pass
    else:
        raise Exception( '无效选择！' )
except Exception as e:
    print( e )
    sys.exit( 1 )

print( '进行现场物料数据的填写...' )
x_file = filedialog.askopenfilename( title='选择数据文件', filetypes=[("EXCEL文件", ".xls")] )
if db_file:
    print( '选择了：{0}'.format( x_file ) )
    x = xlrd.open_workbook( x_file )
    the_sheet = x.sheet_by_index( 0 )
    n_rows = the_sheet.nrows
    for i in range( 1, n_rows ):
        one_row = the_sheet.row_values( i, 0, 4 )
        print( one_row )
        the_part_id = int( one_row[0] )
        the_position = one_row[1]
        the_stock = one_row[2]
        the_update_time = one_row[3]
        cur.execute(
            'SELECT * FROM storage_part WHERE part_id={0} AND position=\'{1}\''.format( the_part_id, the_position ) )
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
                         '({0}, \'{1}\', {2}, \'{3}\', NULL, NULL)'.format( the_part_id,
                                                                            the_position,
                                                                            the_stock,
                                                                            the_update_time ) )
    conn.commit()
print( '完成现场物料数据的填写。' )

print( '进行仓库可用库存量的数据填写...' )
mssql_db = MssqlHandler( '191.1.6.103', 'Greatoo_JJ_Database', 'sa', '8893945' )
x_files = filedialog.askopenfilenames( title='选择数据文件', filetypes=[("EXCEL文件", ".xls")] )
for x_file in x_files:
    print( '选择了: {0}'.format( x_file ) )
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
            cur.execute( 'INSERT INTO storage_part VALUES ({0}, \'T\', NULL, NULL, {1}, \'{2}\')'.format(
                the_part_id, the_stock, the_update_time ) )
conn.commit()
print( '完成仓库可用库存的数据填充。' )

mssql_db.close()
cur.close()
conn.close()
