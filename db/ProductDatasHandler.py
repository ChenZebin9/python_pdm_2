# coding=gbk
""" 操作产品的相关数据库中的数据的工具，也分 SQLite 及 MSSQL 两种。 """

import sqlite3
import pyodbc
from abc import abstractmethod, ABCMeta


class ProductDatabaseHandler( metaclass=ABCMeta ):

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_tags(self, tag_id=None, name=None, parent_id=None):
        pass

    @abstractmethod
    def get_products_by_id(self, product_id):
        pass

    @abstractmethod
    def get_products(self, product_id=None, product_comment=None, status_comment=None, config=None, top=False):
        pass

    @abstractmethod
    def get_children(self, product_id):
        pass

    @abstractmethod
    def get_parent(self, product_id):
        pass

    @abstractmethod
    def get_tags_2_product(self, product_id):
        pass

    @abstractmethod
    def get_products_2_tag(self, tag_id):
        pass

    @abstractmethod
    def get_parts_2_tag(self, tag_id):
        pass

    @abstractmethod
    def get_types(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def tag_product(self, product_id, tag_name, tag_value):
        pass

    @abstractmethod
    def insert_product_record(self, data, tag=None):
        pass

    @abstractmethod
    def delete_product(self, product_id):
        pass

    @abstractmethod
    def update_product(self, data_s):
        pass

    @abstractmethod
    def replace_product(self, original_id, target_id):
        pass

    @abstractmethod
    def get_other_product_info(self, product_id):
        pass

    @abstractmethod
    def update_product_other_info(self, product_id, property_name, property_value):
        """
        更新产品的已有属性的数值
        :param product_id: 产品编号
        :param property_name: 属性名称
        :param property_value: str, 新的属性数值
        :return:
        """
        pass

    @abstractmethod
    def delete_product_other_info(self, product_id, property_name):
        pass

    @abstractmethod
    def insert_product_other_info(self, product_id, property_name, property_value, previous_index):
        pass

    @abstractmethod
    def get_product_other_info_name(self):
        pass

    # 在 parent_tag 下面，改变为 current_tag，删除其它的 tag
    @abstractmethod
    def change_product_tag(self, product_id, parent_tag_name, current_tag_name):
        pass

    # 查看是否售出
    @abstractmethod
    def is_sold(self, product_id):
        pass

    # 查看销售情况
    @abstractmethod
    def get_sold_customer(self, product_id):
        pass

    @abstractmethod
    def get_products_from_customer(self, short_name):
        """ 根据客户的短名称，获取产品 """
        pass

    # 根据日期预先估计出服务单号
    @abstractmethod
    def pre_get_service_record_id(self, the_date):
        pass

    # 获取雇用的人员
    @abstractmethod
    def get_usable_operators(self):
        pass

    # 添加售后服务记录
    @abstractmethod
    def insert_service_record(self, record_id, product_id, the_date, operator, description):
        pass

    # 获取售后记录
    @abstractmethod
    def get_service_record(self, product_id):
        pass

    @abstractmethod
    def insert_sale_contract(self, data_dict):
        """
        创建销售合同
        :return:
        """
        pass

    # 获取客户的清单
    # 返回：短名称、长名称
    @abstractmethod
    def get_customers(self, the_filter=None):
        pass

    @abstractmethod
    def get_available_ser_nr(self):
        """
        获取出厂编号的列表
        :return:
        """
        pass


class SqliteHandler( ProductDatabaseHandler ):

    def get_product_other_info_name(self):
        pass

    def delete_product_other_info(self, product_id, property_name):
        pass

    def insert_product_other_info(self, product_id, property_name, property_value, previous_index):
        pass

    def insert_sale_contract(self, data_dict):
        """
        创建销售合同
        :return:
        """
        code = data_dict['No']
        when = data_dict['Date']
        customer = data_dict['Customer']
        t_customer = data_dict['Terminal Customer']
        comment = data_dict['Comment']
        status = 1
        products = data_dict['Products']
        code = f'\'{code}\''
        when = f'\'{when}\''
        find_customer_sql = f'SELECT [CompanyCode] FROM [JJSale_Company] WHERE [Name]=\'{customer}\''
        self.__c.execute( find_customer_sql )
        r = self.__c.fetchone()
        customer = f'\'{r[0]}\''
        if len( t_customer ) < 1:
            t_customer = 'NULL'
        else:
            find_customer_sql = f'SELECT [CompanyCode] FROM [JJSale_Company] WHERE [Name]=\'{t_customer}\''
            self.__c.execute( find_customer_sql )
            r = self.__c.fetchone()
            t_customer = f'\'{r[0]}\''
        create_contract = f'INSERT INTO [JJSale_Contract] VALUES ({code}, {when}, {customer}, {t_customer}, {status})'
        self.__c.execute( create_contract )
        if len( comment ) < 1:
            comment = 'NULL'
        else:
            comment = f'\'{comment}\''
        for p in products:
            create_product_sold_sql = f'INSERT INTO [JJSale_ProductSale] VALUES (\'{p}\', {code}, {comment})'
            self.__c.execute( create_product_sold_sql )
        self.__conn.commit()

    def get_available_ser_nr(self):
        the_sql = 'select [PropertyValue] from [JJProduce_ProductProperty] ' \
                  'where [PropertyName]=\'出厂编号\' and [PropertyValue] is not null ' \
                  'order by [PropertyValue]'
        self.__c.execute( the_sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    def __init__(self, data_file):
        self.__db_file = data_file
        self.__conn = sqlite3.connect( data_file, check_same_thread=False )
        self.__c = self.__conn.cursor()

    def close(self):
        try:
            self.__c.close()
            self.__conn.close()
        except Exception as ex:
            print( f'Error when close product database: {str( ex )}' )

    def get_tags(self, tag_id=None, name=None, parent_id=None):
        if tag_id is None and name is None and parent_id is None:
            # 找出没有父标签的标签
            sql = 'SELECT * FROM [JJProduce_Tag] WHERE [ParentId] IS NULL AND [id] > 0 ORDER BY [id]'
        else:
            sql = 'SELECT * FROM [JJProduce_Tag] WHERE'
            factor = False
            if tag_id is not None:
                sql = '{1} Id={0}'.format( tag_id, sql )
                factor = True
            if name is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} [TagName] LIKE \'%{0}%\''.format( name, sql )
                factor = True
            if parent_id is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} [ParentId]={0}'.format( parent_id, sql )
            sql += ' ORDER BY [SortIndex], [Id]'
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_products_by_id(self, product_id):
        self.__c.execute( 'SELECT * FROM [JJProduce_Product] WHERE [ProductId]=\'{0}\''.format( product_id ) )
        return self.__c.fetchall()

    def get_products(self, product_id=None, product_comment=None, status_comment=None, config=None, top=False):
        if product_id is None and product_comment is None and status_comment is None and config is None:
            sql = 'SELECT * FROM [JJProduce_Product] '
            if top:
                sql += 'WHERE [ParentProduct] IS NULL '
            sql += 'ORDER BY [ProductId]'
        elif product_id is not None:
            sql = 'SELECT * FROM [JJProduce_Product] WHERE [ProductId] LIKE \'%{0}%\''.format( product_id )
        else:
            search_filter = ''
            if product_comment is not None:
                search_filter += '[ProductComment] LIKE \'%{0}%\''.format( product_comment )
            if status_comment is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += '[StatusComment] LIKE \'%{0}%\''.format( status_comment )
            if config is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += '[Config] LIKE \'%{0}%\''.format( config )
            if top:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += '[ParentProduct] IS NULL'
            sql = 'SELECT * FROM [JJProduce_Product] WHERE {0} ORDER BY [ProductId]'.format( search_filter )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_children(self, product_id):
        sql = 'SELECT * FROM [JJProduce_Product] WHERE [ParentProduct]=\'{0}\' ORDER BY [ProductId]'.format(
            product_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_parent(self, product_id):
        sql = 'SELECT [ParentProduct] FROM [JJProduce_Product] WHERE [ProductId]=\'{0}\''.format( product_id )
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
        sql = 'SELECT t.[Id], t.[TagName], t.[ParentId], t.[SortIndex] ' \
              'FROM [JJProduce_Tag] AS t INNER JOIN [JJProduce_ProductTag] AS p ON t.[Id]=p.[TagId] ' \
              'WHERE p.[ProductId]=\'{0}\''.format( product_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_products_2_tag(self, tag_id):
        sql = 'SELECT p.* FROM [JJProduce_Product] AS p INNER JOIN [JJProduce_ProductTag] AS t ON ' \
              'p.[ProductId]=t.[ProductId] WHERE t.[TagId]={0} ORDER BY [ProductId]'.format( tag_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_parts_2_tag(self, tag_id):
        return self.get_products_2_tag( tag_id )

    def get_types(self):
        sql = 'SELECT [TypeShortName] FROM [JJProduce_ProductType] ORDER BY [TypeShortName]'
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
        sql = 'SELECT [StatusName] FROM [JJProduce_ProductStatus] ORDER BY [StatusOrder]'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    def tag_product(self, product_id, tag_name, tag_value):
        tag_name_id = self.get_tags( name=tag_name )[0][0]
        tag_value_id = self.get_tags( name=tag_value, parent_id=tag_name_id )[0][0]
        sql = 'INSERT INTO [JJProduce_ProductTag] VALUES (\'{0}\', {1})'.format( product_id, tag_value_id )
        self.__c.execute( sql )

    def insert_product_record(self, data, tag=None):
        sql = 'INSERT INTO [JJProduce_Product] ([ProductId], [ProductType], [ActualStatus], [CostType], ' \
              '[ProductComment], [StatusComment], [Config], [ParentProduct]) VALUES ({0})'.format( ', '.join( data ) )
        self.__c.execute( sql )
        product_id = data[0][1:-1]
        if tag is not None:
            for t in tag.keys():
                self.tag_product( product_id, t, tag[t] )
        self.__conn.commit()

    def delete_product(self, product_id):
        self.__c.execute( 'SELECT * FROM [JJProduce_Product] WHERE [ParentProduct]=\'{0}\''.format( product_id ) )
        rs = self.__c.fetchall()
        if len( rs ) > 0:
            raise Exception( '该产品包含了子产品，暂时无法进行删除。' )
        self.__c.execute( 'DELETE FROM [JJSale_ServiceRecord] WHERE [ProductId]=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM [JJSale_ProductShipped] WHERE [Product]=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM [JJSale_ProductSale] WHERE [Product]=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM [JJProduce_ProductTag] WHERE [ProductId]=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM [JJProduce_Product] WHERE [ProductId]=\'{0}\''.format( product_id ) )
        self.__conn.commit()

    def update_product(self, data_s):
        sql = 'UPDATE [JJProduce_Product] SET [ProductType]={1}, [ActualStatus]={2}, [CostType]={3}, ' \
              '[ProductComment]={4}, [StatusComment]={5}, [Config]={6}, [ParentProduct]={7} WHERE [ProductId]={0}'. \
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
            'UPDATE [JJSale_ServiceRecord] SET [ProductId]=\'{0}\' WHERE [ProductId]=\'{1}\''.format( target_id,
                                                                                                      original_id ) )
        self.__c.execute(
            'UPDATE [JJSale_ProductShipped] SET [Product]=\'{0}\' WHERE [Product]=\'{1}\''.format( target_id,
                                                                                                   original_id ) )
        self.__c.execute(
            'UPDATE [JJSale_ProductSale] SET [Product]=\'{0}\' WHERE [Product]=\'{1}\''.format( target_id,
                                                                                                original_id ) )
        rs = self.__c.execute( 'SELECT * FROM [JJProduce_ProductTag] WHERE [ProductId]=\'{0}\''.format( original_id ) )
        for r in rs:
            self.__c.execute(
                'SELECT * FROM [JJProduce_ProductTag] WHERE [ProductId]=\'{0}\' AND [TagId]={1}'.format( target_id,
                                                                                                         r[1] ) )
            t_rs = self.__c.fetchall()
            if len( t_rs ) > 0:
                continue
            self.__c.execute( 'INSERT INTO [JJProduce_ProductTag] VALUES (\'{0}\', {1})'.format( r[0], r[1] ) )
        self.__c.execute(
            'UPDATE [JJProduce_Product] SET [ParentProduct]=\'{0}\' '
            'WHERE [ParentProduct]=\'{1}\''.format( target_id, original_id ) )

    def get_other_product_info(self, product_id):
        self.__c.execute( f'SELECT [PropertyName], [PropertyValue] FROM [JJProduce_ProductProperty] '
                          f'WHERE [ProductId]=\'{product_id}\' ORDER BY [PropertyIndex]' )
        result = []
        ss = self.__c.fetchall()
        for s in ss:
            result.append( s )
        return result

    def update_product_other_info(self, product_id, property_name, property_value):
        sql = f'UPDATE [JJProduce_ProductProperty] SET [PropertyValue]=\'{property_value}\' ' \
              f'WHERE [ProductId]=\'{product_id}\' AND [PropertyName]=\'{property_name}\''
        self.__c.execute( sql )
        self.__conn.commit()

    # 在 parent_tag 下面，改变为 current_tag，删除其它的 tag
    def change_product_tag(self, product_id, parent_tag_name, current_tag_name):
        # TEXT变量要进行转换，不能直接用=(equal to)
        sql = f'SELECT * FROM [JJProduce_Tag] WHERE [TagName]=\'{parent_tag_name}\' AND [ParentId] IS NULL'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            raise Exception( f'提供的\'{parent_tag_name}\'便签有异常。' )
        parent_tag_id = rs[0][0]
        sql = f'SELECT * FROM [JJProduce_Tag] ' \
              f'WHERE [TagName]=\'{current_tag_name}\' AND [ParentId]={parent_tag_id}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            raise Exception( f'{parent_tag_name}标签不包括{current_tag_name}标签。' )
        current_tag_index = rs[0][0]
        # 查看产品下面有没有此类标签
        sql = f'SELECT p.[ProductId], t.[id] FROM [JJProduce_ProductTag] AS p INNER JOIN [JJProduce_Tag] AS t ' \
              f'ON t.[Id]=p.[TagId] WHERE t.[ParentId]={parent_tag_id} AND p.[ProductId]={product_id}'
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
            self.__c.execute( f'DELETE FROM [JJProduce_ProductTag] WHERE [ProductId]={product_id} AND [TagId]={r[1]}' )
        if need_update:
            self.__c.execute( f'INSERT INTO [JJProduce_ProductTag] VALUES ({product_id}, {current_tag_index})' )
            self.__conn.commit()

    # 查看是否售出
    def is_sold(self, product_id):
        self.__c.execute( f'SELECT * FROM [JJSale_SoldOutDetail] WHERE [ProductId]=\'{product_id}\'' )
        rs = self.__c.fetchall()
        if len( rs ) >= 1:
            return True
        return False

    def pre_get_service_record_id(self, the_date):
        """根据日期预先估计出服务单号"""
        format_date = 'AS{0}'.format( the_date )
        self.__c.execute( f'SELECT [ServiceId] FROM [JJSale_ServiceRecord] '
                          f'WHERE [ServiceId] LIKE \'{format_date}%\' ORDER BY [ServiceId] DESC' )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return f'AS{the_date}-1'
        f = rs[0][0]
        n = f[-1:]
        i = int( n ) + 1
        return f'AS{the_date}-{i}'

    def get_sold_customer(self, product_id):
        """根据产品编号，查看销售情况"""
        sql = f'SELECT [ContractCompany], [TerminalCompany] FROM [JJSale_SoldOutDetail] ' \
              f'WHERE [ProductId]=\'{product_id}\''
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        return rs

    def get_products_from_customer(self, short_name):
        """ 根据客户的短名称，获取产品 """
        sql = f'SELECT [ProductId] FROM [JJSale_SoldOutDetail] ' \
              f'WHERE [ContractCompany]=\'{short_name}\' OR [TerminalCompany]=\'{short_name}\''
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        r_rs = []
        for r in rs:
            t_r = self.get_products_by_id( r[0] )[0]
            r_rs.append( (t_r[0], t_r[2], t_r[7], t_r[8], t_r[9]) )
        return r_rs

    def get_usable_operators(self):
        """获取雇用的人员"""
        self.__c.execute( f'SELECT [Name], [PersonCode] FROM [JJCom_HR] WHERE [Status]=0' )
        rs = self.__c.fetchall()
        return rs

    def insert_service_record(self, record_id, product_id, the_date, operator, description):
        """添加售后服务记录"""
        the_sql = f'INSERT INTO [JJSale_ServiceRecord] VALUES (\'{record_id}\', \'{product_id}\', ' \
                  f'\'{the_date}\', \'{operator}\', \'{description}\')'
        self.__c.execute( the_sql )
        self.__conn.commit()

    def get_service_record(self, product_id):
        """获取售后记录"""
        the_sql = f'SELECT [ServiceId], [Description] FROM [JJSale_ServiceRecord] WHERE [ProductId]=\'{product_id}\''
        self.__c.execute( the_sql )
        rs = self.__c.fetchall()
        return rs

    def get_customers(self, the_filter=None):
        """
        # 获取客户的清单
        # 返回：短名称、长名称
        """
        the_sql = 'SELECT * FROM [JJSale_Company]'
        if the_filter is not None:
            the_sql += f' WHERE [Name] LIKE \'%{the_filter}%\''
        the_sql += ' ORDER BY [Name]'
        self.__c.execute( the_sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( (r[2], r[1]) )
        return result


class MssqlHandler( ProductDatabaseHandler ):

    def get_product_other_info_name(self):
        sql = 'SELECT DISTINCT([PropertyName]) FROM [JJProduce].[ProductProperty]'
        self.__c.execute( sql )
        r_s = self.__c.fetchall()
        result = []
        for r in r_s:
            result.append( r[0] )
        return result

    def delete_product_other_info(self, product_id, property_name):
        sql = f'DELETE FROM [JJProduce].[ProductProperty] ' \
              f'WHERE [ProductId]=\'{product_id}\' AND [PropertyName]=\'{property_name}\''
        self.__c.execute( sql )
        self.__conn.commit()

    def insert_product_other_info(self, product_id, property_name, property_value, previous_index):
        sql = f'SELECT [PropertyIndex] FROM [JJProduce].[ProductProperty] ' \
              f'WHERE [ProductId]=\'{product_id}\' ORDER BY [PropertyIndex]'
        self.__c.execute( sql )
        r_s = self.__c.fetchall()
        c = len( r_s )
        do_inc = True
        if c > 0:
            if previous_index == 0:
                next_index = r_s[0][0]
            elif previous_index > c - 1 or previous_index < 0:
                next_index = r_s[-1][0] + 1
                do_inc = False
            else:
                next_index = r_s[previous_index][0]
        else:
            next_index = 1
            do_inc = False
        if do_inc:
            sql = f'UPDATE [JJProduce].[ProductProperty] SET [PropertyIndex]=[PropertyIndex]+1 ' \
                  f'WHERE [PropertyIndex]>={next_index} AND [ProductId]=\'{product_id}\''
            self.__c.execute( sql )
        sql = f'INSERT INTO [JJProduce].[ProductProperty] VALUES ' \
              f'(\'{product_id}\',\'{property_name}\',\'{property_value}\',{next_index})'
        self.__c.execute( sql )
        self.__conn.commit()

    def __init__(self, server, database, user, password):
        self.__conn = pyodbc.connect('DRIVER={{SQL Server}};SERVER={0};DATABASE={1};UID={2};PWD={3}'.
                                     format(server, database, user, password))
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
        self.__c.execute( 'DELETE FROM JJSale.ServiceRecord WHERE ProductId=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM JJSale.ProductShipped WHERE Product=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM JJSale.ProductSale WHERE Product=\'{0}\''.format( product_id ) )
        self.__c.execute( 'DELETE FROM JJProduce.ProductTag WHERE ProductId=\'{0}\''.format( product_id ) )
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
            'UPDATE JJSale.ServiceRecord SET ProductId=\'{0}\' WHERE ProductId=\'{1}\''.format( target_id,
                                                                                                original_id ) )
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

    def update_product_other_info(self, product_id, property_name, property_value):
        """
        更新产品的已有属性的数值
        :param product_id: 产品编号
        :param property_name: 属性名称
        :param property_value: str, 新的属性数值
        :return:
        """
        sql = f'UPDATE [JJProduce].[ProductProperty] SET [PropertyValue]=\'{property_value}\' ' \
              f'WHERE [ProductId]=\'{product_id}\' AND [PropertyName]=\'{property_name}\''
        self.__c.execute( sql )
        self.__conn.commit()

    # 在 parent_tag 下面，改变为 current_tag，删除其它的 tag
    def change_product_tag(self, product_id, parent_tag_name, current_tag_name):
        # TEXT变量要进行转换，不能直接用=(equal to)
        sql = f'SELECT * FROM JJProduce.Tag WHERE CONVERT(VARCHAR, TagName)=\'{parent_tag_name}\' AND ParentId IS NULL'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            raise Exception( f'提供的\'{parent_tag_name}\'便签有异常。' )
        parent_tag_id = rs[0][0]
        sql = f'SELECT * FROM JJProduce.Tag ' \
              f'WHERE CONVERT(VARCHAR, TagName)=\'{current_tag_name}\' AND ParentId={parent_tag_id}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            raise Exception( f'{parent_tag_name}标签不包括{current_tag_name}标签。' )
        current_tag_index = rs[0][0]
        # 查看产品下面有没有此类标签
        sql = f'SELECT p.ProductId, t.id FROM JJProduce.ProductTag AS p INNER JOIN JJProduce.Tag AS t ' \
              f'ON t.Id=p.TagId WHERE t.ParentId={parent_tag_id} AND p.ProductId={product_id}'
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

    # 查看是否售出
    def is_sold(self, product_id):
        self.__c.execute( f'SELECT * FROM JJSale.SoldOutDetail WHERE ProductId=\'{product_id}\'' )
        rs = self.__c.fetchall()
        if len( rs ) >= 1:
            return True
        return False

    # 查看销售情况
    def get_sold_customer(self, product_id):
        sql = f'SELECT ContractCompany, TerminalCompany FROM JJSale.SoldOutDetail WHERE ProductId=\'{product_id}\''
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        return rs

    def get_products_from_customer(self, short_name):
        """ 根据客户的短名称，获取产品 """
        sql = f'SELECT ProductId FROM JJSale.SoldOutDetail ' \
              f'WHERE ContractCompany=\'{short_name}\' OR TerminalCompany=\'{short_name}\''
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        r_rs = []
        for r in rs:
            t_r = self.get_products_by_id( r[0] )[0]
            r_rs.append( (t_r[0], t_r[2], t_r[7], t_r[8], t_r[9]) )
        return r_rs

    # 根据日期预先估计出服务单号
    def pre_get_service_record_id(self, the_date):
        format_date = 'AS{0}'.format( the_date )
        self.__c.execute( f'SELECT ServiceId FROM JJSale.ServiceRecord '
                          f'WHERE ServiceId LIKE \'{format_date}%\' ORDER BY ServiceId DESC' )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return f'AS{the_date}-1'
        f = rs[0][0]
        n = f[-1:]
        i = int( n ) + 1
        return f'AS{the_date}-{i}'

    # 获取雇用的人员
    def get_usable_operators(self):
        self.__c.execute( f'SELECT Name, PersonCode FROM JJCom.HR WHERE Status=0' )
        rs = self.__c.fetchall()
        return rs

    # 添加售后服务记录
    def insert_service_record(self, record_id, product_id, the_date, operator, description):
        the_sql = f'INSERT INTO JJSale.ServiceRecord VALUES (\'{record_id}\', \'{product_id}\', ' \
                  f'\'{the_date}\', \'{operator}\', \'{description}\')'
        self.__c.execute( the_sql )
        self.__conn.commit()

    # 获取售后记录
    def get_service_record(self, product_id):
        the_sql = f'SELECT ServiceId, Description FROM JJSale.ServiceRecord WHERE ProductId=\'{product_id}\''
        self.__c.execute( the_sql )
        rs = self.__c.fetchall()
        return rs

    def insert_sale_contract(self, data_dict):
        """
        创建销售合同
        :return:
        """
        code = data_dict['No']
        when = data_dict['Date']
        customer = data_dict['Customer']
        t_customer = data_dict['Terminal Customer']
        comment = data_dict['Comment']
        status = 1
        products = data_dict['Products']
        code = f'\'{code}\''
        when = f'\'{when}\''
        find_customer_sql = f'SELECT [CompanyCode] FROM [JJSale].[Company] WHERE [Name]=\'{customer}\''
        self.__c.execute( find_customer_sql )
        r = self.__c.fetchone()
        customer = f'\'{r[0]}\''
        if len( t_customer ) < 1:
            t_customer = 'NULL'
        else:
            find_customer_sql = f'SELECT [CompanyCode] FROM [JJSale].[Company] WHERE [Name]=\'{t_customer}\''
            self.__c.execute( find_customer_sql )
            r = self.__c.fetchone()
            t_customer = f'\'{r[0]}\''
        create_contract = f'INSERT INTO [JJSale].[Contract] VALUES ({code}, {when}, {customer}, {t_customer}, {status})'
        self.__c.execute( create_contract )
        if len( comment ) < 1:
            comment = 'NULL'
        else:
            comment = f'\'{comment}\''
        for p in products:
            create_product_sold_sql = f'INSERT INTO [JJSale].[ProductSale] VALUES (\'{p}\', {code}, {comment})'
            self.__c.execute( create_product_sold_sql )
        self.__conn.commit()

    # 获取客户的清单
    # 返回：短名称、长名称
    def get_customers(self, the_filter=None):
        the_sql = 'SELECT * FROM JJSale.Company'
        if the_filter is not None:
            the_sql += f' WHERE Name LIKE \'%{the_filter}%\''
        the_sql += ' ORDER BY Name'
        self.__c.execute( the_sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( (r[2], r[1]) )
        return result

    def get_available_ser_nr(self):
        """
        获取出厂编号的列表
        :return:
        """
        the_sql = 'select [PropertyValue] from [JJProduce].[ProductProperty] ' \
                  'where [PropertyName]=\'出厂编号\' and [PropertyValue] is not null ' \
                  'order by convert(varchar(20),[PropertyValue])'
        self.__c.execute( the_sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result
