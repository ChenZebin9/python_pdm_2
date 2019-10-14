import pymssql
import sqlite3
from sqlite3 import Error
from database_creator import DatabaseCreator
import os
import datetime

db_file = 'greatoo_jj_3.db'

user_db_name = input('请输入数据库名称（直接按Enter接受默认名称）：')
print('数据库文件名称为：')
if user_db_name == '':
    print('greatoo_jj_3.db。')
else:
    print(user_db_name)
    db_file = user_db_name


if os.path.exists(db_file):
    os.remove(db_file)
DatabaseCreator(db_file)

conn = pymssql.connect(server='191.1.6.103', user='sa', password='8893945', database='Greatoo_JJ_Database')
c = conn.cursor()

fill_mission = (1, 1, 1, 1, 1, 1)

t_conn = sqlite3.connect(db_file)
t_c = t_conn.cursor()

# status 的数据
if fill_mission[0] == 1:
    t_c.execute('DELETE FROM status')
    t_conn.commit()

    c.execute('SELECT * FROM JJPart.PartStatus')
    rs = c.fetchall()
    for r in rs:
        t_c.execute('INSERT INTO status VALUES ({0}, \'{1}\')'.format(r[0], r[1]))
    t_conn.commit()

# part 的数据
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

# part_2_file 文件链接
if fill_mission[2] == 1:
    t_c.execute('DELETE FROM part_2_file')
    c.execute('SELECT PartID, FilePath FROM JJPart.FileRelation')
    rs = c.fetchall()
    for r in rs:
        sql = 'INSERT INTO part_2_file VALUES ({0}, \'{1}\')'.format(r[0], r[1])
        t_c.execute(sql)

# part 之间的连接，part_relation
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

# tag 的数据
if fill_mission[4] == 1:
    t_c.execute( 'DELETE FROM tag' )
    t_c.execute('DELETE FROM part_tag')
    c.execute('SELECT id, tag_name, parent_id, sort_index FROM JJCom.Tag')
    rs = c.fetchall()
    for r in rs:
        pp_id = r[2]
        if r[2] is None:
            pp_id = 'NULL'
        t_c.execute('INSERT INTO tag VALUES ({0}, \'{1}\', {2}, {3})'.format(r[0], r[1], pp_id, r[3]))
    c.execute('SELECT part_id, tag_id FROM JJCom.PartTag')
    rs = c.fetchall()
    for r in rs:
        t_c.execute('INSERT INTO part_tag VALUES ({0}, {1})'.format(r[0], r[1]))

rsp = input('是否输出缩略图？（Y/N）')
rsp = rsp.upper()
while rsp != 'Y' and rsp != 'N':
    rsp = input( '请重新输入。是否输出缩略图？（Y/N）' )
    rsp = rsp.upper()

# thumbnail 缩略图
if fill_mission[5] == 1 and rsp == 'Y':
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
            
# 此次数据的版本号
now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
t_c.execute('INSERT INTO Version VALUES (\'{0}\')'.format(now_time))

if 1 in fill_mission:
    t_conn.commit()

c.close()
conn.close()
t_c.close()
t_conn.close()

print('创建完成。')
