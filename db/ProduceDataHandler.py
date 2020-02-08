# coding=gbk
""" 用于操作生产管理所涉的数据库 """

import pymssql


class MssqlHandler:

    def __init__(self, server, user, password, database='Greatoo_JJ_Database'):
        self.__conn = pymssql.connect( server=server, user=user, password=password, database=database )
        self.__c = self.__conn.cursor()

    def close(self):
        self.__conn.close()
