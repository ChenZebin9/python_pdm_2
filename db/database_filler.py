import pymssql
import sqlite3
from sqlite3 import Error

conn = pymssql.connect(server='191.1.6.103', user='sa', password='8893945', database='Greatoo_JJ_Database')
c = conn.cursor()

fill_mission = (1, 1, 1, 1, 1, 1)
# fill_mission = (0, 0, 0, 0, 0, 1)

t_conn = sqlite3.connect('greatoo_jj_3.db')
t_c = t_conn.cursor()

if fill_mission[0] == 1:
    t_c.execute('DELETE FROM status')
    t_conn.commit()

    c.execute('SELECT * FROM JJPart.PartStatus')
    rs = c.fetchall()
    for r in rs:
        t_c.execute('INSERT INTO status VALUES ({0}, \'{1}\')'.format(r[0], r[1]))
    t_conn.commit()

if fill_mission[1] == 1:
    t_c.execute('DELETE FROM part')
    c.execute('SELECT PartID, StatusType, Description1, Description4, Description2, Comment FROM JJPart.Part')
    rs = c.fetchall()
    for r in rs:
        if r[2] == '':
            continue
        if r[4] is not None and len(r[4]) > 0:
            des = '\'{0}\''.format(str(r[4]).strip())
        else:
            des = 'NULL'
        if r[5] is not None and len(r[5]) > 0:
            cmt = '\'{0}\''.format(str(r[5]).strip())
        else:
            cmt = 'NULL'
        sql = 'INSERT INTO part VALUES ({0}, {1}, \'{2}\', \'{3}\', {4}, {5})'.format(r[0], r[1], r[2], r[3], des, cmt)
        try:
            print(sql)
            t_c.execute(sql)
        except Error:
            des = '\'{0}\''.format(des.replace('\'', ''))
            english_name = str(r[3]).replace('\'', '')
            sql = 'INSERT INTO part VALUES ({0}, {1}, \'{2}\', \'{3}\', {4}, {5})'.format(
                r[0], r[1], r[2], english_name, des, cmt )
            t_c.execute(sql)
    c.execute('SELECT Comment, PartID FROM JJPart.Part WHERE Comment IS NOT NULL')
    rs = c.fetchall()
    for r in rs:
        print(r)
        t_c.execute('UPDATE part SET comment=\'{0}\' WHERE id={1}'.format(r[0], r[1]))

if fill_mission[2] == 1:
    t_c.execute('DELETE FROM part_2_file')
    c.execute('SELECT PartID, FilePath FROM JJPart.FileRelation')
    rs = c.fetchall()
    for r in rs:
        sql = 'INSERT INTO part_2_file VALUES ({0}, \'{1}\')'.format(r[0], r[1])
        t_c.execute(sql)

if fill_mission[3] == 1:
    t_c.execute('DELETE FROM part_relation')
    c.execute('SELECT PartRelationID, ChildPart, ParentPart, Quantity, ActualQty, '
              'Number, Comment FROM JJPart.PartRelation')
    rs = c.fetchall()
    for r in rs:
        if r[4] is None:
            rr = r[3]
        else:
            rr = r[4]
        if r[6] is None or len(str(r[6]).strip()) < 1:
            cmt = 'NULL'
        else:
            cmt = '\'{0}\''.format(str(r[6]).strip())
        sql = 'INSERT INTO part_relation VALUES ({0}, {1}, {2}, {3:.3f}, {4:.3f}, {5}, {6})'.format(
            r[0], r[1], r[2], float(r[3]), float(rr), r[5], cmt
        )
        t_c.execute(sql)

if fill_mission[4] == 1:
    t_c.execute( 'DELETE FROM tag' )
    t_c.execute('DELETE FROM part_tag')
    t_c.execute('INSERT INTO tag VALUES (0, \'剪切板\', NULL, 1)')
    index = 1
    t_c.execute('INSERT INTO tag VALUES ({0}, \'类别\', NULL, 1)'.format(index))
    classic_list_index = index
    classic_list = '钣金件 紧固件 电气工程 机械系统-零件 机械系统-装配件 流体系统 ' \
                   '图纸 文档 物料清单 工具 其它 虚拟单元 电气工程-装配件'.split(' ')
    index += 1
    t_index = 1
    for cc in classic_list:
        t_c.execute('INSERT INTO tag VALUES ({0}, \'{1}\', {2}, {3})'.format(index, cc, classic_list_index, t_index))
        t_index += 1
        c.execute('SELECT PartID FROM JJPart.Part WHERE PartType={0} AND StatusType>80'.format(index-1))
        rrs = c.fetchall()
        for rr in rrs:
            t_c.execute('INSERT INTO part_tag VALUES ({0}, {1})'.format(rr[0], index))
        index += 1
    standard_index = index
    t_c.execute('INSERT INTO tag VALUES ({0}, \'标准\', NULL, 1)'.format(standard_index))
    index += 1
    brand_index = index
    t_c.execute( 'INSERT INTO tag VALUES ({0}, \'品牌\', NULL, 1)'.format( brand_index ) )
    index += 1
    c.execute( 'SELECT DISTINCT(Description3) FROM JJPart.Part WHERE StatusType>80 ORDER BY Description3' )
    rs = c.fetchall()
    t_index = 1
    tt_index = 1
    for r in rs:
        print(r)
        if r[0] is None:
            continue
        if str(r[0]).startswith('GB') or str(r[0]).startswith('DIN'):
            t_c.execute( 'INSERT INTO tag VALUES ({0}, \'{1}\', {2}, {3})'.format( index, r[0], standard_index, t_index ) )
            t_index += 1
        else:
            t_c.execute(
                'INSERT INTO tag VALUES ({0}, \'{1}\', {2}, {3})'.format( index, r[0], brand_index, tt_index ) )
            tt_index += 1
        c.execute('SELECT PartID FROM JJPart.Part WHERE Description3=\'{0}\''.format(r[0]))
        rrs = c.fetchall()
        for rr in rrs:
            t_c.execute('INSERT INTO part_tag VALUES ({0}, {1})'.format(rr[0], index))
        index += 1
    t_c.execute('INSERT INTO tag VALUES ({0}, \'巨轮智能ERP物料编码\', NULL, 1)'.format(index))
    erp_num_index = index
    index += 1
    c.execute( 'SELECT DISTINCT(Description6) FROM JJPart.Part WHERE StatusType>80 ORDER BY Description6' )
    rs = c.fetchall()
    t_index = 1
    for r in rs:
        print(r)
        if r[0] is None:
            continue
        t_c.execute('INSERT INTO tag VALUES ({0}, \'{1}\', {2}, {3})'.format(index, r[0], erp_num_index, t_index))
        t_index += 1
        c.execute( 'SELECT PartID FROM JJPart.Part WHERE Description6=\'{0}\''.format( r[0] ) )
        rrs = c.fetchall()
        for rr in rrs:
            t_c.execute( 'INSERT INTO part_tag VALUES ({0}, {1})'.format( rr[0], index ) )
        index += 1
    t_c.execute( 'INSERT INTO tag VALUES ({0}, \'外部编码\', NULL, 1)'.format( index ) )
    foreign_code_index = index
    index += 1
    c.execute( 'SELECT DISTINCT(Description5) FROM JJPart.Part WHERE StatusType>80 ORDER BY Description5' )
    rs = c.fetchall()
    t_index = 1
    for r in rs:
        print( r )
        if r[0] is None or r[0] == '':
            continue
        t_c.execute('INSERT INTO tag VALUES ({0}, \'{1}\', {2}, {3})'.format(index, r[0], foreign_code_index, t_index))
        t_index +=1
        c.execute( 'SELECT PartID FROM JJPart.Part WHERE Description5=\'{0}\''.format( r[0] ) )
        rrs = c.fetchall()
        for rr in rrs:
            t_c.execute( 'INSERT INTO part_tag VALUES ({0}, {1})'.format( rr[0], index ) )
        index += 1

if fill_mission[5] == 1:
    t_c.execute('DELETE FROM part_thumbnail')
    c.execute('SELECT * FROM JJPart.PartThumbnail')
    rs = c.fetchall()
    index = 1
    for r in rs:
        try:
            # if index > 500:
            #     break
            t_c.execute('INSERT INTO part_thumbnail VALUES ({0}, {1}, ?)'.format(r[0], r[2]), (r[1],))
        except Error as ex:
            print('Error:')
            print(ex)
        finally:
            index += 1

if 1 in fill_mission:
    t_conn.commit()

c.close()
conn.close()
t_c.close()
t_conn.close()
