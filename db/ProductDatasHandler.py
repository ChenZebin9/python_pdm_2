# coding=gbk
""" 操作 produce_datas.db 中的数据的工具，也分 SQLite 及 MSSQL 两种。 """

import sqlite3


class SqliteHandler:

    def __init__(self, data_file):
        self.__db_file = data_file
        self.__conn = sqlite3.connect( data_file )
        self.__c = self.__conn.cursor()

    def close(self):
        self.__conn.close()

    def get_tags(self, tag_id=None, name=None, parent_id=None):
        if tag_id is None and name is None and parent_id is None:
            # 找出没有父标签的标签
            sql = 'SELECT * FROM tag WHERE parent_id is NULL AND id > 0 ORDER BY id'
        else:
            sql = 'SELECT * FROM tag WHERE'
            factor = False
            if tag_id is not None:
                sql = '{1} id={0}'.format( tag_id, sql )
                factor = True
            if name is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} tag_name LIKE \'%{0}%\''.format( name, sql )
                factor = True
            if parent_id is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} parent_id={0}'.format( parent_id, sql )
            sql += ' ORDER BY sort_index, id'
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_products_by_id(self, product_id):
        self.__c.execute( 'SELECT * FROM Product_Product WHERE productId=\'{0}\''.format( product_id ) )
        return self.__c.fetchall()

    def get_products(self, product_id=None, product_comment=None, status_comment=None, config=None, top=False):
        if product_id is None and product_comment is None and status_comment is None and config is None:
            sql = 'SELECT * FROM Product_Product '
            if top:
                sql += 'WHERE parentProduct IS NULL '
            sql += 'ORDER BY productId'
        elif product_id is not None:
            sql = 'SELECT * FROM Product_Product WHERE productId LIKE \'%{0}%\''.format( product_id )
        else:
            search_filter = ''
            if product_comment is not None:
                search_filter += 'productComment LIKE \'%{0}%\''.format( product_comment )
            if status_comment is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'statusComment LIKE \'%{0}%\''.format( status_comment )
            if config is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'config LIKE \'%{0}%\''.format( config )
            if top:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'parentProduct IS NULL'
            sql = 'SELECT * FROM Product_Product WHERE {0} ORDER BY productId'.format( search_filter )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_children(self, product_id):
        sql = 'SELECT * FROM Product_Product WHERE parentProduct=\'{0}\' ORDER BY productId'.format( product_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_parent(self, product_id):
        sql = 'SELECT parentProduct FROM Product_Product WHERE productId=\'{0}\''.format( product_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if rs[0][0] is None:
            return None
        else:
            pps = self.get_products_by_id( rs[0][0] )
            if len( pps ) < 1:
                return None
            return pps

    def get_tags_2_product(self, product_id):
        sql = 'SELECT t.id, t.tag_name, t.parent_id, t.sort_index ' \
              'FROM Tag AS t INNER JOIN Product_Tag AS p ON t.id=p.tag_id ' \
              'WHERE p.product_id=\'{0}\''.format( product_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_products_2_tag(self, tag_id):
        sql = 'SELECT p.* FROM Product_Product AS p INNER JOIN Product_tag AS t ON ' \
              'p.productId=t.product_id WHERE t.tag_id={0} ORDER BY productId'.format( tag_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_parts_2_tag(self, tag_id):
        return self.get_products_2_tag( tag_id )

    def get_types(self):
        sql = 'SELECT typeShortName FROM Product_Type ORDER BY typeShortName'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    @staticmethod
    def get_cost_types():
        return '配件', '工具', '低耗', '未确定'

    def get_status(self):
        sql = 'SELECT statusName FROM Product_Status ORDER BY statusOrder'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    def tag_product(self, product_id, tag_name, tag_value):
        tag_name_id = self.get_tags( name=tag_name )[0][0]
        tag_value_id = self.get_tags( name=tag_value, parent_id=tag_name_id )[0][0]
        sql = 'INSERT INTO Product_Tag VALUES (\'{0}\', {1})'.format( product_id, tag_value_id )
        self.__c.execute( sql )

    def insert_product_record(self, data, tag=None):
        sql = 'INSERT INTO Product_Product (productId, productType, actualStatus, costType, productComment, ' \
              'statusComment, config, parentProduct) VALUES ({0})'.format( ', '.join( data ) )
        self.__c.execute( sql )
        product_id = data[0][1:-1]
        if tag is not None:
            for t in tag.keys():
                self.tag_product( product_id, t, tag[t] )
        self.__conn.commit()

    def delete_product(self, product_id):
        self.__c.execute( 'SELECT * FROM Product_Product WHERE parentProduct=\'{0}\''.format( product_id ) )
        rs = self.__c.fetchall()
        if len( rs ) > 0:
            raise Exception( '该产品包含了子产品，暂时无法进行删除。' )
        self.__c.execute( 'DELETE FROM Service_Record WHERE productId=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM Sale_ProductShipped WHERE product=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM Sale_ProductSale WHERE product=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM Product_Tag WHERE product_id=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM Product_ID4Customer WHERE assemblyId=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM Product_Product WHERE productId=\'{0}\''.format( product_id ) )
        self.__conn.commit()

    def update_prduct(self, data_s):
        sql = 'UPDATE Product_Product SET productType={1}, actualStatus={2}, costType={3}, productComment={4}, ' \
              'statusComment={5}, config={6}, parentProduct={7} WHERE productId={0}'. \
            format( data_s[0], data_s[1], data_s[2], data_s[3], data_s[4], data_s[5], data_s[6], data_s[7] )
        self.__c.execute( sql )
        self.__conn.commit()

    def replace_product(self, original_id, target_id):
        if original_id == target_id:
            raise Exception( '目标编号与原编号相同。' )
        rs = self.get_products_by_id( target_id )
        if len( rs ) < 1:
            raise Exception( '目标编号不存在对应的产品。' )
        self.__c.execute(
            'UPDATE Service_Record SET productId=\'{0}\' WHERE productId=\'{1}\''.format( target_id, original_id ) )
        self.__c.execute(
            'UPDATE Sale_ProductShipped SET product=\'{0}\' WHERE product=\'{1}\''.format( target_id, original_id ) )
        self.__c.execute(
            'UPDATE Sale_ProductSale SET product=\'{0}\' WHERE product=\'{1}\''.format( target_id, original_id ) )
        rs = self.__c.execute( 'SELECT * FROM Product_Tag WHERE product_id=\'{0}\''.format( original_id ) )
        for r in rs:
            self.__c.execute(
                'SELECT * FROM Product_Tag WHERE product_id=\'{0}\' AND tag_id={1}'.format( target_id, r[1] ) )
            t_rs = self.__c.fetchall()
            if len( t_rs ) > 0:
                continue
            self.__c.execute( 'INSERT INTO Product_Tag VALUES (\'{0}\', {1})'.format( r[0], r[1] ) )
        self.__c.execute(
            'UPDATE Product_ID4Customer SET assemblyId=\'{0}\' WHERE assemblyId=\'{1}\''.format( target_id,
                                                                                                 original_id ) )
        self.__c.execute(
            'UPDATE Product_Product SET parentProduct=\'{0}\' WHERE parentProduct=\'{1}\''.format( target_id,
                                                                                                   original_id ) )
        self.__conn.commit()

    def get_other_product_info(self, product_id):
        info_headers = ('OPS-Ingersoll密码狗', 'Andron密码狗', 'CNC序列号', '电源柜序列号', 'C轴序列号', '配置代号', '出厂编号')
        rs = self.get_products_by_id( product_id=product_id )
        if len( rs ) < 1:
            return None
        r = rs[0]
        index = 1
        result = {}
        # 获取 OPS-Ingersoll 密码狗的颜色
        the_key = '{0}. {1}'.format( index, info_headers[index - 1] )
        if r[10] is not None:
            self.__c.execute( 'SELECT tagColor FROM Product_OiDongle WHERE dongleId={0}'.format( r[10] ) )
            ss = self.__c.fetchone()
            result[the_key] = ss[0]
        else:
            result[the_key] = ''
        index += 1
        for i in range( 2, 7 ):
            the_key = '{0}. {1}'.format( i, info_headers[i - 1] )
            if r[9 + i] is not None:
                result[the_key] = r[9 + i]
            else:
                result[the_key] = ''
            index += 1
        the_key = '{0}. {1}'.format( index, info_headers[index - 1] )
        self.__c.execute( 'SELECT deliveryId FROM Product_ID4Customer WHERE assemblyId=\'{0}\''.format( product_id ) )
        ss = self.__c.fetchall()
        if len( ss ) > 0:
            result[the_key] = ss[0][0]
        else:
            result[the_key] = ''
        index += 1
        return result

    def update_product_other_info(self, product_id, info_index, info_value):
        pre_sql = 'UPDATE Product_Product SET '
        post_sql = 'WHERE productId = \'{0}\''.format( product_id )
        sql = None
        if info_index == 1:
            if info_value.isspace():
                sql = 'oiDongle=NULL '
            else:
                self.__c.execute( 'SELECT dongleId FROM Product_OiDongle WHERE tagColor=\'{0}\''.format( info_value ) )
                rs = self.__c.fetchall()
                if len( rs ) != 1:
                    raise Exception( '所输入的密码狗标签颜色有异常！' )
                dongle_id = rs[0][0]
                sql = 'oiDongle={0} '.format( dongle_id )
        elif info_index == 2:
            if info_value.isspace():
                sql = 'andronDongle=NULL '
            else:
                sql = 'andronDongle=\'{0}\' '.format( info_value )
        elif info_index == 3:
            if info_value.isspace():
                sql = 'cncSer=NULL '
            else:
                sql = 'cncSer=\'{0}\' '.format( info_value )
        elif info_index == 4:
            if info_value.isspace():
                sql = 'cabinetSer=NULL '
            else:
                sql = 'cabinetSer=\'{0}\' '.format( info_value )
        elif info_index == 5:
            if info_value.isspace():
                sql = 'cAxisSer=NULL '
            else:
                sql = 'cAxisSer=\'{0}\' '.format( info_value )
        elif info_index == 6:
            if info_value.isspace():
                sql = 'optionCode=NULL '
            else:
                sql = 'optionCode=\'{0}\' '.format( info_value )
        elif info_index == 7:
            if info_value.isspace():
                sql = 'DELETE FROM Product_ID4Customer WHERE assemblyId=\'{0}\''.format( product_id )
            else:
                self.__c.execute( 'SELECT * FROM Product_ID4Customer WHERE assemblyId=\'{0}\''.format( product_id ) )
                rs = self.__c.fetchall()
                if len( rs ) < 1:
                    sql = 'INSERT INTO Product_ID4Customer VALUES (\'{0}\', \'{1}\')'.format( product_id, info_value )
                else:
                    sql = 'UPDATE Product_ID4Customer SET deliveryId=\'{1}\' WHERE assemblyId=\'{0}\''.format(
                        product_id, info_value )
        if info_index <= 6:
            sql = pre_sql + sql + post_sql
        self.__c.execute( sql )
        self.__conn.commit()
