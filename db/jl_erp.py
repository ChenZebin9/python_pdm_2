# coding=gbk
import pymssql


class JL_ERP_Database:
    unit_list = (
        "付", "套", "件", "个", "片", "块", "台", "条", "支", "粒", "公斤", "米",
        "升", "吨", "盒", "袋", "根", "桶", "张", "只", "瓶", "箱", "双", "卷",
        "包", "把", "立方米", "平方厘米", "组", "圈", "平方米", "对", "立方厘米", "斤")

    def __init__(self):
        self.__conn = pymssql.connect( server='191.1.0.4', user='ops_dev', password='123@greatoo', database='JL_Mould',
                                       login_timeout=10 )
        self.__c = self.__conn.cursor()

    def get_erp_data(self, erp_code):
        sql = f'SELECT [ITEM_NO], [item_describe], [UNIT] FROM [dbo].[ops_v_item] WHERE [ITEM_NO]=\'{erp_code}\''
        self.__c.execute( sql )
        the_item = self.__c.fetchone()
        if the_item is None:
            return erp_code, '', ''
        unit_code = int( the_item[2].lstrip( '0' ) )
        return the_item[0], the_item[1], JL_ERP_Database.unit_list[unit_code - 1]

    def close(self):
        self.__conn.close()


if __name__ == '__main__':
    database = JL_ERP_Database()
    erp_codes = ['01.07.05.0318', '07.04.07.0234']
    for c in erp_codes:
        print( database.get_erp_data( c ) )
    database.close()
