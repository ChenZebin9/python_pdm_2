from decimal import Decimal

import Com
from db.DatabaseHandler import *
import sqlite3


class SqliteHandler( DatabaseHandler ):

    def set_part_hyper_link(self, part_id, the_link):
        if the_link is None or len( the_link.strip() ) < 1:
            sql = f'DELETE FROM [JJCost_PurchaseLink] WHERE [PartId]={part_id}'
            self.__c.execute( sql )
            return
        sql = f'SELECT [HyperLink] FROM [JJCost_PurchaseLink] WHERE [PartId]={part_id}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            sql = f'INSERT INTO [JJCost_PurchaseLink] VALUES ({part_id}, \'{the_link}\')'
        else:
            sql = f'UPDATE [JJCost_PurchaseLink] SET [HyperLink]=\'{the_link}\' WHERE [PartId]={part_id}'
        self.__c.execute( sql )

    def get_part_hyper_link(self, part_id):
        sql = f'SELECT [HyperLink] FROM [JJCost_PurchaseLink] WHERE [PartId]={part_id}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs[0][0]

    def remove_part_relation(self, relation_id):
        """
        移除原先的关联
        :param relation_id: 关联ID
        :return:
        """
        sql = f'DELETE FROM [JJPart_PartRelation] WHERE [PartRelationID]={relation_id}'
        self.__c.execute( sql )

    def update_part_relation(self, relation_id, index_id, parent_id, child_id, sum_qty, actual_qty, relation_comment):
        """
        更新或新近一个新的零件关联
        :param relation_id: 关联ID，可能为None
        :param index_id: 关联的index，代表在子项目中的排序
        :param parent_id: 父ID
        :param child_id: 子ID
        :param sum_qty: 统计数量
        :param actual_qty: 实际数量
        :param relation_comment: 关联备注
        :return:
        """
        sql = 'SELECT MAX([PartRelationID]) FROM [JJPart_PartRelation]'
        self.__c.execute( sql )
        r = self.__c.fetchone()
        next_relation_id = r[0] + 1
        comment_4_sql = 'null'
        if relation_comment is not None and len( relation_comment ) > 0:
            comment_4_sql = f'\'{relation_comment.strip()}\''
        if relation_id is None:
            sql = f'INSERT INTO [JJPart_PartRelation] VALUES ({next_relation_id}, {parent_id}, {child_id}, {sum_qty},' \
                  f' \'件\', {index_id}, {comment_4_sql}, {actual_qty}, 0)'
            self.__c.execute( sql )
        else:
            sql = f'UPDATE [JJPart_PartRelation] SET [Quantity]={sum_qty}, [Number]={index_id}, [Comment]={comment_4_sql},' \
                  f' [ActualQty]={actual_qty} WHERE [PartRelationID]={relation_id}'
            self.__c.execute( sql )

    def get_pick_material_record(self, begin_date, end_date):
        sql = 'SELECT r.[BillName], i.[ItemId], i.[PartId], i.[ErpId], r.[DoingDate], ' \
              'r.[DoneQty], r.[Comment], r.[Id] AS [RecordId] FROM [JJStorage_SupplyOperationRecord] AS r ' \
              'INNER JOIN [JJStorage_KbnSupplyItem] AS i ON r.[LinkItem]=i.[ItemId] ' \
              'WHERE r.[Process]=14'
        sql += f' AND r.[DoingDate]>=\'{begin_date}\' AND r.[DoingDate]<=\'{end_date}\''
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def create_put_back_material_record(self, bill_name, operator, when, data):
        pass

    def cancel_material_requirement(self, item_id, cancel_qty, change_doing=False):
        sql = f'SELECT [DoneQty], [DoingQty] FROM [JJStorage_KbnSupplyItem] WHERE [ItemId]={item_id}'
        self.__c.execute( sql )
        r = self.__c.fetchone()
        doing_qty = float( r[1] )
        update_doing_qty_str = ''
        if change_doing:
            update_doing_qty_str = f', [DoingQty]={doing_qty - cancel_qty} '
        all_done_qty = float( r[0] ) + cancel_qty
        sql = f'UPDATE [JJStorage_KbnSupplyItem] SET [DoneQty]={all_done_qty}{update_doing_qty_str} ' \
              f'WHERE [ItemId]={item_id}'
        self.__c.execute( sql )
        self.__conn.commit()

    def cancel_supply_operation(self, record_id, cancel_qty):
        sql = f'SELECT [Done], [Qty], [DoneQty], [LinkItem] FROM [JJStorage_SupplyOperationRecord] WHERE [Id]={record_id}'
        self.__c.execute( sql )
        r = self.__c.fetchone()
        qty = float( r[1] )
        done_qty = float( r[2] )
        done_qty += cancel_qty
        done = 1 if done_qty >= qty else 0
        item_id = r[3]
        sql = f'UPDATE [JJStorage_SupplyOperationRecord] SET [Done]={done}, [DoneQty]={done_qty} WHERE [Id]={record_id}'
        self.__c.execute( sql )
        self.cancel_material_requirement( item_id, cancel_qty, change_doing=True )

    def set_part_thumbnail(self, part_id, image_data):
        get_version_sql = f'SELECT [Version] FROM [JJPart_PartThumbnail] ' \
                          f'WHERE [PartId]={part_id} ORDER BY [Version] DESC'
        self.__c.execute( get_version_sql )
        r = self.__c.fetchone()
        next_version = 1
        if r is not None:
            next_version += r[0]
        insert_new_img_sql = 'INSERT INTO [JJPart_PartThumbnail] ([PartID], [Thumbnail], [Version])' \
                             ' VALUES ({0}, {1}, {2})'.format( part_id, str( image_data, encoding='ascii' ),
                                                               next_version )
        self.__c.execute( insert_new_img_sql )
        self.__conn.commit()

    def clean_part_thumbnail(self, part_id):
        delete_sql = f'DELETE FROM [JJPart_PartThumbnail] WHERE [PartId]={part_id}'
        self.__c.execute( delete_sql )
        self.__conn.commit()

    def get_last_supply_record_link(self, this_id):
        select_sql = f'SELECT [LastId] FROM [JJStorage_SupplyRecordLink] WHERE [ThisId]={this_id}'
        self.__c.execute( select_sql )
        r = self.__c.fetchone()
        return r[0]

    @staticmethod
    def __null_2_empty_in_list(the_original_list):
        """ 将列表中的 None 全部转换为 str.empty """
        the_result = []
        for s in the_original_list:
            if s is None:
                the_result.append( '' )
            else:
                the_result.append( s )
        return the_result

    def get_part_info_quick(self, part_id):
        sql = f'SELECT [name], [description], [brand], [standard], [foreign_code], [jl_erp_code], [comment], [type]' \
              f' FROM [JJPart_PartDetail2] WHERE [id]={part_id}'
        self.__c.execute( sql )
        one_row = self.__c.fetchone()
        if one_row is not None:
            temp = self.__null_2_empty_in_list( one_row )
            if len( temp[3] ) < 1:
                description3 = f'{temp[2]} {temp[3]}'.strip()
            else:
                description3 = temp[2]
            result = temp[:2]
            result.append( description3 )
            result.extend( temp[4:] )
            return result
        else:
            return None

    def get_parts_by_config(self, part_id=None, name=None, english_name=None, description=None, column_config=None):
        if column_config[0] == 0:
            raise Exception( '必须显示项目号或零件号！' )
        use_status = 0 in column_config[5:-1]

        select_cmd = 'SELECT '
        default_segments = (
            'p.[PartID] AS id',
            'p.[Description1] AS name',
            'p.[Description4] AS english_name',
            'p.[Description2] AS description',
            's.[StatusDescription] AS status',
            'p.[Comment] AS comment'
        )
        option_segments = {
            0: ('', 'LEFT OUTER JOIN [JJPart_PartStatus] AS s ON s.[StatusType]=p.[StatusID])'),
            1: ('t1.[tag_name] AS type',
                '([JJCom_Tag] AS t1 INNER JOIN [JJCom_PartTag] AS pt1 ON '
                't1.[id]=pt1.[tag_id] AND t1.[parent_id]=1) ON p.[PartID]=pt1.[part_id]'),
            15: ('t2.[tag_name] AS standard',
                 '([JJCom_Tag] AS t2 INNER JOIN [JJCom_PartTag] AS pt2 ON '
                 't2.[id]=pt2.[tag_id] AND t2.[parent_id]=15) ON p.[PartID]=pt2.[part_id]'),
            16: ('t3.[tag_name] AS brand',
                 '([JJCom_Tag] AS t3 INNER JOIN [JJCom_PartTag] AS pt3 ON '
                 't3.[id]=pt3.[tag_id] AND t3.[parent_id]=16) ON p.[PartID]=pt3.[part_id]'),
            266: ('t4.[tag_name] AS jl_erp_code',
                  '([JJCom_Tag] AS t4 INNER JOIN [JJCom_PartTag] AS pt4 ON '
                  't4.[id]=pt4.[tag_id] AND t4.[parent_id]=266) ON p.[PartID]=pt4.[part_id]'),
            1288: ('t5.[tag_name] AS foreign_code',
                   '([JJCom_Tag] AS t5 INNER JOIN [JJCom_PartTag] AS pt5 ON '
                   't5.[id]=pt5.[tag_id] AND t5.[parent_id]=1288) ON p.[PartID]=pt5.[part_id]'),
            2064: ('t6.[tag_name] AS zd_erp_code',
                   '([JJCom_Tag] AS t6 INNER JOIN [JJCom_PartTag] AS pt6 ON '
                   't6.[id]=pt6.[tag_id] AND t6.[parent_id]=2064) ON p.[PartID]=pt6.[part_id]'),
            2111: ('t7.[tag_name] AS source',
                   '([JJCom_Tag] AS t7 INNER JOIN [JJCom_PartTag] AS pt7 ON '
                   't7.[id]=pt7.[tag_id] AND t7.[parent_id]=2111) ON p.[PartID]=pt7.[part_id]'),
            2112: ('t8.[tag_name] AS unit',
                   '([JJCom_Tag] AS t8 INNER JOIN [JJCom_PartTag] AS pt8 ON '
                   't8.[id]=pt8.[tag_id] AND t8.[parent_id]=2112) ON p.[PartID]=pt8.[part_id]'),
            2406: ('t9.[tag_name] AS product',
                   '([JJCom_Tag] AS t9 INNER JOIN [JJCom_PartTag] AS pt9 ON '
                   't9.[id]=pt9.[tag_id] AND t9.[parent_id]=2406) ON p.[PartID]=pt9.[part_id]')
        }
        the_display_columns = []
        from_tag_tables = []
        i = 0
        for c in column_config[0:5]:
            if c == 1:
                the_display_columns.append( default_segments[i] )
            i += 1
        for c in column_config[5:-1]:
            the_display_columns.append( option_segments[c][0] )
            from_tag_tables.append( option_segments[c][1] )
        if column_config[-1] == 1:
            the_display_columns.append( default_segments[-1] )
        if len( the_display_columns ) < 1:
            raise Exception( '没有选择要显示的字段！' )
        select_cmd += ', '.join( the_display_columns )
        f_str = '(' if use_status else ''
        select_cmd += f' {f_str}FROM [JJPart_Part] AS p '
        if column_config[4] == 1:
            select_cmd += option_segments[0][1]
        if len( from_tag_tables ) > 0:
            select_cmd += 'LEFT OUTER JOIN '
            from_tag_tables_str = ' LEFT OUTER JOIN '.join( from_tag_tables )
            select_cmd += from_tag_tables_str

        default_where = '(p.[StatusType]=90 OR p.[StatusType]=100)'
        if part_id is None and name is None and english_name is None and description is None:
            sql = '{0} WHERE {1} ORDER BY p.[PartID]'.format( select_cmd, default_where )
        elif part_id is not None:
            sql = '{0} WHERE {2} AND p.[PartID]={1}'.format( select_cmd, part_id, default_where )
        else:
            search_filter = ''
            if name is not None:
                search_filter += 'p.[Description1] LIKE \'%{0}%\''.format( name )
            if english_name is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'p.[Description4] LIKE \'%{0}%\''.format( english_name )
            if description is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'p.[Description2] LIKE \'%{0}%\''.format( description )
            sql = '{0} WHERE {1} AND {2} ORDER BY p.[PartID]'.format( select_cmd, search_filter, default_where )
        self.__c.execute( sql )
        temp = self.__c.fetchall()
        # 去除可能出现的重复
        result = {}
        for t in temp:
            id = t[0]
            if id in result:
                original_info = result[id]
                c = len( original_info )
                for i in range( 1, c ):
                    c_i = t[i]
                    o_i = original_info[i]
                    original_info[i] = self.__combi( o_i, c_i )
                result[id] = original_info
            else:
                result[id] = list( t )
        return result

    def get_available_supply_operation_bill(self, prefix=None):
        sql = f'SELECT COUNT(*) FROM [JJStorage_OperationBill] WHERE [BillName] LIKE \'{prefix}%\''
        self.__c.execute( sql )
        c = self.__c.fetchone()[0]
        return f'{prefix}-{c + 1}'

    def select_process_data(self, process_type=1):
        if process_type == 1 or process_type == 2:
            sql = 'SELECT b.[BillName], i.[ItemId], i.[PartId], i.[ErpId], b.[BuildDate], i.[Qty], ' \
                  'i.[DoingQty], i.[DoneQty], i.[Comment] ' \
                  'FROM [JJStorage_KbnSupplyItem] AS i INNER JOIN [JJStorage_KbnSupplyBill] AS b ' \
                  'ON i.[BillName]=b.[BillName] WHERE i.[DoneQty]+i.[DoingQty]<i.[Qty] AND b.[BuildDate]>\'2020/1/1\''
            self.__c.execute( sql )
            r_s = self.__c.fetchall()
            count = len( r_s )
            if process_type == 1:
                return count, r_s
            else:
                # 进行数据的进一步筛选，筛选出来源是“自制”的零件
                result = []
                for i in r_s:
                    sql = f'SELECT * FROM [JJCom_PartTag] WHERE [part_id]={i[2]} AND [tag_id]=17'
                    self.__c.execute( sql )
                    t_s = self.__c.fetchall()
                    if len( t_s ) > 0:
                        result.append( i )
                return len( result ), result
        elif process_type == 3 or process_type == 4:
            process_id_str = 'WHERE r.[Done]<>1 AND r.[Qty]>r.[DoneQty] AND (r.[Process]=11 OR r.[Process]=12)'
            if process_type == 4:
                process_id_str = 'WHERE r.[Process]=13'
            sql = 'SELECT r.[BillName], i.[ItemId], i.[PartId], i.[ErpId], r.[DoingDate], r.[Qty], ' \
                  'r.[DoneQty], r.[Comment], i.[Comment], r.[Id] ' \
                  'FROM [JJStorage_SupplyOperationRecord] AS r INNER JOIN [JJStorage_KbnSupplyItem] AS i ' \
                  'ON r.[LinkItem]=i.[ItemId] '
            sql += process_id_str
            self.__c.execute( sql )
            r_s = self.__c.fetchall()
            count = len( r_s )
            result = []
            for r in r_s:
                new_row = list( r[:7] )
                comment = r[7]
                comment_dict = {}
                if comment is None:
                    comment = ''
                else:
                    comment_dict = Com.str_2_dict( comment )
                    if 'Comment' in comment_dict:
                        comment = comment_dict['Comment']
                    else:
                        comment = ''
                if r[8] is not None and len( r[8] ) > 0:
                    comment += f' {r[8]}'
                if len( comment ) < 1:
                    comment = None
                new_row.extend( [Decimal( 0.0 ), comment, r[9]] )
                # 获取入库记录时，要仓位和单价的信息
                if process_type == 4:
                    pos = '' if not ('Position' in comment_dict) else comment_dict['Position']
                    u_price = '' if not ('UnitPrice' in comment_dict) else comment_dict['UnitPrice']
                    new_row.extend( [pos, u_price] )
                result.append( new_row )
            return count, result

    def create_supply_operation(self, data):
        pass

    def create_picking_record(self, data, mark):
        pass

    def next_available_part_id(self):
        sql = 'SELECT [PartID] FROM [JJPart_Part] WHERE [StatusType]=10'
        self.__c.execute( sql )
        r = self.__c.fetchone()
        if r is not None:
            sql = f'UPDATE [JJPart_Part] SET [StatusType]=20 WHERE [PartID]={r[0]}'
            self.__c.execute( sql )
            return r[0]
        get_max_id = f'SELECT MAX([PartID]) FROM [JJPart_Part]'
        self.__c.execute( get_max_id )
        r = self.__c.fetchone()
        next_id = r[0] + 1
        temp_create_part = f'INSERT INTO [JJPart_Part] VALUES ({next_id}, 20, null, \'dummy\', ' \
                           f'null, null, \'dummy\', null, null, null, null)'
        self.__c.execute( temp_create_part )
        self.__conn.commit()
        return next_id

    def set_part_id_2_prepared(self, part_id):
        sql = f'UPDATE [JJPart_Part] SET [StatusType]=10 WHERE [PartID]={part_id}'
        self.__c.execute( sql )
        self.__conn.commit()

    @staticmethod
    def __evaluate_str(ss):
        if ss is None:
            return 'NULL'
        if type( ss ) != str:
            raise TypeError( 'Type is not str.' )
        if len( ss ) < 1:
            return 'NULL'
        return f'\'{ss}\''

    @staticmethod
    def __combi(o_i, c_i):
        """
        比较两个字符，若不相同，则用逗号进行联接
        :param o_i: 原的字符串
        :param c_i: 新的字符串
        :return:
        """
        if (o_i == c_i) or (c_i is None or len( c_i ) < 1):
            return o_i
        if o_i is None or len( o_i ) < 1:
            return c_i
        return f'{o_i}, {c_i}'

    def create_a_new_part(self, part_id, name, english_name, description, comment, tag_dict):
        real_description = SqliteHandler.__evaluate_str( description )
        real_comment = SqliteHandler.__evaluate_str( comment )
        # 创建单元
        create_sql = f'UPDATE [JJPart_Part] SET [StatusType]=100, [Description1]=\'{name}\', ' \
                     f'[Description2]={real_description}, [Description4]=\'{english_name}\', ' \
                     f'[Comment]={real_comment} WHERE [PartID]={part_id}'
        self.__c.execute( create_sql )
        self.__conn.commit()
        # 创建标签
        for k in tag_dict:
            tag_list = self.get_tags( name=k )
            if len( tag_list ) > 0:
                parent_tag_id = tag_list[0][0]
            else:
                raise Exception( '没有所填写的父标签值。' )
            tag_list = self.get_tags( name=tag_dict[k], parent_id=parent_tag_id )
            if len( tag_list ) < 1:
                tag_id = self.create_one_tag( tag_dict[k], parent_tag_id )
            else:
                tag_id = tag_list[0][0]
            self.set_tag_2_part( tag_id, part_id )
            if k == '类别':
                get_type_sql = f'SELECT [ID], [GroupNr] FROM [JJPart_PartType] WHERE [TypeName]=\'{tag_dict[k]}\''
                self.__c.execute( get_type_sql )
                r = self.__c.fetchone()
                group_c = f'{r[1]:02d}0'
                update_part_type = f'UPDATE [JJPart_Part] SET [PartType]={r[0]}, [PartGroup]=\'{group_c}\' ' \
                                   f'WHERE [PartID]={part_id}'
                self.__c.execute( update_part_type )
                self.__conn.commit()
            elif k == '品牌' or k == '标准':
                get_description3 = f'SELECT [Description3] FROM [JJPart_Part] WHERE [PartID]={part_id}'
                self.__c.execute( get_description3 )
                des3 = self.__c.fetchone()[0]
                if des3 is None:
                    current_des3 = tag_dict[k]
                else:
                    tt = des3.strip()
                    if len( tt ) < 1:
                        current_des3 = tag_dict[k]
                    else:
                        current_des3 = f'{tt} {tag_dict[k]}'
                update_part_description3 = f'UPDATE [JJPart_Part] SET [Description3]=\'{current_des3}\' ' \
                                           f'WHERE [PartID]={part_id}'
                self.__c.execute( update_part_description3 )
                self.__conn.commit()

    def update_part_info(self, part_id, name, english_name, description, comment):
        if len( description ) < 1:
            real_description = 'null'
        else:
            real_description = f'\'{description}\''
        if len( comment ) < 1:
            real_comment = 'null'
        else:
            real_comment = f'\'{comment}\''
        # 更新单元
        create_sql = f'UPDATE [JJPart_Part] SET [Description1]=\'{name}\', [Description2]={real_description},' \
                     f' [Description4]=\'{english_name}\', [Comment]={real_comment} WHERE [PartID]={part_id}'
        self.__c.execute( create_sql )
        self.__conn.commit()

    def insert_requirements(self, bill_data, items_data):
        pass

    def get_require_bill(self, prefix=None, bill_num=None):
        sql = f'SELECT [BillName], [BuildDate], [Operator] FROM [JJStorage_KbnSupplyBill]'
        if prefix is None and bill_num is None:
            pass
        elif prefix is not None:
            sql += f' WHERE [BillName] LIKE \'{prefix}%\''
        elif bill_num is not None:
            sql += f' WHERE [BillName]==\'{bill_num}\''
        self.__c.execute( sql )
        r_s = self.__c.fetchall()
        if len( r_s ) < 1:
            return None
        else:
            return r_s

    def get_erp_info(self, erp_code, jl_erp=False):
        table_name = 'JJPart_ZdErp' if not jl_erp else 'JJPart_JlErp'
        sql = f'SELECT * FROM [{table_name}] WHERE [ErpId]=\'{erp_code}\''
        self.__c.execute( sql )
        r_s = self.__c.fetchall()
        if len( r_s ) < 1:
            return None
        return r_s[0][0], r_s[0][1], r_s[0][2]

    def get_products_by_id(self, product_id):
        self.__c.execute( 'SELECT * FROM [JJProduce_Product] WHERE [ProductId]=\'{0}\''.format( product_id ) )
        return self.__c.fetchall()

    def get_all_storing_position(self):
        sql = 'SELECT DISTINCT([Position]) FROM [JJStorage_Storing]'
        self.__c.execute( sql )
        r_s = self.__c.fetchall()
        result = []
        for r in r_s:
            result.append( r[0] )
        result.sort()
        return result

    def get_storing(self, part_id=None, position=None):
        sql = 'SELECT * FROM [JJStorage_Storing]'
        if part_id is not None or position is not None:
            sql += ' WHERE'
            if part_id is not None:
                sql += f' [PartId]={part_id}'
            if position is not None:
                if part_id is not None:
                    sql += ' AND'
                c = len( position )
                for i in range( c ):
                    if i > 0:
                        sql += ' OR'
                    sql += f' [Position]=\'{position[i]}\''
        self.__c.execute( sql )
        r = self.__c.fetchall()
        if len( r ) < 1:
            return None
        return r

    def del_tag_from_part(self, tag_id, part_id):
        sql = 'DELETE FROM [JJCom_PartTag] WHERE [tag_id]={0} AND [part_id]={1}'.format( tag_id, part_id )
        self.__c.execute( sql )
        self.__conn.commit()

    def del_one_tag(self, tag_id):
        del_link_sql = 'DELETE FROM [JJCom_PartTag] WHERE [tag_id]={0}'.format( tag_id )
        self.__c.execute( del_link_sql )
        del_tag_sql = 'DELETE FROM [JJCom_Tag] WHERE [id]={0}'.format( tag_id )
        self.__c.execute( del_tag_sql )
        self.__conn.commit()

    def rename_one_tag(self, tag_id, tag_name):
        update_tag_sql = 'UPDATE [JJCom_Tag] SET [tag_name]=\'{0}\' WHERE [id]={1}'.format( tag_name, tag_id )
        self.__c.execute( update_tag_sql )
        self.__conn.commit()

    def set_tag_2_part(self, tag_id, part_id):
        check_tag_link = 'SELECT [part_id] FROM [JJCom_PartTag] WHERE [part_id]={0} AND [tag_id]={1}'.format( part_id,
                                                                                                              tag_id )
        self.__c.execute( check_tag_link )
        if len( self.__c.fetchall() ) > 0:
            return False
        insert_tag_link = 'INSERT INTO [JJCom_PartTag] VALUES ({0}, {1})'.format( part_id, tag_id )
        self.__c.execute( insert_tag_link )
        self.__conn.commit()
        return True

    def copy(self):
        return 'SQLite3', SqliteHandler( database_file=self.__db_file, copy=True, conn=self.__conn )

    def create_one_tag(self, name, parent_id):
        tag_count = 'SELECT MAX([id]) FROM [JJCom_Tag]'
        self.__c.execute( tag_count )
        next_id = self.__c.fetchone()[0] + 1
        if parent_id is None:
            sort_count = 'SELECT MAX([sort_index]) FROM [JJCom_Tag] WHERE [parent_id] IS NULL'
            self.__c.execute( sort_count )
            next_sort_index = self.__c.fetchone()[0] + 1
            insert_sql = 'INSERT INTO [JJCom_Tag] VALUES ({0}, \'{1}\', NULL, {2})'.format( next_id, name,
                                                                                            next_sort_index )
        else:
            sort_count = 'SELECT MAX([sort_index]) FROM [JJCom_Tag] WHERE [parent_id]={0}'.format( parent_id )
            self.__c.execute( sort_count )
            the_sort = self.__c.fetchone()[0]
            if the_sort is None:
                next_sort_index = 1
            else:
                next_sort_index = the_sort + 1
            insert_sql = 'INSERT INTO [JJCom_Tag] VALUES ({0}, \'{1}\', {2}, {3})'.format( next_id, name,
                                                                                           parent_id, next_sort_index )
        self.__c.execute( insert_sql )
        self.__conn.commit()
        return next_id

    def save_change(self):
        if self.__conn is not None:
            self.__conn.commit()

    def get_tags_2_part(self, part_id):
        sql = 'SELECT t.[id], t.[tag_name], t.[parent_id], t.[sort_index] ' \
              'FROM [JJCom_Tag] AS t INNER JOIN [JJCom_PartTag] AS p ON t.[id]=p.[tag_id] ' \
              'WHERE p.[part_id]={0}'.format( part_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_parts_2_tag(self, tag_id):
        sql = 'SELECT [id], [name], [english_name], [description], [status], [comment] ' \
              'FROM [JJPart_PartTagView] WHERE [tag_id]={0}'.format( tag_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_tags(self, tag_id=None, name=None, parent_id=None):
        if tag_id is None and name is None and parent_id is None:
            # 找出没有父标签的标签
            sql = 'SELECT * FROM [JJCom_Tag] WHERE [parent_id] IS NULL AND [id] > 0 ORDER BY [id]'
        else:
            sql = 'SELECT * FROM [JJCom_Tag] WHERE'
            factor = False
            if tag_id is not None:
                sql = '{1} [id]={0}'.format( tag_id, sql )
                factor = True
            if name is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} [tag_name] LIKE \'%{0}%\''.format( name, sql )
                factor = True
            if parent_id is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} [parent_id]={0}'.format( parent_id, sql )
            sql += ' ORDER BY [sort_index], [id]'
        self.__c.execute( sql )
        return self.__c.fetchall()

    def __init__(self, database_file, copy=False, conn=None):
        self.__db_file = database_file
        # 为解决多线程的问题
        if not copy:
            self.__conn = sqlite3.connect( database_file, check_same_thread=False )
        else:
            self.__conn = conn
        self.__conn.isolation_level = None
        self.__conn.row_factory = sqlite3.Row
        self.__c = self.__conn.cursor()

    def get_parts(self, part_id=None, name=None, english_name=None, description=None):
        select_cmd = 'SELECT t.[PartID] AS id, t.[Description1] AS name, t.[Description4] AS english_name,' \
                     ' t.[Description2] AS description, s.[StatusDescription] AS status, t.[Comment] AS comment'
        from_database = 'FROM [JJPart_Part] AS t INNER JOIN [JJPart_PartStatus] AS s ON t.[StatusType]=s.[StatusID]'
        default_where = '(t.[StatusType]=90 OR t.[StatusType]=100)'
        if part_id is None and name is None and english_name is None and description is None:
            sql = '{0} {1} WHERE {2} ORDER BY t.[PartID]'.format( select_cmd, from_database, default_where )
        elif part_id is not None:
            sql = '{0} {1} WHERE {3} AND t.[PartID]={2}'.format( select_cmd, from_database, part_id, default_where )
        else:
            search_filter = ''
            if name is not None:
                search_filter += 't.[Description1] LIKE \'%{0}%\''.format( name )
            if english_name is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 't.[Description4] LIKE \'%{0}%\''.format( english_name )
            if description is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 't.[Description2] LIKE \'%{0}%\''.format( description )
            sql = '{1} {2} WHERE {3} AND {0} ORDER BY t.[PartID]'.format( search_filter, select_cmd,
                                                                          from_database, default_where )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_files_2_part(self, part_id):
        sql = 'SELECT [FilePath] FROM [JJPart_FileRelation] WHERE [PartID]={0}'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    def get_thumbnail_2_part(self, part_id, ver=None):
        sql = 'SELECT [Thumbnail], [Version] FROM [JJPart_PartThumbnail] ' \
              'WHERE [PartId]={0} ORDER BY [Version] DESC'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs[0][0]

    def get_children(self, part_id):
        sql = 'SELECT [Number] AS relation_index, [PartID] AS id, [Description1] AS name,' \
              ' [Description4] AS english_name, [StatusType] AS status, [Description2] AS description,' \
              ' [Comment] AS comment, [Quantity] AS qty_1,' \
              ' [ActualQty] AS qty_2, [PartRelationID] AS relation_id FROM [JJPart_ChildParts] ' \
              'WHERE [ParentPart]={0} ORDER BY [Number]'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_parents(self, part_id):
        sql = 'SELECT b.[Number], b.[ParentPart], a.[Description1], a.[Description4], c.[StatusDescription],' \
              ' a.[Description2], b.[Comment], b.[Quantity], b.[ActualQty], b.[PartRelationID]' \
              ' FROM [JJPart_PartRelation] AS b INNER JOIN ([JJPart_Part] AS a' \
              ' INNER JOIN [JJPart_PartStatus] AS c ON a.[StatusType]=c.[StatusID])' \
              ' ON b.[ParentPart]=a.[PartID]' \
              ' WHERE b.[ChildPart]={0}' \
              ' ORDER BY b.[ParentPart], b.[PartRelationID]'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_sub_tag_by_part_and_tag_name(self, part_id, tag_name):
        tt = self.get_tags( name=tag_name )
        if len( tt ) < 1:
            return None
        sql = 'SELECT t.[tag_name] ' \
              'FROM [JJCom_Tag] AS t INNER JOIN [JJCom_PartTag] AS p ON t.[id]=p.[tag_id] ' \
              'WHERE t.[parent_id]={0} AND p.[part_id]={1}'.format( tt[0][0], part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        temp = []
        for r in rs:
            temp.append( r[0] )
        return ','.join( temp )

    def close(self):
        try:
            if self.__c is not None:
                self.__c.close()
            if self.__conn is not None:
                self.__conn.close()
        except Exception as ex:
            print( f'Close Database Error: {ex}' )

    def sort_one_tag_to_index(self, tag_id, target_index):
        sql = 'UPDATE [JJCom_Tag] SET [sort_index]={0} WHERE [id]={1}'.format( target_index, tag_id )
        self.__c.execute( sql )

    def set_tag_parent(self, tag_id, parent_id):
        if parent_id is not None:
            sql = 'UPDATE [JJCom_Tag] SET [parent_id]={0} WHERE [id]={1}'.format( parent_id, tag_id )
        else:
            sql = 'UPDATE [JJCom_Tag] SET [parent_id]=NULL WHERE [id]={0}'.format( tag_id )
        self.__c.execute( sql )

    def get_pick_record_throw_erp(self, erp_id, which_company=1, top=2):
        """ 获取巨轮智能的ERP领料记录 """
        sql_top = ''
        if top > 0:
            sql_top = ' LIMIT 0,{0}'.format( top )
        sql = 'SELECT [BillNumber], [Qty], [Price], [PickDate] ' \
              'FROM [JJStorage_ErpPickingRecord] WHERE [PartNumber]=\'{0}\' ' \
              'AND [PickDate] > \'2018-1-1\' ORDER BY [PickDate] DESC{1}'.format( erp_id, sql_top )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            sql = 'SELECT [BillNumber], [Qty], [Price], [PickDate] ' \
                  'FROM [JJStorage_ErpPickingRecord] WHERE [PartNumber]=\'{0}\' ' \
                  'ORDER BY [PickDate] DESC{1}'.format( erp_id, sql_top )
            self.__c.execute( sql )
            rs = self.__c.fetchall()
            if len( rs ) < 1:
                return None
            else:
                return rs
        return rs

    def get_price_from_self_record(self, part_id, top=2):
        """ 获取本系统的价格记录信息 """
        sql_top = ''
        sql_top_1 = ''
        if top > 0:
            sql_top = ' ORDER BY [PartId], [Position] LIMIT 0,{0}'.format( top )
            sql_top_1 = ' LIMIT 0,{0}'.format( top )
        # 首先，从仓储数据进行检查
        sql = f'SELECT [UnitPrice], [Qty], [LastRecordDate] FROM [JJStorage_Storing] ' \
              f'WHERE [PartId]={part_id}{sql_top}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) > 0:
            result = []
            for r in rs:
                if r[0] is not None and r[0] > 0.0:
                    fade_qty = Decimal.from_float( r[1] ) if type( r[1] ) == float else r[1]
                    if fade_qty <= 0.001:
                        fade_qty = Decimal( 1.0 )
                    t0 = Decimal.from_float( r[0] ) if type( r[0] ) == float else r[0]
                    one_r = [0, t0 * fade_qty, Decimal.from_float( 0.0 ), Decimal.from_float( 0.0 ),
                             fade_qty, r[2], '库存']
                    result.append( one_r )
            if len( result ) > 0:
                return result
        sql = 'SELECT i.[ListID], i.[PriceWithTax], i.[OtherCost], l.[TaxRate], ' \
              'i.[Amount], l.[QuotedDate], s.[Name] FROM ' \
              '[JJCost_QuotationItem] AS i INNER JOIN [JJCost_Quotation] AS l ON i.[ListID]=l.[QuotationID] ' \
              'INNER JOIN [JJCost_Supplier] AS s ON l.[SupplierID]=s.[SupplierID] ' \
              'WHERE [PartID]={0} ORDER BY l.[QuotedDate] DESC{1}'.format( part_id, sql_top_1 )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_erp_data(self, erp_code):
        sql = f'SELECT [ErpId], [Description], [Unit] FROM [JJPart_ZdErp] WHERE [ErpId]=\'{erp_code}\''
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return erp_code, '', ''
        return rs[0]
