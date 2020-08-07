import xlwings as xw
import pymssql
import datetime

first_row_index = 3
last_row_index = 60
erp_code_column = 'A'
qty_column = 'D'
unit_price_column = 'G'
store_code = 'E'


def get_part_by_erp_code(c, the_code):
    """
        通过中德ERP编号，获取相应的零件号；
        中德ERP物料编码的 tag_id = 2064
    """
    sql_1 = f'SELECT id FROM JJCom.Tag WHERE parent_id=2064 AND CONVERT(VARCHAR, tag_name)=\'{the_code}\''
    c.execute( sql_1 )
    r = c.fetchall()
    if len( r ) < 1:
        return None
    tag_id = r[0][0]
    sql_2 = f'SELECT part_id FROM JJCom.PartTag WHERE tag_id={tag_id}'
    c.execute( sql_2 )
    r = c.fetchall()
    if len( r ) < 1:
        return None
    return r[0][0]


def insert_one_record(c, part_id, qty, today, unit_price_value):
    """
        插入一个仓储的记录；
        中德仓库的仓位代号为：D。
    """
    sql_2 = f'SELECT * FROM JJStorage.Storing WHERE PartId={part_id} AND Position=\'D\''
    c.execute( sql_2 )
    r = c.fetchall()
    if len( r ) > 0:
        # 是否要进行更新
        return
    sql_1 = f'INSERT INTO JJStorage.Storing VALUES ({part_id}, \'{store_code}\', {qty}, \'{today}\', {unit_price_value})'
    c.execute( sql_1 )


server = '191.1.6.103'
user = 'sa'
password = '8893945'
database = 'Greatoo_JJ_Database'

conn = pymssql.connect( server=server, user=user, password=password, database=database )
c = conn.cursor()

the_date = '{0}'.format( datetime.date.today() )
the_date = '2020/2/19'

for i in range( first_row_index, last_row_index + 1 ):
    the_cell = xw.Range( f'{erp_code_column}{i}' )
    erp_code = the_cell.value
    t = xw.Range( f'{qty_column}{i}' ).value
    qty = float( t )
    print( '{0} -> {1}'.format( erp_code, qty ) )
    the_part = get_part_by_erp_code( c, erp_code )
    if the_part is None:
        the_cell.color = (255, 0, 255)
        continue
    print( 'insert one record' )
    u_t = xw.Range( f'{unit_price_column}{i}' )
    unit_price = float( u_t.value )
    insert_one_record( c, the_part, qty, the_date, unit_price )

conn.commit()
conn.close()
print( 'The End.' )
