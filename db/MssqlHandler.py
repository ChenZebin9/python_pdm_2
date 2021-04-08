from db.DatabaseHandler import *
import pymssql
from decimal import Decimal
import Com


class MssqlHandler( DatabaseHandler ):

    def set_part_hyper_link(self, part_id, the_link):
        if the_link is None or len( the_link.strip() ) < 1:
            sql = f'DELETE FROM [JJCost].[PurchaseLink] WHERE [PartId]={part_id}'
            self.__c.execute( sql )
            return
        sql = f'SELECT [HyperLink] FROM [JJCost].[PurchaseLink] WHERE [PartId]={part_id}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            sql = f'INSERT INTO [JJCost].[PurchaseLink] VALUES ({part_id}, \'{the_link}\')'
        else:
            sql = f'UPDATE [JJCost].[PurchaseLink] SET [HyperLink]=\'{the_link}\' WHERE [PartId]={part_id}'
        self.__c.execute( sql )

    def get_part_hyper_link(self, part_id):
        sql = f'SELECT [HyperLink] FROM [JJCost].[PurchaseLink] WHERE [PartId]={part_id}'
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs[0][0]

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
        comment_4_sql = 'null'
        if relation_comment is not None and len( relation_comment ) > 0:
            comment_4_sql = f'\'{relation_comment.strip()}\''
        # MSSQL的PartRelationID有自动增量
        if relation_id is None:
            sql = f'INSERT INTO [JJPart].[PartRelation] ([ParentPart], [ChildPart], [Quantity],' \
                  f' [Unit], [Number], [Comment], [ActualQty]) VALUES ({parent_id}, {child_id}, {sum_qty},' \
                  f' \'件\', {index_id}, {comment_4_sql}, {actual_qty})'
            self.__c.execute( sql )
        else:
            sql = f'UPDATE [JJPart].[PartRelation] SET [Quantity]={sum_qty}, [Number]={index_id}, [Comment]={comment_4_sql},' \
                  f' [ActualQty]={actual_qty} WHERE [PartRelationID]={relation_id}'
            self.__c.execute( sql )

    def remove_part_relation(self, relation_id):
        """
        移除原先的关联
        :param relation_id: 关联ID
        :return:
        """
        sql = f'DELETE FROM [JJPart].[PartRelation] WHERE [PartRelationID]={relation_id}'
        self.__c.execute( sql )

    def get_last_supply_record_link(self, this_id):
        select_sql = f'SELECT [LastId] FROM [JJStorage].[SupplyRecordLink] WHERE [ThisId]={this_id}'
        self.__c.execute( select_sql )
        r = self.__c.fetchone()
        return r[0]

    def clean_part_thumbnail(self, part_id):
        delete_sql = f'DELETE FROM [JJPart].[PartThumbnail] WHERE [PartId]={part_id}'
        self.__c.execute( delete_sql )
        self.__conn.commit()

    def set_part_thumbnail(self, part_id, image_data):
        """
        设置零件的缩略图
        :param part_id: 零件号
        :param image_data: 图像数据
        :return:
        """
        get_version_sql = f'SELECT [Version] FROM [JJPart].[PartThumbnail] ' \
                          f'WHERE [PartId]={part_id} ORDER BY [Version] DESC'
        self.__c.execute( get_version_sql )
        r = self.__c.fetchone()
        next_version = 1
        if r is not None:
            next_version += r[0]
        insert_new_img_sql = 'INSERT INTO [JJPart].[PartThumbnail] ([PartID], [Thumbnail], [Version])' \
                             ' VALUES ({0}, {1}, {2})'.format( part_id, str( image_data, encoding='ascii' ),
                                                               next_version )
        self.__c.execute( insert_new_img_sql )
        self.__conn.commit()

    def cancel_supply_operation(self, record_id, cancel_qty):
        """
        将需求处理操作（JJStorage.SupplyOperationRecord）删除，并更新相关的物料需求（JJStorage.KbnSupplyItem）
        :param record_id: 需求处理操作编号
        :param cancel_qty: 要作废的数量
        :return:
        """
        sql = f'SELECT [Done], [Qty], [DoneQty], [LinkItem] FROM [JJStorage].[SupplyOperationRecord] WHERE [Id]={record_id}'
        self.__c.execute( sql )
        r = self.__c.fetchone()
        qty = float( r[1] )
        done_qty = float( r[2] )
        done_qty += cancel_qty
        done = 1 if done_qty >= qty else 0
        item_id = r[3]
        sql = f'UPDATE [JJStorage].[SupplyOperationRecord] SET [Done]={done}, [DoneQty]={done_qty} WHERE [Id]={record_id}'
        self.__c.execute( sql )
        self.cancel_material_requirement( item_id, cancel_qty, change_doing=True )

    def cancel_material_requirement(self, item_id, cancel_qty, change_doing=False):
        """
        将物料需求（JJStorage.KbnSupplyItem）作废
        :param change_doing: 是否改变doing字段的值
        :param cancel_qty: float 要作废的数量
        :param item_id: 需求编号
        :return:
        """
        sql = f'SELECT [DoneQty], [DoingQty] FROM [JJStorage].[KbnSupplyItem] WHERE [ItemId]={item_id}'
        self.__c.execute( sql )
        r = self.__c.fetchone()
        doing_qty = float( r[1] )
        update_doing_qty_str = ''
        if change_doing:
            update_doing_qty_str = f', [DoingQty]={doing_qty - cancel_qty} '
        all_done_qty = float( r[0] ) + cancel_qty
        sql = f'UPDATE [JJStorage].[KbnSupplyItem] SET [DoneQty]={all_done_qty}{update_doing_qty_str} ' \
              f'WHERE [ItemId]={item_id}'
        self.__c.execute( sql )
        self.__conn.commit()

    def create_put_back_material_record(self, bill_name, operator, when, data):
        """
        创建退料的操作数据
        :param when: 日期
        :param bill_name: 单号
        :param operator: 操作者
        :param data: 数据 [退料所倚靠的单号]
        :return:
        """
        # 创建退料单
        sql = f'INSERT INTO [JJStorage].[OperationBill] VALUES (\'{bill_name}\', \'{operator}\', \'{when}\', ' \
              f'\'退料单\', 0)'
        self.__c.execute( sql )
        # 创建退料单的项目
        sql = 'SELECT MAX([Id]) FROM [JJStorage].[SupplyOperationRecord]'
        self.__c.execute( sql )
        r = self.__c.fetchone()
        next_record_id = r[0] + 1
        for d in data:
            sql = f'SELECT [LinkItem], [DoneQty], [Comment] FROM [JJStorage].[SupplyOperationRecord] WHERE [Id]={d}'
            self.__c.execute( sql )
            r = self.__c.fetchone()
            other_data_dict = Com.str_2_dict( r[2] )
            other_data_dict['RollBack'] = 'Y'
            # 更新原有的纪录
            new_comment = Com.dict_2_str( other_data_dict )
            sql = f'UPDATE [JJStorage].[SupplyOperationRecord] SET [Comment]=\'{new_comment}\' WHERE [Id]={d}'
            self.__c.execute( sql )
            # 创建新的数据
            other_data_dict.pop( 'RollBack' )
            other_data_dict['OriginalRecord'] = f'{d}'
            price = 0.0
            price_need_update = False
            if 'Price' in other_data_dict:
                price_need_update = True
                price = float( other_data_dict['Price'] )
                price = -price
                other_data_dict['Price'] = '%.2f' % price
            new_comment = Com.dict_2_str( other_data_dict )
            qty = float( -r[1] )
            sql = f'INSERT INTO [JJStorage].[SupplyOperationRecord] VALUES ({next_record_id}, 1, \'{when}\', ' \
                  f'\'{operator}\', 14, {r[0]}, {qty}, \'{bill_name}\', {qty}, \'{new_comment}\')'
            self.__c.execute( sql )
            # 更新仓储信息
            sql = f'SELECT [PartId] FROM [JJStorage].[KbnSupplyItem] WHERE [ItemId]={r[0]}'
            self.__c.execute( sql )
            r = self.__c.fetchone()
            p_id = r[0]
            position = other_data_dict['FromStorage']
            # 获取库存信息
            get_storing = f'SELECT [Qty], [UnitPrice] FROM [JJStorage].[Storing] ' \
                          f'WHERE [PartId]={p_id} AND [Position]=\'{position}\''
            self.__c.execute( get_storing )
            r = self.__c.fetchone()
            qty_info = float( r[0] )
            unit_price = float( r[1] )
            if price_need_update:
                updated_price = (qty_info * unit_price + price) / (qty_info + qty)
            else:
                updated_price = unit_price
            # 更新仓库库存
            update_storing = f'UPDATE [JJStorage].[Storing] ' \
                             f'SET [Qty]={qty_info - qty}, [LastRecordDate]=\'{when}\', [UnitPrice]={updated_price} ' \
                             f'WHERE [PartId]={p_id} AND [Position]=\'{position}\''
            self.__c.execute( update_storing )
            next_record_id += 1
        self.__conn.commit()

    def get_pick_material_record(self, begin_date, end_date):
        """
        获取领料记录
        :param begin_date: 起始日期
        :param end_date: 结束日期
        :return: [BillName, ItemId, PartId, ErpId, DoingDate, DoneQty, Comment, RecordId]
        """
        sql = 'SELECT r.[BillName], i.[ItemId], i.[PartId], i.[ErpId], r.[DoingDate], ' \
              'r.[DoneQty], r.[Comment], r.[Id] AS [RecordId] FROM [JJStorage].[SupplyOperationRecord] AS r ' \
              'INNER JOIN [JJStorage].[KbnSupplyItem] AS i ON r.[LinkItem]=i.[ItemId] ' \
              'WHERE r.[Process]=14'
        sql += f' AND r.[DoingDate]>=\'{begin_date}\' AND r.[DoingDate]<=\'{end_date}\''
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_part_info_quick(self, part_id):
        """
        利用 PartDetail2 视图，快速获取PART的信息
        :param part_id:
        :return:[name, description, brand&standard, foreign_code, erp_code, comment, type]
        """
        sql = f'SELECT [name], [description], [brand], [standard], [foreign_code], [jl_erp_code], [comment], [type]' \
              f' FROM [JJPart].[PartDetail2] WHERE [id]={part_id}'
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
        create_sql = f'UPDATE [JJPart].[Part] SET [Description1]=\'{name}\', [Description2]={real_description},' \
                     f' [Description4]=\'{english_name}\', [Comment]={real_comment} WHERE [PartID]={part_id}'
        self.__c.execute( create_sql )
        self.__conn.commit()

    def create_a_new_part(self, part_id, name, english_name, description, comment, tag_dict):
        if len( description ) < 1:
            real_description = 'null'
        else:
            real_description = f'\'{description}\''
        if len( comment ) < 1:
            real_comment = 'null'
        else:
            real_comment = f'\'{comment}\''
        # 创建单元
        create_sql = f'UPDATE [JJPart].[Part] SET [StatusType]=100, [Description1]=\'{name}\', ' \
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
                get_type_sql = f'SELECT [ID], [GroupNr] FROM [JJPart].[PartType] WHERE [TypeName]=\'{tag_dict[k]}\''
                self.__c.execute( get_type_sql )
                r = self.__c.fetchone()
                group_c = f'{r[1]:02d}0'
                update_part_type = f'UPDATE [JJPart].[Part] SET [PartType]={r[0]}, [PartGroup]=\'{group_c}\' ' \
                                   f'WHERE [PartID]={part_id}'
                self.__c.execute( update_part_type )
                self.__conn.commit()
            elif k == '品牌' or k == '标准':
                get_description3 = f'SELECT [Description3] FROM [JJPart].[Part] WHERE [PartID]={part_id}'
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
                update_part_description3 = f'UPDATE [JJPart].[Part] SET [Description3]=\'{current_des3}\' ' \
                                           f'WHERE [PartID]={part_id}'
                self.__c.execute( update_part_description3 )
                self.__conn.commit()

    def set_part_id_2_prepared(self, part_id):
        sql = f'UPDATE [JJPart].[Part] SET [StatusType]=10 WHERE [PartID]={part_id}'
        self.__c.execute( sql )
        self.__conn.commit()

    def next_available_part_id(self):
        sql = 'SELECT [PartID] FROM [JJPart].[Part] WHERE [StatusType]=10'
        self.__c.execute( sql )
        r = self.__c.fetchone()
        if r is not None:
            sql = f'UPDATE [JJPart].[Part] SET [StatusType]=20 WHERE [PartID]={r[0]}'
            self.__c.execute( sql )
            return r[0]
        temp_create_part = f'INSERT INTO [JJPart].[Part] VALUES (20, null, \'dummy\', ' \
                           f'null, null, \'dummy\', null, null, null, null)'
        self.__c.execute( temp_create_part )
        get_max_id = f'SELECT MAX([PartID]) FROM [JJPart].[Part]'
        self.__c.execute( get_max_id )
        r = self.__c.fetchone()
        next_id = r[0]
        self.__conn.commit()
        return next_id

    def get_available_supply_operation_bill(self, prefix=None):
        sql = f'SELECT COUNT(*) FROM [JJStorage].[OperationBill] WHERE [BillName] LIKE \'{prefix}%\''
        self.__c.execute( sql )
        c = self.__c.fetchone()[0]
        return f'{prefix}-{c + 1}'

    def create_picking_record(self, data, mark):
        """
        创建出库记录
        :param mark: {}，里面包括：record - int
        :param data:{}，里面包括：BillName - str, Operator - str, DoingDate - str, BillType - str, FromStorage - str,
        Items - [Contract - str, PartId - int, ErpId - str, Qty - float, RecordIndex - int]
        :return:
        """
        bill_name = data[0]
        operator = data[1]
        the_date = data[2]
        bill_type = data[3]
        from_storage = data[4]
        current_process = 14
        except_type = 0  # 异常级别：0-询问解决、1-报警（无法解决）
        try:
            insert_require_bill_sql = f'INSERT INTO [JJStorage].[KbnSupplyBill] VALUES (\'{bill_name}\', \'{the_date}\', ' \
                                      f'\'{operator}\')'
            self.__c.execute( insert_require_bill_sql )
            insert_operation_bill_sql = f'INSERT INTO [JJStorage].[OperationBill] VALUES (\'{bill_name}\', \'{operator}\', ' \
                                        f'\'{the_date}\', \'{bill_type}\', 0)'
            self.__c.execute( insert_operation_bill_sql )

            self.__c.execute( 'SELECT MAX([Id]) FROM [JJStorage].[SupplyOperationRecord]' )
            temp_r = self.__c.fetchone()[0]
            if temp_r is None:
                next_operation_id = 1
            else:
                next_operation_id = temp_r + 1
            self.__c.execute( 'SELECT MAX([ItemId]) FROM [JJStorage].[KbnSupplyItem]' )
            temp_r = self.__c.fetchone()[0]
            if temp_r is None:
                next_require_id = 1
            else:
                next_require_id = temp_r + 1
            for item in data[5]:
                actual_storage = from_storage
                record_index = item[4]
                unit_price = None
                qty_need = item[3]  # 当前所需的数量
                while True:
                    if record_index in mark and mark[record_index] == 0:
                        actual_storage = 'X'
                    if actual_storage != 'X':
                        # 获取库存信息
                        get_storing = f'SELECT [Position], [Qty], [UnitPrice] FROM [JJStorage].[Storing] ' \
                                      f'WHERE [PartId]={item[1]} ORDER BY [Position]'
                        self.__c.execute( get_storing )
                        rs = self.__c.fetchall()
                        if len( rs ) < 1:
                            # 完全没有记录
                            except_type = 0
                            raise Exception( f'{item[1]:0>8} 没有相应的库存，是否直接打印？' )
                        qty_sum = 0.0
                        rr = []  # real_record, only D or E
                        if actual_storage == 'F':
                            for r in rs:
                                if r[0] == 'F':
                                    rr.append( r )
                        else:
                            for r in rs:
                                if r[0] == 'D' or r[0] == 'E':
                                    rr.append( r )
                        for r in rr:
                            qty_sum += r[1]
                        if qty_sum >= qty_need:
                            # 整体数量是足够的
                            remain_qty = qty_need
                            for r in rr:
                                if remain_qty < 0.0:
                                    break
                                if remain_qty > r[1]:
                                    q = r[1]
                                else:
                                    q = remain_qty
                                remain_qty -= q
                                # 更新仓库库存
                                update_storing = f'UPDATE [JJStorage].[Storing] ' \
                                                 f'SET [Qty]={r[1] - q}, [LastRecordDate]=\'{the_date}\' ' \
                                                 f'WHERE [PartId]={item[1]} AND [Position]=\'{r[0]}\''
                                self.__c.execute( update_storing )
                                # 创建需求记录
                                comment_dict = {'FromStorage': r[0], 'Contract': item[0]}
                                unit_price = r[2]
                                if unit_price is not None:
                                    comment_dict['Price'] = '%.2f' % (qty_need * float( unit_price ))
                                insert_require_item = f'INSERT INTO [JJStorage].[KbnSupplyItem] VALUES ({next_require_id}, ' \
                                                      f'\'{bill_name}\', {item[1]}, {q}, 0.0, {q}, \'{item[2]}\', ' \
                                                      f'null, null)'
                                self.__c.execute( insert_require_item )
                                # 创建操作记录
                                comment_str = Com.dict_2_str( comment_dict )
                                insert_operation_item = f'INSERT INTO [JJStorage].[SupplyOperationRecord] VALUES ({next_operation_id}, ' \
                                                        f'1, \'{the_date}\', \'{operator}\', {current_process}, {next_require_id}, ' \
                                                        f'{q}, \'{bill_name}\', {q}, \'{comment_str}\')'
                                self.__c.execute( insert_operation_item )
                                next_require_id += 1
                                next_operation_id += 1
                        else:
                            # 整体数量不足
                            except_type = 1
                            raise Exception( f'{item[1]:0>8} 库存不足，须修改领料数量！' )
                    else:
                        # 创建需求记录
                        comment_dict = {'FromStorage': actual_storage, 'Contract': item[0]}
                        insert_require_item = f'INSERT INTO [JJStorage].[KbnSupplyItem] VALUES ({next_require_id}, ' \
                                              f'\'{bill_name}\', {item[1]}, {qty_need}, 0.0, {qty_need}, \'{item[2]}\', ' \
                                              f'null, null)'
                        self.__c.execute( insert_require_item )
                        # 创建操作记录
                        comment_str = Com.dict_2_str( comment_dict )
                        insert_operation_item = f'INSERT INTO [JJStorage].[SupplyOperationRecord] VALUES ({next_operation_id}, ' \
                                                f'1, \'{the_date}\', \'{operator}\', {current_process}, {next_require_id}, ' \
                                                f'{qty_need}, \'{bill_name}\', {qty_need}, \'{comment_str}\')'
                        self.__c.execute( insert_operation_item )
                        next_require_id += 1
                        next_operation_id += 1
                    break
            self.__conn.commit()
            return None
        except Exception as e:
            self.__conn.rollback()
            return except_type, str( e ), record_index

    def create_supply_operation(self, data):
        """
        创建物料操作的数据库记录
        :param data:{}, 里面包括：部分BillName - str, Operator - str, DoingDate - str, BillType - str, NextProcess - int,
        Items - [LinkItem - int, Qty - float, Comment - str]
        当 NextProcess = 13 or 15 时，Items多了三项（原来有三项，总共六项）[LastOperationId - int, StorageId - str, UnitPrice - float]
        :return: 最终确定的 BillName
        """
        bill_name = data['BillName']
        bill_type = data['BillType']
        next_process = data['NextProcess']
        pre_fix = 'B'
        if bill_type == '投料单':
            pre_fix = 'B'
        elif bill_type == '派工单':
            pre_fix = 'M'
        elif bill_type == '入库单':
            pre_fix = 'S'
        try:
            bill_name = '{0}{1}'.format( pre_fix, bill_name )
            sql = f'SELECT COUNT(*) FROM [JJStorage].[OperationBill] WHERE [BillName] LIKE \'{bill_name}%\''
            self.__c.execute( sql )
            c = self.__c.fetchone()[0]
            bill_name += f'-{c + 1}'
            operator = data['Operator']
            doing_date = data['DoingDate']
            insert_bill_sql = f'INSERT INTO [JJStorage].[OperationBill] VALUES (\'{bill_name}\', \'{operator}\', ' \
                              f'\'{doing_date}\', \'{bill_type}\', 0)'
            self.__c.execute( insert_bill_sql )
            self.__c.execute( 'SELECT MAX([Id]) FROM [JJStorage].[SupplyOperationRecord]' )
            temp_r = self.__c.fetchone()[0]
            if temp_r is None:
                next_id = 1
            else:
                next_id = temp_r + 1
            items = data['Items']
            for item in items:
                if item[2] is None or len( item[2] ) < 1:
                    comment = 'null'
                else:
                    comment = {'Comment': item[2]}
                if bill_type == '入库单':
                    # 建立入库单时，在comment，补充仓位和单价的信息
                    if type( comment ) == str:
                        comment = {}
                    comment['Position'] = item[4]
                    if item[5] is not None:
                        comment['UnitPrice'] = '%.3f' % item[5]
                if type( comment ) == dict:
                    comment = '\'{0}\''.format( Com.dict_2_str( comment ) )
                done_qty = 0.0 if bill_type != '入库单' else item[1]
                is_done = 0 if bill_type != '入库单' else 1
                insert_item_sql = f'INSERT INTO [JJStorage].[SupplyOperationRecord] VALUES ({next_id}, {is_done}, ' \
                                  f'\'{doing_date}\', \'{operator}\', {next_process}, {item[0]}, {item[1]}, ' \
                                  f'\'{bill_name}\', {done_qty}, {comment})'
                self.__c.execute( insert_item_sql )
                # 建立 supply operation 的链接
                last_supply_record = None
                if bill_type == '入库单':
                    last_supply_record = item[3]
                    if next_process == 15:  # 退库单则需要绑定再上一级的记录
                        update_o_link = f'UPDATE [JJStorage].[SupplyOperationRecord] SET [Process]=15 ' \
                                        f'WHERE [Id]={item[3]}'
                        self.__c.execute( update_o_link )
                        last_supply_record = self.get_last_supply_record_link( last_supply_record )
                    insert_item_sql = f'INSERT INTO [JJStorage].[SupplyRecordLink] VALUES ' \
                                      f'({next_id}, {last_supply_record})'
                    self.__c.execute( insert_item_sql )
                get_link_item_info = f'SELECT [Qty], [DoingQty], [DoneQty], [PartId] FROM [JJStorage].[KbnSupplyItem] ' \
                                     f'WHERE [ItemId]={item[0]}'
                self.__c.execute( get_link_item_info )
                qty_info = self.__c.fetchone()
                part_id = qty_info[3]
                if bill_type == '投料单' or bill_type == '派工单':
                    update_link_item = f'UPDATE [JJStorage].[KbnSupplyItem] ' \
                                       f'SET [DoingQty]={float( qty_info[1] ) + item[1]} ' \
                                       f'WHERE [ItemId]={item[0]}'
                    self.__c.execute( update_link_item )
                else:
                    # 更新需求数据
                    required_doing_qty = float( qty_info[1] ) - item[1]
                    required_done_qty = float( qty_info[2] ) + item[1]
                    update_link_item = f'UPDATE [JJStorage].[KbnSupplyItem] SET [DoingQty]={required_doing_qty}, ' \
                                       f'[DoneQty]={required_done_qty} WHERE [ItemId]={item[0]}'
                    self.__c.execute( update_link_item )
                    # 更新上一个操作的数据
                    get_operation_info_sql = f'SELECT [Qty], [DoneQty] FROM [JJStorage].[SupplyOperationRecord] ' \
                                             f'WHERE [Id]={item[3]}'
                    self.__c.execute( get_operation_info_sql )
                    last_operation_info = self.__c.fetchone()
                    operation_done_qty = float( last_operation_info[1] ) + item[1]
                    if operation_done_qty >= last_operation_info[0]:
                        additional_update = ', [Done]=1 '
                    else:
                        additional_update = ', [Done]=0 '
                    update_last_operation = f'UPDATE [JJStorage].[SupplyOperationRecord] ' \
                                            f'SET [DoneQty]={operation_done_qty}{additional_update} ' \
                                            f'WHERE [Id]={last_supply_record}'
                    self.__c.execute( update_last_operation )
                    # 更新仓储数据
                    get_storing_info_sql = f'SELECT * FROM [JJStorage].[Storing] ' \
                                           f'WHERE [PartId]={part_id} AND [Position]=\'{item[4]}\''
                    self.__c.execute( get_storing_info_sql )
                    r_s = self.__c.fetchall()
                    if len( r_s ) < 1:
                        if item[5] is None:
                            unit_price = 'null'
                        else:
                            unit_price = '{0}'.format( item[5] )
                        insert_new_storing = f'INSERT INTO [JJStorage].[Storing] ' \
                                             f'VALUES ({part_id}, \'{item[4]}\', {item[1]}, ' \
                                             f'\'{doing_date}\', {unit_price})'
                        self.__c.execute( insert_new_storing )
                    else:
                        # 不同仓位的价格可能不同
                        qty_sum = 0.0
                        for r in r_s:
                            qty_sum += r[2]
                        current_price = r_s[0][4]
                        neu_unit_price = None
                        if current_price is None:
                            if item[5] is not None:
                                neu_unit_price = '{0}'.format( item[5] )
                        else:
                            original_price_sum = qty_sum * float( current_price )
                            if item[5] is None:
                                neu_unit_price = current_price
                            else:
                                neu_price_sum = item[5] * item[1] + original_price_sum
                                new_sum = qty_sum + item[1]
                                if new_sum > 0:
                                    neu_unit_price = neu_price_sum / (qty_sum + item[1])
                                else:
                                    neu_unit_price = 0.0
                        unit_price_str = 'null'
                        if neu_unit_price is not None:
                            unit_price_str = '{0}'.format( neu_unit_price )
                        update_new_storing = f'UPDATE [JJStorage].[Storing] SET ' \
                                             f'[Qty]={qty_sum + item[1]}, [LastRecordDate]=\'{doing_date}\', ' \
                                             f'[UnitPrice]={unit_price_str} ' \
                                             f'WHERE [PartId]={part_id} AND [Position]=\'{item[4]}\''
                        self.__c.execute( update_new_storing )
                next_id += 1
            self.__conn.commit()
            return bill_name
        except Exception as e:
            self.__conn.rollback()
            raise e

    def select_process_data(self, process_type=1):
        """
        查询处于某些阶段（根据process_type的数值）的过程数据
        :param process_type: 1=可投料，2=可派工，3=可入库，4=可领料
        :return: 数量, None（或者数据）[BillName, ItemId, PartId, ErpId, 上次处理日期, Qty, DoingQty, DoneQty, Comment]
                 注：此处的comment = KbnSupplyItem的Comment + SupplyOperationRecord的Comment
        """
        if process_type == 1 or process_type == 2:
            sql = 'SELECT b.[BillName], i.[ItemId], i.[PartId], i.[ErpId], b.[BuildDate], i.[Qty], ' \
                  'i.[DoingQty], i.[DoneQty], i.[Comment] ' \
                  'FROM [JJStorage].[KbnSupplyItem] AS i INNER JOIN [JJStorage].[KbnSupplyBill] AS b ' \
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
                    sql = f'SELECT * FROM [JJCom].[PartTag] WHERE [part_id]={i[2]} AND [tag_id]=17'
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
                  'FROM [JJStorage].[SupplyOperationRecord] AS r INNER JOIN [JJStorage].[KbnSupplyItem] AS i ' \
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

    def insert_requirements(self, bill_data, items_data):
        sql = f'INSERT INTO [JJStorage].[KbnSupplyBill] ' \
              f'VALUES (\'{bill_data[0]}\', \'{bill_data[1]}\', \'{bill_data[2]}\')'
        self.__c.execute( sql )
        get_index_sql = 'SELECT MAX([ItemId]) FROM [JJStorage].[KbnSupplyItem]'
        self.__c.execute( get_index_sql )
        t = self.__c.fetchone()[0]
        if t is None:
            next_index = 1
        else:
            next_index = t + 1
        for item in items_data:
            if item[3] is None or len( item[3] ) < 1:
                the_comment = 'NULL'
            else:
                the_comment = f'\'{item[3]}\''
            if item[1] is None:
                the_erp_id = 'NULL'
            else:
                the_erp_id = f'\'{item[1]}\''
            the_qty = '%.2f' % item[2]
            sql = f'INSERT INTO [JJStorage].[KbnSupplyItem] ' \
                  f'VALUES ({next_index}, \'{bill_data[0]}\', {item[0]}, {the_qty}, 0.0, 0.0, {the_erp_id}, NULL, ' \
                  f'{the_comment})'
            next_index += 1
            self.__c.execute( sql )
        self.__conn.commit()

    def get_require_bill(self, prefix=None, bill_num=None):
        sql = f'SELECT [BillName], [BuildDate], [Operator] FROM [JJStorage].[KbnSupplyBill]'
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
        # TODO 使用巨轮智能的仓库时的情况？
        sql = f'SELECT * FROM JJPart.ZdErp WHERE ErpId=\'{erp_code}\''
        self.__c.execute( sql )
        r_s = self.__c.fetchall()
        if len( r_s ) < 1:
            return None
        return r_s[0][0], r_s[0][1], r_s[0][2]

    def get_products_by_id(self, product_id):
        self.__c.execute( 'SELECT * FROM JJProduce.Product WHERE ProductId=\'{0}\''.format( product_id ) )
        return self.__c.fetchall()

    def get_all_storing_position(self):
        sql = 'SELECT DISTINCT(Position) FROM JJStorage.Storing'
        self.__c.execute( sql )
        r_s = self.__c.fetchall()
        result = []
        for r in r_s:
            result.append( r[0] )
        result.sort()
        return result

    def get_storing(self, part_id=None, position=None):
        sql = 'SELECT * FROM JJStorage.Storing'
        if part_id is not None or position is not None:
            sql += ' WHERE'
            if part_id is not None:
                sql += f' PartId={part_id}'
            if position is not None:
                if part_id is not None:
                    sql += ' AND'
                c = len( position )
                for i in range( c ):
                    if i > 0:
                        sql += ' OR'
                    sql += f' Position=\'{position[i]}\''
        self.__c.execute( sql )
        r = self.__c.fetchall()
        if len( r ) < 1:
            return None
        return r

    def del_tag_from_part(self, tag_id, part_id):
        sql = 'DELETE FROM JJCom.PartTag WHERE tag_id={0} AND part_id={1}'.format( tag_id, part_id )
        self.__c.execute( sql )
        self.__conn.commit()

    def get_parents(self, part_id):
        sql = 'SELECT b.Number, b.ParentPart, a.Description1, a.Description4, c.StatusDescrption,' \
              ' a.Description2, b.Comment, b.Quantity, b.ActualQty, b.PartRelationID' \
              ' FROM JJPart.PartRelation AS b INNER JOIN (JJPart.Part AS a' \
              ' INNER JOIN JJPart.PartStatus AS c ON a.StatusType=c.StatusID)' \
              ' ON b.ParentPart=a.PartID' \
              ' WHERE b.ChildPart={0}' \
              ' ORDER BY b.ParentPart, b.PartRelationID'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def copy(self):
        # 能否用本身的 conn 作为参数传递？待测试。
        return 'MSSQL', MssqlHandler( self.__server, self.__database, self.__user, self.__password )

    def set_tag_2_part(self, tag_id, part_id):
        check_tag_link = 'SELECT part_id FROM JJCom.PartTag WHERE part_id={0} AND tag_id={1}'.format( part_id, tag_id )
        self.__c.execute( check_tag_link )
        if len( self.__c.fetchall() ) > 0:
            return False
        insert_tag_link = 'INSERT INTO JJCom.PartTag VALUES ({0}, {1})'.format( part_id, tag_id )
        self.__c.execute( insert_tag_link )
        self.__conn.commit()
        return True

    def rename_one_tag(self, tag_id, tag_name):
        update_tag_sql = 'UPDATE JJCom.Tag SET tag_name=\'{0}\' WHERE id={1}'.format( tag_name, tag_id )
        self.__c.execute( update_tag_sql )
        self.__conn.commit()

    def del_one_tag(self, tag_id):
        del_link_sql = 'DELETE FROM JJCom.PartTag WHERE tag_id={0}'.format( tag_id )
        self.__c.execute( del_link_sql )
        del_tag_sql = 'DELETE FROM JJCom.Tag WHERE id={0}'.format( tag_id )
        self.__c.execute( del_tag_sql )
        self.__conn.commit()

    def create_one_tag(self, name, parent_id):
        tag_count = 'SELECT MAX(id) FROM JJCom.Tag'
        self.__c.execute( tag_count )
        next_id = self.__c.fetchone()[0] + 1
        if parent_id is None:
            sort_count = 'SELECT MAX(sort_index) FROM JJCom.Tag WHERE parent_id is NULL'
            self.__c.execute( sort_count )
            next_sort_index = self.__c.fetchone()[0] + 1
            insert_sql = 'INSERT INTO JJCom.Tag VALUES ({0}, \'{1}\', NULL, {2})'.format( next_id, name,
                                                                                          next_sort_index )
        else:
            sort_count = 'SELECT MAX(sort_index) FROM JJCom.Tag WHERE parent_id={0}'.format( parent_id )
            self.__c.execute( sort_count )
            the_sort = self.__c.fetchone()[0]
            if the_sort is None:
                next_sort_index = 1
            else:
                next_sort_index = the_sort + 1
            insert_sql = 'INSERT INTO JJCom.Tag VALUES ({0}, \'{1}\', {2}, {3})'.format( next_id, name,
                                                                                         parent_id, next_sort_index )
        self.__c.execute( insert_sql )
        self.__conn.commit()
        return next_id

    def __init__(self, server, database, user, password):
        self.__server = server
        self.__database = database
        self.__user = user
        self.__password = password
        self.__conn = pymssql.connect( server=server, user=user, password=password, database=database,
                                       login_timeout=10 )
        self.__c = self.__conn.cursor()

    def get_parts(self, part_id=None, name=None, english_name=None, description=None):
        select_cmd = 'SELECT t.PartID AS id, t.Description1 AS name, t.Description4 AS english_name,' \
                     ' t.Description2 AS description, s.StatusDescrption AS status, t.Comment AS comment'
        from_database = 'FROM JJPart.Part AS t INNER JOIN JJPart.PartStatus AS s ON t.StatusType=s.StatusID'
        default_where = '(t.StatusType=90 OR t.StatusType=100)'
        if part_id is None and name is None and english_name is None and description is None:
            sql = '{0} {1} WHERE {2} ORDER BY t.PartID'.format( select_cmd, from_database, default_where )
        elif part_id is not None:
            sql = '{0} {1} WHERE {3} AND t.PartID={2}'.format( select_cmd, from_database, part_id, default_where )
        else:
            search_filter = ''
            if name is not None:
                search_filter += 't.Description1 LIKE \'%{0}%\''.format( name )
            if english_name is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 't.Description4 LIKE \'%{0}%\''.format( english_name )
            if description is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 't.Description2 LIKE \'%{0}%\''.format( description )
            sql = '{1} {2} WHERE {3} AND {0} ORDER BY t.PartID'.format( search_filter, select_cmd,
                                                                        from_database, default_where )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_parts_by_config(self, part_id=None, name=None, english_name=None, description=None, column_config=None):
        if column_config[0] == 0:
            raise Exception( '必须显示项目号或零件号！' )

        select_cmd = 'SELECT '
        default_segments = (
            'p.[PartID] AS id',
            'p.[Description1] AS name',
            'p.[Description4] AS english_name',
            'p.[Description2] AS description',
            's.[StatusDescrption] AS status',
            'p.[Comment] AS comment'
        )
        option_segments = {
            0: ('', 'LEFT OUTER JOIN [JJPart].[PartStatus] AS s ON s.[StatusType]=p.[StatusID]'),
            1: ('t1.[tag_name] AS type',
                '[JJCom].[Tag] AS t1 INNER JOIN [JJCom].[PartTag] AS pt1 ON '
                't1.[id]=pt1.[tag_id] AND t1.[parent_id]=1 ON p.[PartID]=pt1.[part_id]'),
            15: ('t2.[tag_name] AS standard',
                 '[JJCom].[Tag] AS t2 INNER JOIN [JJCom].[PartTag] AS pt2 ON '
                 't2.[id]=pt2.[tag_id] AND t2.[parent_id]=15 ON p.[PartID]=pt2.[part_id]'),
            16: ('t3.[tag_name] AS brand',
                 '[JJCom].[Tag] AS t3 INNER JOIN [JJCom].[PartTag] AS pt3 ON '
                 't3.[id]=pt3.[tag_id] AND t3.[parent_id]=16 ON p.[PartID]=pt3.[part_id]'),
            266: ('t4.[tag_name] AS jl_erp_code',
                  '[JJCom].[Tag] AS t4 INNER JOIN [JJCom].[PartTag] AS pt4 ON '
                  't4.[id]=pt4.[tag_id] AND t4.[parent_id]=266 ON p.[PartID]=pt4.[part_id]'),
            1288: ('t5.[tag_name] AS foreign_code',
                   '[JJCom].[Tag] AS t5 INNER JOIN [JJCom].[PartTag] AS pt5 ON '
                   't5.[id]=pt5.[tag_id] AND t5.[parent_id]=1288 ON p.[PartID]=pt5.[part_id]'),
            2064: ('t6.[tag_name] AS zd_erp_code',
                   '[JJCom].[Tag] AS t6 INNER JOIN [JJCom].[PartTag] AS pt6 ON '
                   't6.[id]=pt6.[tag_id] AND t6.[parent_id]=2064 ON p.[PartID]=pt6.[part_id]'),
            2111: ('t7.[tag_name] AS source',
                   '[JJCom].[Tag] AS t7 INNER JOIN [JJCom].[PartTag] AS pt7 ON '
                   't7.[id]=pt7.[tag_id] AND t7.[parent_id]=2111 ON p.[PartID]=pt7.[part_id]'),
            2112: ('t8.[tag_name] AS unit',
                   '[JJCom].[Tag] AS t8 INNER JOIN [JJCom].[PartTag] AS pt8 ON '
                   't8.[id]=pt8.[tag_id] AND t8.[parent_id]=2112 ON p.[PartID]=pt8.[part_id]'),
            2406: ('t9.[tag_name] AS product',
                   '[JJCom].[Tag] AS t9 INNER JOIN [JJCom].[PartTag] AS pt9 ON '
                   't9.[id]=pt9.[tag_id] AND t9.[parent_id]=2406 ON p.[PartID]=pt9.[part_id]')
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

        select_cmd += ' FROM [JJPart].[Part] AS p '
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
                    original_info[i] = MssqlHandler.__combi( o_i, c_i )
                result[id] = original_info
            else:
                result[id] = list( t )
        return result

    def get_tags(self, tag_id=None, name=None, parent_id=None):
        if tag_id is None and name is None and parent_id is None:
            # 找出没有父标签的标签
            sql = 'SELECT * FROM JJCom.Tag WHERE parent_id is NULL AND id > 0 ORDER BY id'
        else:
            sql = 'SELECT * FROM JJCom.Tag WHERE'
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

    def get_tags_2_part(self, part_id):
        sql = 'SELECT t.id, t.tag_name, t.parent_id, t.sort_index ' \
              'FROM JJCom.Tag AS t INNER JOIN JJCom.PartTag AS p ON t.id=p.tag_id ' \
              'WHERE p.part_id={0}'.format( part_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_sub_tag_by_part_and_tag_name(self, part_id, tag_name):
        tt = self.get_tags( name=tag_name )
        if len( tt ) < 1:
            return None
        sql = 'SELECT t.tag_name ' \
              'FROM JJCom.Tag AS t INNER JOIN JJCom.PartTag AS p ON t.id=p.tag_id ' \
              'WHERE t.parent_id={0} AND p.part_id={1}'.format( tt[0][0], part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        temp = []
        for r in rs:
            temp.append( r[0] )
        return ' '.join( temp )

    def get_parts_2_tag(self, tag_id):
        sql = 'SELECT id, name, english_name, description, status, comment ' \
              'FROM JJPart.PartTagView WHERE tag_id={0}'.format( tag_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_files_2_part(self, part_id):
        sql = 'SELECT FilePath FROM JJPart.FileRelation WHERE PartID={0}'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    def get_thumbnail_2_part(self, part_id, ver=None):
        sql = 'SELECT Thumbnail, Version FROM JJPart.PartThumbnail ' \
              'WHERE PartId={0} ORDER BY Version DESC'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs[0][0]

    def get_children(self, part_id):
        sql = 'SELECT Number AS relation_index, PartID AS id, Description1 AS name, Description4 AS english_name,' \
              ' StatusType AS status, Description2 AS description, Comment AS comment, Quantity AS qty_1,' \
              ' ActualQty AS qty_2, PartRelationID AS relation_id FROM JJPart.ChildParts ' \
              'WHERE ParentPart={0} ORDER BY Number'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def close(self):
        # if self.__c is not None:
        #     self.__c.close()
        if self.__conn is not None:
            self.__conn.close()

    def save_change(self):
        if self.__conn is not None:
            self.__conn.commit()

    def sort_one_tag_to_index(self, tag_id, target_index):
        sql = 'UPDATE JJCom.Tag SET sort_index={0} WHERE id={1}'.format( target_index, tag_id )
        self.__c.execute( sql )

    def set_tag_parent(self, tag_id, parent_id):
        if parent_id is not None:
            sql = 'UPDATE JJCom.Tag SET parent_id={0} WHERE id={1}'.format( parent_id, tag_id )
        else:
            sql = 'UPDATE JJCom.Tag SET parent_id=NULL WHERE id={0}'.format( tag_id )
        self.__c.execute( sql )

    def get_pick_record_throw_erp(self, erp_id, which_company=1, top=2):
        """ 获取巨轮智能的ERP领料记录 """
        sql_top = ''
        if top > 0:
            sql_top = 'TOP({0}) '.format( top )
        sql = 'SELECT {1}BillNumber, Qty, Price, PickDate ' \
              'FROM JJStorage.ErpPickingRecord WHERE PartNumber=\'{0}\' ' \
              'AND PickDate > \'2018-1-1\' ORDER BY PickDate DESC'.format( erp_id, sql_top )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            sql = 'SELECT {1}BillNumber, Qty, Price, PickDate ' \
                  'FROM JJStorage.ErpPickingRecord WHERE PartNumber=\'{0}\' ' \
                  'ORDER BY PickDate DESC'.format( erp_id, sql_top )
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
        if top > 0:
            sql_top = 'TOP({0}) '.format( top )
        # 首先，从仓储数据进行检查
        sql = f'SELECT {sql_top}[UnitPrice], CONVERT(DECIMAL, [Qty]), [LastRecordDate] FROM [JJStorage].[Storing] ' \
              f'WHERE [PartId]={part_id}'
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) > 0:
            result = []
            for r in rs:
                if r[0] is not None and r[0] > 0.0:
                    fade_qty = r[1]
                    if fade_qty <= 0.001:
                        fade_qty = Decimal( 1.0 )
                    one_r = [0, r[0] * fade_qty, Decimal.from_float( 0.0 ), Decimal.from_float( 0.0 ),
                             fade_qty, r[2], '库存']
                    result.append( one_r )
            if len( result ) > 0:
                return result
        sql = 'SELECT {1}i.ListID, i.PriceWithTax, i.OtherCost, CONVERT(DECIMAL(5,2), l.TaxRate), ' \
              'CONVERT(DECIMAL, i.Amount), l.QuotedDate, s.Name FROM ' \
              'JJCost.QuotationItem AS i INNER JOIN JJCost.Quotation AS l ON i.ListID=l.QuotationID ' \
              'INNER JOIN JJCost.Supplier AS s ON l.SupplierID=s.SupplierID ' \
              'WHERE PartID={0} ORDER BY l.QuotedDate DESC'.format( part_id, sql_top )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_erp_data(self, erp_code):
        sql = f'SELECT [ErpId], [Description], [Unit] FROM [JJPart].[ZdErp] WHERE [ErpId]=\'{erp_code}\''
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return erp_code, '', ''
        return rs[0]

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
