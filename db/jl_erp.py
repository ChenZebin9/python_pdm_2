# coding=gbk
import pyodbc


class JL_ERP_Database:
    unit_list = (
        "付", "套", "件", "个", "片", "块", "台", "条", "支", "粒", "公斤", "米",
        "升", "吨", "盒", "袋", "根", "桶", "张", "只", "瓶", "箱", "双", "卷",
        "包", "把", "立方米", "平方厘米", "组", "圈", "平方米", "对", "立方厘米", "斤",
        "本", "筒", "克", "批", "磅", "节")

    def __init__(self):
        self.__conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=191.1.0.4;UID=ops_dev;PWD=123@greatoo;DATABASE=JL_Mould')
        self.__c = self.__conn.cursor()

    def get_erp_data(self, erp_code):
        sql = f'SELECT [ITEM_NO], [item_describe], [UNIT] FROM [dbo].[ops_v_item] WHERE [ITEM_NO]=\'{erp_code}\''
        self.__c.execute(sql)
        the_item = self.__c.fetchone()
        if the_item is None:
            return erp_code, '', ''
        unit_code = int(the_item[2].lstrip('0'))
        return the_item[0], the_item[1], JL_ERP_Database.unit_list[unit_code - 1]

    def close(self):
        self.__conn.close()

    def search_thr_erp_id(self, id_str: str):
        sql = f'SELECT [ITEM_NO], [item_describe], [UNIT] FROM [dbo].[ops_v_item] ' \
              f'WHERE [ITEM_NO] LIKE \'{id_str}%\' ORDER BY [ITEM_NO]'
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        if r_s is None or len(r_s) < 1:
            return None
        result = []
        for r in r_s:
            unit_str = r[2].lstrip('0')
            u = JL_ERP_Database.unit_list[int(unit_str) - 1] if len(unit_str) > 0 else ''
            # print(r)
            result.append((r[0], r[1], u))
        return result

    def search_thr_erp_description(self, des_str: str):
        search_str = des_str.replace('*', '%')
        search_str = search_str.replace('?', '_')
        sql = f'SELECT [ITEM_NO], [item_describe], [UNIT] FROM [dbo].[ops_v_item] ' \
              f'WHERE [item_describe] LIKE \'{search_str}\' ORDER BY [ITEM_NO]'
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        if r_s is None or len(r_s) < 1:
            return None
        result = []
        for r in r_s:
            unit_str = r[2].lstrip('0')
            u = JL_ERP_Database.unit_list[int(unit_str) - 1] if len(unit_str) > 0 else ''
            result.append((r[0], r[1], u))
        return result


if __name__ == '__main__':
    database = JL_ERP_Database()
    erp_codes = ['01.07.05.0318', '07.04.07.0234']
    for c in erp_codes:
        print(database.get_erp_data(c))
    database.close()
