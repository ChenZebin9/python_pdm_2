# coding=gbk
""" 操作 produce_datas.db 中的数据的工具，也分 SQLite 及 MSSQL 两种。 """

import sqlite3
import pymssql


class SqliteHandler:

    def __init__(self, data_file):
        self.__db_file = data_file
        self.__conn = sqlite3.connect( data_file, check_same_thread=False )
        self.__c = self.__conn.cursor()

    def close(self):
        self.__c.close()
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

    def update_product(self, data_s):
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
        self.__c.execute( f'SELECT propertyName, propertyValue FROM Product_Property '
                          f'WHERE productId=\'{product_id}\' ORDER BY propertyIndex' )
        result = []
        ss = self.__c.fetchall()
        for s in ss:
            result.append( s )
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

    # 在 parent_tag 下面，改变为 current_tag，删除其它的 tag
    def change_product_tag(self, product_id, parent_tag_name, current_tag_name):
        self.__c.execute( f'SELECT * FROM Tag WHERE tag_name=\'{parent_tag_name}\' AND parent_id IS NULL' )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            raise Exception( f'提供的\'{parent_tag_name}\'便签有异常。' )
        parent_tag_id = rs[0][0]
        self.__c.execute( f'SELECT * FROM Tag WHERE tag_name=\'{current_tag_name}\' AND parent_id={parent_tag_id}' )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            raise Exception( f'\'{parent_tag_name}\'标签不包括\'{current_tag_name}\'标签。' )
        current_tag_index = rs[0][0]
        # 查看产品下面有没有此类标签
        sql = f'SELECT p.product_id, t.id FROM Product_Tag AS p INNER JOIN Tag AS t ON t.id=p.tag_id ' \
            f'WHERE t.parent_id={parent_tag_id} AND p.product_id={product_id}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        t_l = []
        for r in rs:
            t_l.append( (r[0], r[1]) )
        need_update = True
        for r in t_l:
            if r[1] == current_tag_index:
                need_update = False
                continue
            self.__c.execute( f'DELETE FROM Product_Tag WHERE product_id={product_id} AND tag_id={r[1]}' )
        if need_update:
            self.__c.execute( f'INSERT INTO Product_Tag VALUES ({product_id}, {current_tag_index})' )
            self.__conn.commit()

    # 获取售后记录
    def get_after_sale_service(self, product_id):
        pass

    # 查看是否售出
    def is_saled(self, product_id):
        self.__c.execute( f'SELECT * FROM Sale_SoldOutDetail WHERE productId=\'{product_id}\'' )
        rs = self.__c.fetchall()
        if len(rs) >= 1:
            return True
        return False


class MssqlHandler:

    def __init__(self, server, user, password, database='Greatoo_JJ_Database'):
        self.__conn = pymssql.connect( server=server, user=user, password=password, database=database )
        self.__c = self.__conn.cursor()

    def close(self):
        self.__conn.close()

    def get_tags(self, tag_id=None, name=None, parent_id=None):
        if tag_id is None and name is None and parent_id is None:
            # 找出没有父标签的标签
            sql = 'SELECT * FROM JJProduce.Tag WHERE ParentId is NULL AND id > 0 ORDER BY id'
        else:
            sql = 'SELECT * FROM JJProduce.Tag WHERE'
            factor = False
            if tag_id is not None:
                sql = '{1} Id={0}'.format( tag_id, sql )
                factor = True
            if name is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} TagName LIKE \'%{0}%\''.format( name, sql )
                factor = True
            if parent_id is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} ParentId={0}'.format( parent_id, sql )
            sql += ' ORDER BY SortIndex, Id'
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_products_by_id(self, product_id):
        self.__c.execute( 'SELECT * FROM JJProduce.Product WHERE ProductId=\'{0}\''.format( product_id ) )
        return self.__c.fetchall()

    def get_products(self, product_id=None, product_comment=None, status_comment=None, config=None, top=False):
        if product_id is None and product_comment is None and status_comment is None and config is None:
            sql = 'SELECT * FROM JJProduce.Product '
            if top:
                sql += 'WHERE ParentProduct IS NULL '
            sql += 'ORDER BY ProductId'
        elif product_id is not None:
            sql = 'SELECT * FROM JJProduce.Product WHERE ProductId LIKE \'%{0}%\''.format( product_id )
        else:
            search_filter = ''
            if product_comment is not None:
                search_filter += 'ProductComment LIKE \'%{0}%\''.format( product_comment )
            if status_comment is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'StatusComment LIKE \'%{0}%\''.format( status_comment )
            if config is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'Config LIKE \'%{0}%\''.format( config )
            if top:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'ParentProduct IS NULL'
            sql = 'SELECT * FROM JJProduce.Product WHERE {0} ORDER BY ProductId'.format( search_filter )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_children(self, product_id):
        sql = 'SELECT * FROM JJProduce.Product WHERE ParentProduct=\'{0}\' ORDER BY ProductId'.format( product_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_parent(self, product_id):
        sql = 'SELECT ParentProduct FROM JJProduce.Product WHERE ProductId=\'{0}\''.format( product_id )
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
        sql = 'SELECT t.Id, t.TagName, t.ParentId, t.SortIndex ' \
              'FROM JJProduce.Tag AS t INNER JOIN JJProduce.ProductTag AS p ON t.Id=p.TagId ' \
              'WHERE p.ProductId=\'{0}\''.format( product_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_products_2_tag(self, tag_id):
        sql = 'SELECT p.* FROM JJProduce.Product AS p INNER JOIN JJProduce.ProductTag AS t ON ' \
              'p.ProductId=t.ProductId WHERE t.TagId={0} ORDER BY ProductId'.format( tag_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_parts_2_tag(self, tag_id):
        return self.get_products_2_tag( tag_id )

    def get_types(self):
        sql = 'SELECT TypeShortName FROM JJProduce.ProductType ORDER BY TypeShortName'
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
        sql = 'SELECT StatusName FROM JJProduce.ProductStatus ORDER BY StatusOrder'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    def tag_product(self, product_id, tag_name, tag_value):
        tag_name_id = self.get_tags( name=tag_name )[0][0]
        tag_value_id = self.get_tags( name=tag_value, parent_id=tag_name_id )[0][0]
        sql = 'INSERT INTO JJProduce.ProductTag VALUES (\'{0}\', {1})'.format( product_id, tag_value_id )
        self.__c.execute( sql )

    def insert_product_record(self, data, tag=None):
        sql = 'INSERT INTO JJProduce.Product (ProductId, ProductType, ActualStatus, CostType, ProductComment, ' \
              'StatusComment, Config, ParentProduct) VALUES ({0})'.format( ', '.join( data ) )
        self.__c.execute( sql )
        product_id = data[0][1:-1]
        if tag is not None:
            for t in tag.keys():
                self.tag_product( product_id, t, tag[t] )
        self.__conn.commit()

    def delete_product(self, product_id):
        self.__c.execute( 'SELECT * FROM JJProduce.Product WHERE ParentProduct=\'{0}\''.format( product_id ) )
        rs = self.__c.fetchall()
        if len( rs ) > 0:
            raise Exception( '该产品包含了子产品，暂时无法进行删除。' )
        self.__c.execute( 'DELETE FROM JJProduce.ServiceRecord WHERE ProductId=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM JJSale.ProductShipped WHERE Product=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM JJSale.ProductSale WHERE Product=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM JJProduce.ProductTag WHERE ProductId=\'{0}\''.format( product_id ) )
        # self.__c.execute( 'DELETE FROM Product_ID4Customer WHERE assemblyId=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM JJProduce.Product WHERE ProductId=\'{0}\''.format( product_id ) )
        self.__conn.commit()

    def update_product(self, data_s):
        sql = 'UPDATE JJProduce.Product SET ProductType={1}, ActualStatus={2}, CostType={3}, ProductComment={4}, ' \
              'StatusComment={5}, Config={6}, ParentProduct={7} WHERE ProductId={0}'. \
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
            'UPDATE JJSale.ServiceRecord SET ProductId=\'{0}\' WHERE ProductId=\'{1}\''.format( target_id, original_id ) )
        self.__c.execute(
            'UPDATE JJSale.ProductShipped SET Product=\'{0}\' WHERE Product=\'{1}\''.format( target_id, original_id ) )
        self.__c.execute(
            'UPDATE JJSale.ProductSale SET Product=\'{0}\' WHERE Product=\'{1}\''.format( target_id, original_id ) )
        rs = self.__c.execute( 'SELECT * FROM JJProduce.ProductTag WHERE ProductId=\'{0}\''.format( original_id ) )
        for r in rs:
            self.__c.execute(
                'SELECT * FROM JJProduce.ProductTag WHERE ProductId=\'{0}\' AND TagId={1}'.format( target_id, r[1] ) )
            t_rs = self.__c.fetchall()
            if len( t_rs ) > 0:
                continue
            self.__c.execute( 'INSERT INTO JJProduce.ProductTag VALUES (\'{0}\', {1})'.format( r[0], r[1] ) )
        # self.__c.execute(
        #     'UPDATE Product_ID4Customer SET assemblyId=\'{0}\' WHERE assemblyId=\'{1}\''.format( target_id,
        #                                                                                          original_id ) )
        self.__c.execute(
            'UPDATE JJProduce.Product SET ParentProduct=\'{0}\' WHERE ParentProduct=\'{1}\''.format( target_id,
                                                                                                   original_id ) )
        self.__conn.commit()

    def get_other_product_info(self, product_id):
        self.__c.execute( f'SELECT PropertyName, PropertyValue FROM JJProduce.ProductProperty '
                          f'WHERE ProductId=\'{product_id}\' ORDER BY PropertyIndex' )
        result = []
        ss = self.__c.fetchall()
        for s in ss:
            result.append( s )
        return result

    # 完全没用了
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

    # 在 parent_tag 下面，改变为 current_tag，删除其它的 tag
    def change_product_tag(self, product_id, parent_tag_name, current_tag_name):
        self.__c.execute( f'SELECT * FROM JJProduce.Tag WHERE TagName=\'{parent_tag_name}\' AND ParentId IS NULL' )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            raise Exception( f'提供的\'{parent_tag_name}\'便签有异常。' )
        parent_tag_id = rs[0][0]
        self.__c.execute( f'SELECT * FROM JJProduce.Tag WHERE TagName=\'{current_tag_name}\' AND ParentId={parent_tag_id}' )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            raise Exception( f'\'{parent_tag_name}\'标签不包括\'{current_tag_name}\'标签。' )
        current_tag_index = rs[0][0]
        # 查看产品下面有没有此类标签
        sql = f'SELECT p.ProductId, t.id FROM JJProduce.ProductTag AS p INNER JOIN JJProduce.Tag AS t ON t.Id=p.TagId ' \
            f'WHERE t.ParentId={parent_tag_id} AND p.ProductId={product_id}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        t_l = []
        for r in rs:
            t_l.append( (r[0], r[1]) )
        need_update = True
        for r in t_l:
            if r[1] == current_tag_index:
                need_update = False
                continue
            self.__c.execute( f'DELETE FROM JJProduce.ProductTag WHERE ProductId={product_id} AND TagId={r[1]}' )
        if need_update:
            self.__c.execute( f'INSERT INTO JJProduce.ProductTag VALUES ({product_id}, {current_tag_index})' )
            self.__conn.commit()

    # 获取售后记录
    def get_after_sale_service(self, product_id):
        pass

    # 查看是否售出
    def is_saled(self, product_id):
        self.__c.execute( f'SELECT * FROM JJSale.SoldOutDetail WHERE ProductId=\'{product_id}\'' )
        rs = self.__c.fetchall()
        if len(rs) >= 1:
            return True
        return False
