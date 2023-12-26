import datetime
import io
import sqlite3
import tempfile
from decimal import Decimal

from PIL import Image

import Com
from db.DatabaseHandler import *


class SqliteHandler(DatabaseHandler):

    def update_jo_erp_foundation_info(self, _data):
        """
        更新钜欧的ERP基础物料数据
        :param _data: [(erp_id, description, _unit)]
        :return: 处理的统计结果
        """
        insert_c = 0
        update_c = 0
        no_c = 0
        for r in _data:
            erp_id = r[0]
            description = r[1]
            _unit = r[2]
            self.__c.execute(f'SELECT * FROM [JJPart_JoErp] WHERE [ErpId]=\'{erp_id}\'')
            rs = self.__c.fetchall()
            if len(rs) > 0:
                if description != rs[0][1]:
                    self.__c.execute(
                        f'UPDATE [JJPart_JoErp] SET [Description]=\'{description}\' WHERE [ErpId]=\'{erp_id}\'')
                    update_c += 1
                else:
                    no_c += 1
            else:
                self.__c.execute(f'INSERT INTO [JJPart_JoErp] VALUES (\'{erp_id}\', \'{description}\', \'{_unit}\')')
                insert_c += 1
        self.__conn.commit()
        return f'新增{insert_c}个，更新{update_c}个，未处理{no_c}个。'

    def edit_part_to_identical_group(self, fun_id, part_id, grade=6, add_action=True):
        """
        一个零件对于同质组的操作，加入或移除
        :param grade: 评分，1-10，仅作为参考
        :param fun_id:
        :param part_id:
        :param add_action: True - 加入，False - 移除
        :return:
        """
        try:
            sql = f'SELECT [ID] FROM [JJPart_IdenticalPartLink] WHERE [FunctionID]={fun_id} AND [Part]={part_id}'
            self.__c.execute(sql)
            r_s = self.__c.fetchall()
            if add_action:
                if len(r_s) < 1:
                    next_id_sql = 'SELECT MAX([ID]) FROM [JJPart_IdenticalPartLink]'
                    self.__c.execute(next_id_sql)
                    next_id = self.__c.fetchone()[0] + 1
                    insert_sql = f'INSERT INTO [JJPart_IdenticalPartLink] VALUES ' \
                                 f'({next_id}, {fun_id}, {part_id}, {grade}, 1)'
                    self.__c.execute(insert_sql)
                else:
                    _id = r_s[0][0]
                    update_sql = f'UPDATE [JJPart_IdenticalPartLink] SET [Evaluate]={grade} WHERE [ID]={_id}'
                    self.__c.execute(update_sql)
            else:
                if len(r_s) < 1:
                    raise Exception('零件不属于该同质组，无法移除。')
                _id = r_s[0][0]
                delete_sql = f'DELETE FROM [JJPart_IdenticalPartLink] WHERE [ID]={_id}'
                self.__c.execute(delete_sql)
            self.__conn.commit()
        except Exception as ex:
            self.__conn.rollback()
            raise ex

    def delete_identical_description(self, fun_id):
        """
        删除同质单元描述
        :param fun_id:
        :return:
        """
        sql = f'SELECT * FROM [JJPart_IdenticalPart] WHERE [ID]={fun_id}'
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        if len(r_s) < 1:
            raise Exception('没有找到相应的同质描述ID。')
        sql = f'UPDATE [JJPart_IdenticalPart] SET [StatusType]=0 WHERE [ID]={fun_id}'
        self.__c.execute(sql)
        self.__conn.commit()

    def set_identical_description(self, fun_description, fun_id=-1):
        """
        创建或更新同质单元描述
        :param fun_description: 描述文本
        :param fun_id: -1：创建并返回新Id，>0：更新同质描述
        :return:
        """
        next_id = 0
        if fun_id < 0:
            # 创建新同质描述
            sql = 'SELECT MAX([ID]) FROM [JJPart_IdenticalPart]'
            self.__c.execute(sql)
            r = self.__c.fetchone()[0]
            next_id = r + 1
            sql = f'INSERT INTO [JJPart_IdenticalPart] VALUES ({next_id}, \'{fun_description}\', 100, null)'
            self.__c.execute(sql)
            self.__conn.commit()
            return next_id
        else:
            # 更新现有同质描述
            sql = f'SELECT * FROM [JJPart_IdenticalPart] WHERE [ID]={fun_id}'
            self.__c.execute(sql)
            r_s = self.__c.fetchall()
            if len(r_s) < 1:
                raise Exception('没有找到相应的同质描述ID。')
            sql = f'UPDATE [JJPart_IdenticalPart] SET [Description]=\'{fun_description}\' WHERE [ID]={fun_id}'
            self.__c.execute(sql)
            self.__conn.commit()
            return fun_id

    def get_identical_description(self, filter_text):
        """
        根据所给的字符，获取同质单元的描述
        :param filter_text: 关键字
        :return:
        """
        sql = 'SELECT [ID], [Description] FROM [JJPart_IdenticalPart] ' \
              f'WHERE [Description] LIKE \'%{filter_text}%\' AND [StatusType]=100'
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        return r_s

    def replace_part_relation(self, relation_id, part_id):
        sql = f'UPDATE [JJPart_PartRelation] SET [ChildPart]={part_id} WHERE [PartRelationID]={relation_id}'
        self.__c.execute(sql)
        self.__conn.commit()

    def search_thr_erp_id(self, id_str: str, is_zd=True):
        id_seg = '[ErpId]' if is_zd else '[ErpCode]'
        table_name = '[JJPart_ZdErp]' if is_zd else '[JJPart_JlErp]'
        sql = f'SELECT * FROM {table_name} WHERE {id_seg} LIKE \'{id_str}%\' ORDER BY {id_seg}'
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        return r_s

    def search_thr_erp_description(self, des_str: str, is_zd=True):
        search_str = des_str.replace('*', '%')
        search_str = search_str.replace('?', '_')
        id_seg = '[ErpId]' if is_zd else '[ErpCode]'
        table_name = '[JJPart_ZdErp]' if is_zd else '[JJPart_JlErp]'
        if '%' not in search_str or '_' in search_str:
            search_str = f'%{search_str}%'
        sql = f'SELECT * FROM {table_name} WHERE [Description] LIKE \'{search_str}\' ORDER BY {id_seg}'
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        return r_s

    def update_zd_erp_foundation_info(self, _data):
        insert_c = 0
        update_c = 0
        no_c = 0
        for r in _data:
            erp_id = r[0]
            description = r[1]
            _unit = r[2]
            self.__c.execute(f'SELECT * FROM [JJPart_ZdErp] WHERE [ErpId]=\'{erp_id}\'')
            rs = self.__c.fetchall()
            if len(rs) > 0:
                if description != rs[0][1]:
                    self.__c.execute(
                        f'UPDATE [JJPart_ZdErp] SET [Description]=\'{description}\' WHERE [ErpId]=\'{erp_id}\'')
                    update_c += 1
                else:
                    no_c += 1
            else:
                self.__c.execute(f'INSERT INTO [JJPart_ZdErp] VALUES (\'{erp_id}\', \'{description}\', \'{_unit}\')')
                insert_c += 1
        self.__conn.commit()
        return f'新增{insert_c}个，更新{update_c}个，未处理{no_c}个。'

    def generate_a_image(self, part_id, ver=None):
        img_data = self.get_thumbnail_2_part(part_id, ver)
        if img_data is None:
            return None
        byte_stream = io.BytesIO(img_data)
        roiImage = Image.open(byte_stream)
        o_size = roiImage.size
        max_edge = max(o_size[0], o_size[1])
        scale_f = 200 / max_edge
        w = int(o_size[0] * scale_f)
        h = int(o_size[1] * scale_f)
        roiImage = roiImage.resize((w, h))
        imgByteArr = io.BytesIO()
        roiImage.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        target_file = '{0}\\{1:08d}.png'.format(tempfile.gettempdir(), part_id)
        with open(target_file, 'wb') as f:
            f.write(imgByteArr)
        f.close()
        return target_file

    def get_identical_parts(self, _id, mode=1, keep_original=False):
        """
        获取同质单元
        :param keep_original: 当 mode=1 时，是否保留原零件
        :param mode: 1=id 代表零件号，0=id代表功能号
        :param _id:
        :return: 当mode=1时，([PartID], (ID, Description, StatusType))；当mode≠1时，[PartID]
        """
        if mode == 1:
            sql = f'SELECT [FunctionID] FROM [JJPart_IdenticalPartLink] WHERE [Part]={_id}'
            self.__c.execute(sql)
            r_s = self.__c.fetchall()
            result = []
            if len(r_s) < 1:
                return None
            sql = f'SELECT * FROM [JJPart_IdenticalPart] WHERE [ID]={r_s[0][0]}'
            self.__c.execute(sql)
            fun_record = self.__c.fetchone()
            sql = f'SELECT [Part] FROM [JJPart_IdenticalPartLink] WHERE [FunctionID]={fun_record[0]} ORDER BY [Part]'
            self.__c.execute(sql)
            r_s = self.__c.fetchall()
            for r in r_s:
                if r[0] != _id or keep_original:
                    result.append(r[0])
            return result, (fun_record[0], fun_record[1], fun_record[2])
        else:
            sql = f'SELECT [Part] FROM [JJPart_IdenticalPartLink] WHERE [FunctionID]={_id} ORDER BY [Part]'
            self.__c.execute(sql)
            r_s = self.__c.fetchall()
            return r_s

    def clear_storing_position(self, storage_position):
        today = datetime.datetime.today()
        t_str = today.strftime('%Y-%m-%d')
        sql = f'UPDATE [JJStorage_Storing] ' \
              f'SET [Qty]=0.0, [LastRecordDate]=\'{t_str}\' WHERE [Position]=\'{storage_position}\''
        self.__c.execute(sql)
        self.__conn.commit()

    def update_part_storing(self, part_id, qty, storage_position, _date, unit_price):
        sql = f'SELECT [Qty] FROM [JJStorage_Storing] WHERE [PartId]={part_id} AND [Position]=\'{storage_position}\''
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        if len(r_s) < 1:
            sql = f'INSERT INTO [JJStorage_Storing] VALUES ' \
                  f'({part_id}, \'{storage_position}\', {qty}, \'{_date}\', {unit_price})'
        else:
            sql = f'UPDATE [JJStorage_Storing] SET [Qty]={qty}, [LastRecordDate]=\'{_date}\', UnitPrice={unit_price} ' \
                  f'WHERE [PartId]={part_id} AND [Position]=\'{storage_position}\''
        self.__c.execute(sql)
        self.__conn.commit()

    def remove_file_link_from_part(self, part_id, file_path):
        pass

    def get_database_type(self):
        return 'SQLite'

    def add_file_link_2_part(self, part_id, file_path):
        pass

    def set_part_hyper_link(self, part_id, the_link):
        if the_link is None or len(the_link.strip()) < 1:
            sql = f'DELETE FROM [JJCost_PurchaseLink] WHERE [PartId]={part_id}'
            self.__c.execute(sql)
            return
        sql = f'SELECT [HyperLink] FROM [JJCost_PurchaseLink] WHERE [PartId]={part_id}'
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            sql = f'INSERT INTO [JJCost_PurchaseLink] VALUES ({part_id}, \'{the_link}\')'
        else:
            sql = f'UPDATE [JJCost_PurchaseLink] SET [HyperLink]=\'{the_link}\' WHERE [PartId]={part_id}'
        self.__c.execute(sql)

    def get_part_hyper_link(self, part_id):
        sql = f'SELECT [HyperLink] FROM [JJCost_PurchaseLink] WHERE [PartId]={part_id}'
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs[0][0]

    def remove_part_relation(self, relation_id):
        """
        移除原先的关联
        :param relation_id: 关联ID
        :return:
        """
        sql = f'DELETE FROM [JJPart_PartRelation] WHERE [PartRelationID]={relation_id}'
        self.__c.execute(sql)

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
        self.__c.execute(sql)
        r = self.__c.fetchone()
        next_relation_id = r[0] + 1
        comment_4_sql = 'null'
        if relation_comment is not None and len(relation_comment) > 0:
            comment_4_sql = f'\'{relation_comment.strip()}\''
        if relation_id is None:
            sql = f'INSERT INTO [JJPart_PartRelation] VALUES ({next_relation_id}, {parent_id}, {child_id}, {sum_qty},' \
                  f' \'件\', {index_id}, {comment_4_sql}, {actual_qty}, 0)'
            self.__c.execute(sql)
        else:
            sql = f'UPDATE [JJPart_PartRelation] SET [Quantity]={sum_qty}, [Number]={index_id}, [Comment]={comment_4_sql},' \
                  f' [ActualQty]={actual_qty} WHERE [PartRelationID]={relation_id}'
            self.__c.execute(sql)

    def get_pick_material_record(self, begin_date, end_date):
        sql = 'SELECT r.[BillName], i.[ItemId], i.[PartId], i.[ErpId], r.[DoingDate], ' \
              'r.[DoneQty], r.[Comment], r.[Id] AS [RecordId] FROM [JJStorage_SupplyOperationRecord] AS r ' \
              'INNER JOIN [JJStorage_KbnSupplyItem] AS i ON r.[LinkItem]=i.[ItemId] ' \
              'WHERE r.[Process]=14'
        sql += f' AND r.[DoingDate]>=\'{begin_date}\' AND r.[DoingDate]<=\'{end_date}\''
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs

    def create_put_back_material_record(self, bill_name, operator, when, data):
        pass

    def cancel_material_requirement(self, item_id, cancel_qty, change_doing=False):
        sql = f'SELECT [DoneQty], [DoingQty] FROM [JJStorage_KbnSupplyItem] WHERE [ItemId]={item_id}'
        self.__c.execute(sql)
        r = self.__c.fetchone()
        doing_qty = float(r[1])
        update_doing_qty_str = ''
        if change_doing:
            update_doing_qty_str = f', [DoingQty]={doing_qty - cancel_qty} '
        all_done_qty = float(r[0]) + cancel_qty
        sql = f'UPDATE [JJStorage_KbnSupplyItem] SET [DoneQty]={all_done_qty}{update_doing_qty_str} ' \
              f'WHERE [ItemId]={item_id}'
        self.__c.execute(sql)
        self.__conn.commit()

    def cancel_supply_operation(self, record_id, cancel_qty):
        sql = f'SELECT [Done], [Qty], [DoneQty], [LinkItem] FROM [JJStorage_SupplyOperationRecord] WHERE [Id]={record_id}'
        self.__c.execute(sql)
        r = self.__c.fetchone()
        qty = float(r[1])
        done_qty = float(r[2])
        done_qty += cancel_qty
        done = 1 if done_qty >= qty else 0
        item_id = r[3]
        sql = f'UPDATE [JJStorage_SupplyOperationRecord] SET [Done]={done}, [DoneQty]={done_qty} WHERE [Id]={record_id}'
        self.__c.execute(sql)
        self.cancel_material_requirement(item_id, cancel_qty, change_doing=True)

    def set_part_thumbnail(self, part_id, image_data):
        get_version_sql = f'SELECT [Version] FROM [JJPart_PartThumbnail] ' \
                          f'WHERE [PartId]={part_id} ORDER BY [Version] DESC'
        self.__c.execute(get_version_sql)
        r = self.__c.fetchone()
        next_version = 1
        if r is not None:
            next_version += r[0]
        self.__c.execute('INSERT INTO [JJPart_PartThumbnail] ([PartID], [Thumbnail], [Version]) VALUES (?, ?, ?)',
                         (part_id, image_data, next_version))
        self.__conn.commit()

    def clean_part_thumbnail(self, part_id):
        delete_sql = f'DELETE FROM [JJPart_PartThumbnail] WHERE [PartId]={part_id}'
        self.__c.execute(delete_sql)
        self.__conn.commit()

    def get_last_supply_record_link(self, this_id):
        select_sql = f'SELECT [LastId] FROM [JJStorage_SupplyRecordLink] WHERE [ThisId]={this_id}'
        self.__c.execute(select_sql)
        r = self.__c.fetchone()
        return r[0]

    @staticmethod
    def __null_2_empty_in_list(the_original_list):
        """ 将列表中的 None 全部转换为 str.empty """
        the_result = []
        for s in the_original_list:
            if s is None:
                the_result.append('')
            else:
                the_result.append(s)
        return the_result

    def get_part_info_quick(self, part_id):
        sql = f'SELECT [name], [description], [brand], [standard], [foreign_code], [jl_erp_code], [comment], [type]' \
              f' FROM [JJPart_PartDetail2] WHERE [id]={part_id}'
        self.__c.execute(sql)
        one_row = self.__c.fetchone()
        if one_row is not None:
            temp = self.__null_2_empty_in_list(one_row)
            if len(temp[3]) < 1:
                description3 = f'{temp[2]} {temp[3]}'.strip()
            else:
                description3 = temp[2]
            result = temp[:2]
            result.append(description3)
            result.extend(temp[4:])
            return result
        else:
            return None

    def get_parts_by_config(self, part_id=None, name=None, english_name=None, description=None, column_config=None):
        if column_config[0] == 0:
            raise Exception('必须显示项目号或零件号！')
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
                   't9.[id]=pt9.[tag_id] AND t9.[parent_id]=2406) ON p.[PartID]=pt9.[part_id]'),
            2958: ('t10.[tag_name] AS storing ',
                   '([JJCom_Tag] AS t10 INNER JOIN [JJCom_PartTag] AS pt10 ON '
                   't10.[id]=pt10.[tag_id] AND t10.[parent_id]=2958) ON p.[PartID]=pt10.[part_id]'),
            4339: ('t11.[tag_name] AS jo_erp_code',
                   '([JJCom_Tag] AS t11 INNER JOIN [JJCom_PartTag] AS pt11 ON '
                   't11.[id]=pt11.[tag_id] AND t11.[parent_id]=4339) ON p.[PartID]=pt11.[part_id]')
        }
        the_display_columns = []
        from_tag_tables = []
        i = 0
        for c in column_config[0:5]:
            if c == 1:
                the_display_columns.append(default_segments[i])
            i += 1
        for c in column_config[5:-1]:
            the_display_columns.append(option_segments[c][0])
            from_tag_tables.append(option_segments[c][1])
        if column_config[-1] == 1:
            the_display_columns.append(default_segments[-1])
        if len(the_display_columns) < 1:
            raise Exception('没有选择要显示的字段！')
        select_cmd += ', '.join(the_display_columns)
        f_str = '(' if use_status else ''
        select_cmd += f' {f_str}FROM [JJPart_Part] AS p '
        if column_config[4] == 1:
            select_cmd += option_segments[0][1]
        if len(from_tag_tables) > 0:
            select_cmd += 'LEFT OUTER JOIN '
            from_tag_tables_str = ' LEFT OUTER JOIN '.join(from_tag_tables)
            select_cmd += from_tag_tables_str

        default_where = '(p.[StatusType]=90 OR p.[StatusType]=100)'
        if part_id is None and name is None and english_name is None and description is None:
            sql = '{0} WHERE {1} ORDER BY p.[PartID]'.format(select_cmd, default_where)
        elif part_id is not None:
            sql = '{0} WHERE {2} AND p.[PartID]={1}'.format(select_cmd, part_id, default_where)
        else:
            search_filter = ''
            if name is not None:
                search_filter += 'p.[Description1] LIKE \'%{0}%\''.format(name)
            if english_name is not None:
                if len(search_filter) > 0:
                    search_filter += ' AND '
                search_filter += 'p.[Description4] LIKE \'%{0}%\''.format(english_name)
            if description is not None:
                if len(search_filter) > 0:
                    search_filter += ' AND '
                search_filter += 'p.[Description2] LIKE \'%{0}%\''.format(description)
            sql = '{0} WHERE {1} AND {2} ORDER BY p.[PartID]'.format(select_cmd, search_filter, default_where)
        self.__c.execute(sql)
        temp = self.__c.fetchall()
        # 去除可能出现的重复
        result = {}
        for t in temp:
            _id = t[0]
            if _id in result:
                original_info = result[_id]
                c = len(original_info)
                for i in range(1, c):
                    c_i = t[i]
                    o_i = original_info[i]
                    original_info[i] = self.__combi(o_i, c_i)
                result[_id] = original_info
            else:
                result[_id] = list(t)
        return result

    def get_available_supply_operation_bill(self, prefix=None):
        sql = f'SELECT COUNT(*) FROM [JJStorage_OperationBill] WHERE [BillName] LIKE \'{prefix}%\''
        self.__c.execute(sql)
        c = self.__c.fetchone()[0]
        return f'{prefix}-{c + 1}'

    def select_process_data(self, process_type=1):
        if process_type == 1 or process_type == 2:
            sql = 'SELECT b.[BillName], i.[ItemId], i.[PartId], i.[ErpId], b.[BuildDate], i.[Qty], ' \
                  'i.[DoingQty], i.[DoneQty], i.[Comment] ' \
                  'FROM [JJStorage_KbnSupplyItem] AS i INNER JOIN [JJStorage_KbnSupplyBill] AS b ' \
                  'ON i.[BillName]=b.[BillName] WHERE i.[DoneQty]+i.[DoingQty]<i.[Qty] AND b.[BuildDate]>\'2020/1/1\''
            self.__c.execute(sql)
            r_s = self.__c.fetchall()
            count = len(r_s)
            if process_type == 1:
                return count, r_s
            else:
                # 进行数据的进一步筛选，筛选出来源是“自制”的零件
                result = []
                for i in r_s:
                    sql = f'SELECT * FROM [JJCom_PartTag] WHERE [part_id]={i[2]} AND [tag_id]=17'
                    self.__c.execute(sql)
                    t_s = self.__c.fetchall()
                    if len(t_s) > 0:
                        result.append(i)
                return len(result), result
        elif process_type == 3 or process_type == 4:
            process_id_str = 'WHERE r.[Done]<>1 AND r.[Qty]>r.[DoneQty] AND (r.[Process]=11 OR r.[Process]=12)'
            if process_type == 4:
                process_id_str = 'WHERE r.[Process]=13'
            sql = 'SELECT r.[BillName], i.[ItemId], i.[PartId], i.[ErpId], r.[DoingDate], r.[Qty], ' \
                  'r.[DoneQty], r.[Comment], i.[Comment], r.[Id] ' \
                  'FROM [JJStorage_SupplyOperationRecord] AS r INNER JOIN [JJStorage_KbnSupplyItem] AS i ' \
                  'ON r.[LinkItem]=i.[ItemId] '
            sql += process_id_str
            self.__c.execute(sql)
            r_s = self.__c.fetchall()
            count = len(r_s)
            result = []
            for r in r_s:
                new_row = list(r[:7])
                comment = r[7]
                comment_dict = {}
                if comment is None:
                    comment = ''
                else:
                    comment_dict = Com.str_2_dict(comment)
                    if 'Comment' in comment_dict:
                        comment = comment_dict['Comment']
                    else:
                        comment = ''
                if r[8] is not None and len(r[8]) > 0:
                    comment += f' {r[8]}'
                if len(comment) < 1:
                    comment = None
                new_row.extend([Decimal(0.0), comment, r[9]])
                # 获取入库记录时，要仓位和单价的信息
                if process_type == 4:
                    pos = '' if not ('Position' in comment_dict) else comment_dict['Position']
                    u_price = '' if not ('UnitPrice' in comment_dict) else comment_dict['UnitPrice']
                    new_row.extend([pos, u_price])
                result.append(new_row)
            return count, result

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
            bill_name = '{0}{1}'.format(pre_fix, bill_name)
            sql = f'SELECT COUNT(*) FROM [JJStorage_OperationBill] WHERE [BillName] LIKE \'{bill_name}%\''
            self.__c.execute(sql)
            c = self.__c.fetchone()[0]
            bill_name += f'-{c + 1}'
            operator = data['Operator']
            doing_date = data['DoingDate']
            insert_bill_sql = f'INSERT INTO [JJStorage_OperationBill] VALUES (\'{bill_name}\', \'{operator}\', ' \
                              f'\'{doing_date}\', \'{bill_type}\', 0)'
            self.__c.execute(insert_bill_sql)
            self.__c.execute('SELECT MAX([Id]) FROM [JJStorage_SupplyOperationRecord]')
            temp_r = self.__c.fetchone()[0]
            if temp_r is None:
                next_id = 1
            else:
                next_id = temp_r + 1
            items = data['Items']
            for item in items:
                if item[2] is None or len(item[2]) < 1:
                    comment = 'null'
                else:
                    comment = {'Comment': item[2]}
                if bill_type == '入库单':
                    # 建立入库单时，在comment，补充仓位和单价的信息
                    if type(comment) == str:
                        comment = {}
                    comment['Position'] = item[4]
                    if item[5] is not None:
                        comment['UnitPrice'] = '%.3f' % item[5]
                if type(comment) == dict:
                    comment = '\'{0}\''.format(Com.dict_2_str(comment))
                done_qty = 0.0 if bill_type != '入库单' else item[1]
                is_done = 0 if bill_type != '入库单' else 1
                insert_item_sql = f'INSERT INTO [JJStorage_SupplyOperationRecord] VALUES ({next_id}, {is_done}, ' \
                                  f'\'{doing_date}\', \'{operator}\', {next_process}, {item[0]}, {item[1]}, ' \
                                  f'\'{bill_name}\', {done_qty}, {comment})'
                self.__c.execute(insert_item_sql)
                # 建立 supply operation 的链接
                last_supply_record = None
                if bill_type == '入库单':
                    last_supply_record = item[3]
                    if next_process == 15:  # 退库单则需要绑定再上一级的记录
                        update_o_link = f'UPDATE [JJStorage_SupplyOperationRecord] SET [Process]=15 ' \
                                        f'WHERE [Id]={item[3]}'
                        self.__c.execute(update_o_link)
                        last_supply_record = self.get_last_supply_record_link(last_supply_record)
                    insert_item_sql = f'INSERT INTO [JJStorage_SupplyRecordLink] VALUES ' \
                                      f'({next_id}, {last_supply_record})'
                    self.__c.execute(insert_item_sql)
                get_link_item_info = f'SELECT [Qty], [DoingQty], [DoneQty], [PartId] FROM [JJStorage_KbnSupplyItem] ' \
                                     f'WHERE [ItemId]={item[0]}'
                self.__c.execute(get_link_item_info)
                qty_info = self.__c.fetchone()
                part_id = qty_info[3]
                if bill_type == '投料单' or bill_type == '派工单':
                    update_link_item = f'UPDATE [JJStorage_KbnSupplyItem] ' \
                                       f'SET [DoingQty]={float(qty_info[1]) + item[1]} ' \
                                       f'WHERE [ItemId]={item[0]}'
                    self.__c.execute(update_link_item)
                else:
                    # 更新需求数据
                    required_doing_qty = float(qty_info[1]) - item[1]
                    required_done_qty = float(qty_info[2]) + item[1]
                    update_link_item = f'UPDATE [JJStorage_KbnSupplyItem] SET [DoingQty]={required_doing_qty}, ' \
                                       f'[DoneQty]={required_done_qty} WHERE [ItemId]={item[0]}'
                    self.__c.execute(update_link_item)
                    # 更新上一个操作的数据
                    get_operation_info_sql = f'SELECT [Qty], [DoneQty] FROM [JJStorage_SupplyOperationRecord] ' \
                                             f'WHERE [Id]={item[3]}'
                    self.__c.execute(get_operation_info_sql)
                    last_operation_info = self.__c.fetchone()
                    operation_done_qty = float(last_operation_info[1]) + item[1]
                    if operation_done_qty >= last_operation_info[0]:
                        additional_update = ', [Done]=1 '
                    else:
                        additional_update = ', [Done]=0 '
                    update_last_operation = f'UPDATE [JJStorage_SupplyOperationRecord] ' \
                                            f'SET [DoneQty]={operation_done_qty}{additional_update} ' \
                                            f'WHERE [Id]={last_supply_record}'
                    self.__c.execute(update_last_operation)
                    # 更新仓储数据
                    get_storing_info_sql = f'SELECT * FROM [JJStorage_Storing] ' \
                                           f'WHERE [PartId]={part_id} AND [Position]=\'{item[4]}\''
                    self.__c.execute(get_storing_info_sql)
                    r_s = self.__c.fetchall()
                    if len(r_s) < 1:
                        if item[5] is None:
                            unit_price = 'null'
                        else:
                            unit_price = '{0}'.format(item[5])
                        insert_new_storing = f'INSERT INTO [JJStorage_Storing] ' \
                                             f'VALUES ({part_id}, \'{item[4]}\', {item[1]}, ' \
                                             f'\'{doing_date}\', {unit_price})'
                        self.__c.execute(insert_new_storing)
                    else:
                        # 不同仓位的价格可能不同
                        qty_sum = 0.0
                        for r in r_s:
                            qty_sum += r[2]
                        current_price = r_s[0][4]
                        neu_unit_price = None
                        if current_price is None:
                            if item[5] is not None:
                                neu_unit_price = '{0}'.format(item[5])
                        else:
                            original_price_sum = qty_sum * float(current_price)
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
                            unit_price_str = '{0}'.format(neu_unit_price)
                        update_new_storing = f'UPDATE [JJStorage_Storing] SET ' \
                                             f'[Qty]={qty_sum + item[1]}, [LastRecordDate]=\'{doing_date}\', ' \
                                             f'[UnitPrice]={unit_price_str} ' \
                                             f'WHERE [PartId]={part_id} AND [Position]=\'{item[4]}\''
                        self.__c.execute(update_new_storing)
                next_id += 1
            self.__conn.commit()
            return bill_name
        except Exception as e:
            self.__conn.rollback()
            raise e

    def create_picking_record(self, data, mark):
        """
        创建出库记录
        :param mark: {}，里面包括：record - int
        :param data:[]，里面包括：BillName - str, Operator - str, DoingDate - str, BillType - str, FromStorage - str,
        Items - [Contract - str, PartId - int, ErpId - str, Qty - float, RecordIndex - int]
        :return:
        """
        # TODO 参考 MssqlHandler 的方式进行修改
        bill_name = data[0]
        operator = data[1]
        the_date = data[2]
        bill_type = data[3]
        from_storage = data[4]
        current_process = 14
        except_type = 0  # 异常级别：0-询问解决、1-报警（无法解决）
        record_index = None
        try:
            insert_require_bill_sql = f'INSERT INTO [JJStorage_KbnSupplyBill] VALUES (\'{bill_name}\', \'{the_date}\', ' \
                                      f'\'{operator}\')'
            self.__c.execute(insert_require_bill_sql)
            insert_operation_bill_sql = f'INSERT INTO [JJStorage_OperationBill] VALUES (\'{bill_name}\', \'{operator}\', ' \
                                        f'\'{the_date}\', \'{bill_type}\', 0)'
            self.__c.execute(insert_operation_bill_sql)

            self.__c.execute('SELECT MAX([Id]) FROM [JJStorage_SupplyOperationRecord]')
            temp_r = self.__c.fetchone()[0]
            if temp_r is None:
                next_operation_id = 1
            else:
                next_operation_id = temp_r + 1
            self.__c.execute('SELECT MAX([ItemId]) FROM [JJStorage_KbnSupplyItem]')
            temp_r = self.__c.fetchone()[0]
            if temp_r is None:
                next_require_id = 1
            else:
                next_require_id = temp_r + 1
            for item in data[5]:
                actual_storage = from_storage
                record_index = item[4]
                # unit_price = None
                qty_need = item[3]  # 当前所需的数量
                while True:
                    if record_index in mark and mark[record_index] == 0:
                        actual_storage = 'X'
                    if actual_storage != 'X':
                        # 获取库存信息
                        get_storing = f'SELECT [Position], [Qty], [UnitPrice] FROM [JJStorage_Storing] ' \
                                      f'WHERE [PartId]={item[1]} ORDER BY [Position]'
                        self.__c.execute(get_storing)
                        rs = self.__c.fetchall()
                        if len(rs) < 1:
                            # 完全没有记录
                            except_type = 0
                            raise Exception(f'{item[1]:0>8} 没有相应的库存，是否直接打印？')
                        qty_sum = 0.0
                        rr = []  # real_record, only D or E
                        if actual_storage == 'F':
                            for r in rs:
                                if r[0] == 'F':
                                    rr.append(r)
                        elif actual_storage == 'A':
                            for r in rs:
                                if r[0] == 'A':
                                    rr.append(r)
                        else:
                            for r in rs:
                                if r[0] == 'D' or r[0] == 'E':
                                    rr.append(r)
                        for r in rr:
                            qty_sum += r[1]
                        if qty_sum >= qty_need:
                            # 整体数量是足够的
                            remain_qty = qty_need
                            for r in rr:
                                if remain_qty <= 0.0:
                                    break
                                if remain_qty > r[1]:
                                    q = r[1]
                                else:
                                    q = remain_qty
                                remain_qty -= q
                                if q <= 0.0:
                                    continue
                                # 更新仓库库存
                                update_storing = f'UPDATE [JJStorage_Storing] ' \
                                                 f'SET [Qty]={r[1] - q}, [LastRecordDate]=\'{the_date}\' ' \
                                                 f'WHERE [PartId]={item[1]} AND [Position]=\'{r[0]}\''
                                self.__c.execute(update_storing)
                                # 创建需求记录
                                comment_dict = {'FromStorage': r[0], 'Contract': item[0]}
                                unit_price = r[2]
                                if unit_price is not None:
                                    comment_dict['Price'] = '%.2f' % (qty_need * float(unit_price))
                                insert_require_item = f'INSERT INTO [JJStorage_KbnSupplyItem] VALUES ({next_require_id}, ' \
                                                      f'\'{bill_name}\', {item[1]}, {q}, 0.0, {q}, \'{item[2]}\', ' \
                                                      f'null, null)'
                                self.__c.execute(insert_require_item)
                                # 创建操作记录
                                comment_str = Com.dict_2_str(comment_dict)
                                insert_operation_item = f'INSERT INTO [JJStorage_SupplyOperationRecord] VALUES ({next_operation_id}, ' \
                                                        f'1, \'{the_date}\', \'{operator}\', {current_process}, {next_require_id}, ' \
                                                        f'{q}, \'{bill_name}\', {q}, \'{comment_str}\')'
                                self.__c.execute(insert_operation_item)
                                next_require_id += 1
                                next_operation_id += 1
                        else:
                            # 整体数量不足
                            except_type = 1
                            raise Exception(f'{item[1]:0>8} 库存不足，须修改领料数量！')
                    else:
                        # 创建需求记录
                        comment_dict = {'FromStorage': actual_storage, 'Contract': item[0]}
                        insert_require_item = f'INSERT INTO [JJStorage_KbnSupplyItem] VALUES ({next_require_id}, ' \
                                              f'\'{bill_name}\', {item[1]}, {qty_need}, 0.0, {qty_need}, \'{item[2]}\', ' \
                                              f'null, null)'
                        self.__c.execute(insert_require_item)
                        # 创建操作记录
                        comment_str = Com.dict_2_str(comment_dict)
                        insert_operation_item = f'INSERT INTO [JJStorage_SupplyOperationRecord] VALUES ({next_operation_id}, ' \
                                                f'1, \'{the_date}\', \'{operator}\', {current_process}, {next_require_id}, ' \
                                                f'{qty_need}, \'{bill_name}\', {qty_need}, \'{comment_str}\')'
                        self.__c.execute(insert_operation_item)
                        next_require_id += 1
                        next_operation_id += 1
                    break
            self.__conn.commit()
            return None
        except Exception as e:
            self.__conn.rollback()
            return except_type, str(e), record_index

    def next_available_part_id(self):
        sql = 'SELECT [PartID] FROM [JJPart_Part] WHERE [StatusType]=10'
        self.__c.execute(sql)
        r = self.__c.fetchone()
        if r is not None:
            sql = f'UPDATE [JJPart_Part] SET [StatusType]=20 WHERE [PartID]={r[0]}'
            self.__c.execute(sql)
            return r[0]
        get_max_id = f'SELECT MAX([PartID]) FROM [JJPart_Part]'
        self.__c.execute(get_max_id)
        r = self.__c.fetchone()
        next_id = r[0] + 1
        temp_create_part = f'INSERT INTO [JJPart_Part] VALUES ({next_id}, 20, null, \'dummy\', ' \
                           f'null, null, \'dummy\', null, null, null, null)'
        self.__c.execute(temp_create_part)
        self.__conn.commit()
        return next_id

    def set_part_id_2_prepared(self, part_id):
        sql = f'UPDATE [JJPart_Part] SET [StatusType]=10 WHERE [PartID]={part_id}'
        self.__c.execute(sql)
        self.__conn.commit()

    @staticmethod
    def __evaluate_str(ss):
        if ss is None:
            return 'NULL'
        if type(ss) != str:
            raise TypeError('Type is not str.')
        if len(ss) < 1:
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
        if (o_i == c_i) or (c_i is None or len(c_i) < 1):
            return o_i
        if o_i is None or len(o_i) < 1:
            return c_i
        return f'{o_i}, {c_i}'

    def create_a_new_part(self, part_id, name, english_name, description, comment, tag_dict):
        real_description = SqliteHandler.__evaluate_str(description)
        real_comment = SqliteHandler.__evaluate_str(comment)
        # 创建单元
        create_sql = f'UPDATE [JJPart_Part] SET [StatusType]=100, [Description1]=\'{name}\', ' \
                     f'[Description2]={real_description}, [Description4]=\'{english_name}\', ' \
                     f'[Comment]={real_comment} WHERE [PartID]={part_id}'
        self.__c.execute(create_sql)
        self.__conn.commit()
        # 创建标签
        for k in tag_dict:
            tag_list = self.get_tags(name=k)
            if len(tag_list) > 0:
                parent_tag_id = tag_list[0][0]
            else:
                raise Exception('没有所填写的父标签值。')
            tag_list = self.get_tags(name=tag_dict[k], parent_id=parent_tag_id)
            if len(tag_list) < 1:
                tag_id = self.create_one_tag(tag_dict[k], parent_tag_id)
            else:
                tag_id = tag_list[0][0]
            self.set_tag_2_part(tag_id, part_id)
            if k == '类别':
                get_type_sql = f'SELECT [ID], [GroupNr] FROM [JJPart_PartType] WHERE [TypeName]=\'{tag_dict[k]}\''
                self.__c.execute(get_type_sql)
                r = self.__c.fetchone()
                group_c = f'{r[1]:02d}0'
                update_part_type = f'UPDATE [JJPart_Part] SET [PartType]={r[0]}, [PartGroup]=\'{group_c}\' ' \
                                   f'WHERE [PartID]={part_id}'
                self.__c.execute(update_part_type)
                self.__conn.commit()
            elif k == '品牌' or k == '标准':
                get_description3 = f'SELECT [Description3] FROM [JJPart_Part] WHERE [PartID]={part_id}'
                self.__c.execute(get_description3)
                des3 = self.__c.fetchone()[0]
                if des3 is None:
                    current_des3 = tag_dict[k]
                else:
                    tt = des3.strip()
                    if len(tt) < 1:
                        current_des3 = tag_dict[k]
                    else:
                        current_des3 = f'{tt} {tag_dict[k]}'
                update_part_description3 = f'UPDATE [JJPart_Part] SET [Description3]=\'{current_des3}\' ' \
                                           f'WHERE [PartID]={part_id}'
                self.__c.execute(update_part_description3)
                self.__conn.commit()

    def update_part_info(self, part_id, name, english_name, description, comment):
        if len(description) < 1:
            real_description = 'null'
        else:
            real_description = f'\'{description}\''
        if len(comment) < 1:
            real_comment = 'null'
        else:
            real_comment = f'\'{comment}\''
        # 更新单元
        create_sql = f'UPDATE [JJPart_Part] SET [Description1]=\'{name}\', [Description2]={real_description},' \
                     f' [Description4]=\'{english_name}\', [Comment]={real_comment} WHERE [PartID]={part_id}'
        self.__c.execute(create_sql)
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
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        if len(r_s) < 1:
            return None
        else:
            return r_s

    def get_erp_info(self, erp_code, jl_erp=False):
        table_name = 'JJPart_ZdErp' if not jl_erp else 'JJPart_JlErp'
        column_name = 'ErpId' if not jl_erp else 'ErpCode'
        sql = f'SELECT * FROM [{table_name}] WHERE [{column_name}]=\'{erp_code}\''
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        if len(r_s) < 1:
            return None
        return r_s[0][0], r_s[0][1], r_s[0][2]

    def get_products_by_id(self, product_id):
        self.__c.execute('SELECT * FROM [JJProduce_Product] WHERE [ProductId]=\'{0}\''.format(product_id))
        return self.__c.fetchall()

    def get_all_storing_position(self):
        sql = 'SELECT DISTINCT([Position]) FROM [JJStorage_Storing] ORDER BY [Position]'
        self.__c.execute(sql)
        r_s = self.__c.fetchall()
        result = []
        for r in r_s:
            result.append(r[0])
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
                c = len(position)
                for i in range(c):
                    if i > 0:
                        sql += ' OR'
                    sql += f' [Position]=\'{position[i]}\''
        self.__c.execute(sql)
        r = self.__c.fetchall()
        if len(r) < 1:
            return None
        return r

    def del_tag_from_part(self, tag_id, part_id):
        sql = 'DELETE FROM [JJCom_PartTag] WHERE [tag_id]={0} AND [part_id]={1}'.format(tag_id, part_id)
        self.__c.execute(sql)
        self.__conn.commit()

    def del_one_tag(self, tag_id):
        del_link_sql = 'DELETE FROM [JJCom_PartTag] WHERE [tag_id]={0}'.format(tag_id)
        self.__c.execute(del_link_sql)
        del_tag_sql = 'DELETE FROM [JJCom_Tag] WHERE [id]={0}'.format(tag_id)
        self.__c.execute(del_tag_sql)
        self.__conn.commit()

    def rename_one_tag(self, tag_id, tag_name):
        update_tag_sql = 'UPDATE [JJCom_Tag] SET [tag_name]=\'{0}\' WHERE [id]={1}'.format(tag_name, tag_id)
        self.__c.execute(update_tag_sql)
        self.__conn.commit()

    def set_tag_2_part(self, tag_id, part_id):
        check_tag_link = 'SELECT [part_id] FROM [JJCom_PartTag] WHERE [part_id]={0} AND [tag_id]={1}'.format(part_id,
                                                                                                             tag_id)
        self.__c.execute(check_tag_link)
        if len(self.__c.fetchall()) > 0:
            return False
        insert_tag_link = 'INSERT INTO [JJCom_PartTag] VALUES ({0}, {1})'.format(part_id, tag_id)
        self.__c.execute(insert_tag_link)
        self.__conn.commit()
        return True

    def copy(self):
        return 'SQLite3', SqliteHandler(database_file=self.__db_file, copy=True, conn=self.__conn)

    def create_one_tag(self, name, parent_id):
        tag_count = 'SELECT MAX([id]) FROM [JJCom_Tag]'
        self.__c.execute(tag_count)
        next_id = self.__c.fetchone()[0] + 1
        if parent_id is None:
            sort_count = 'SELECT MAX([sort_index]) FROM [JJCom_Tag] WHERE [parent_id] IS NULL'
            self.__c.execute(sort_count)
            next_sort_index = self.__c.fetchone()[0] + 1
            insert_sql = 'INSERT INTO [JJCom_Tag] VALUES ({0}, \'{1}\', NULL, {2})'.format(next_id, name,
                                                                                           next_sort_index)
        else:
            sort_count = 'SELECT MAX([sort_index]) FROM [JJCom_Tag] WHERE [parent_id]={0}'.format(parent_id)
            self.__c.execute(sort_count)
            the_sort = self.__c.fetchone()[0]
            if the_sort is None:
                next_sort_index = 1
            else:
                next_sort_index = the_sort + 1
            insert_sql = 'INSERT INTO [JJCom_Tag] VALUES ({0}, \'{1}\', {2}, {3})'.format(next_id, name,
                                                                                          parent_id, next_sort_index)
        self.__c.execute(insert_sql)
        self.__conn.commit()
        return next_id

    def save_change(self):
        if self.__conn is not None:
            self.__conn.commit()

    def get_tags_2_part(self, part_id):
        sql = 'SELECT t.[id], t.[tag_name], t.[parent_id], t.[sort_index] ' \
              'FROM [JJCom_Tag] AS t INNER JOIN [JJCom_PartTag] AS p ON t.[id]=p.[tag_id] ' \
              'WHERE p.[part_id]={0}'.format(part_id)
        self.__c.execute(sql)
        return self.__c.fetchall()

    def get_tag_id(self, name, parent_name=None):
        """
        获取给定名称的tag的id，以便于进一步判断
        :param name:
        :param parent_name:
        :return: int or None
        """
        if parent_name is None:
            sql = f'SELECT [id] FROM [JJCom_Tag] WHERE [tag_name]=\'{name}\' AND [parent_id] IS NULL'
            self.__c.execute(sql)
            r = self.__c.fetchone()
            if r is None:
                return None
            else:
                return r[0]
        sql = f'SELECT [id] FROM [JJCom_Tag] WHERE [tag_name]=\'{parent_name}\' AND [parent_id] IS NULL'
        self.__c.execute(sql)
        r = self.__c.fetchone()
        if r is None:
            return None
        parent_id = r[0]
        sql = f'SELECT [id] FROM [JJCom_Tag] WHERE [tag_name]=\'{name}\' AND [parent_id]={parent_id}'
        self.__c.execute(sql)
        r = self.__c.fetchone()
        if r is None:
            return None
        return r[0]

    def get_parts_2_tag(self, tag_id):
        sql = 'SELECT [id], [name], [english_name], [description], [status], [comment] ' \
              'FROM [JJPart_PartTagView] WHERE [tag_id]={0}'.format(tag_id)
        self.__c.execute(sql)
        return self.__c.fetchall()

    def get_tags(self, tag_id=None, name=None, parent_id=None):
        if tag_id is None and name is None and parent_id is None:
            # 找出没有父标签的标签
            sql = 'SELECT * FROM [JJCom_Tag] WHERE [parent_id] IS NULL AND [id] > 0 ORDER BY [sort_index]'
        else:
            sql = 'SELECT * FROM [JJCom_Tag] WHERE'
            factor = False
            if tag_id is not None:
                sql = '{1} [id]={0}'.format(tag_id, sql)
                factor = True
            if name is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} [tag_name] LIKE \'%{0}%\''.format(name, sql)
                factor = True
            if parent_id is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} [parent_id]={0}'.format(parent_id, sql)
            sql += ' ORDER BY [sort_index], [id]'
        self.__c.execute(sql)
        return self.__c.fetchall()

    def __init__(self, database_file, copy=False, conn=None):
        self.__db_file = database_file
        # 为解决多线程的问题
        if not copy:
            self.__conn = sqlite3.connect(database_file, check_same_thread=False)
        else:
            self.__conn = conn
        # 此处会导致 auto-commit，去除 2022-12-04
        # self.__conn.isolation_level = None
        self.__conn.row_factory = sqlite3.Row
        self.__c = self.__conn.cursor()

    def get_parts(self, part_id=None, name=None, english_name=None, description=None):
        select_cmd = 'SELECT t.[PartID] AS id, t.[Description1] AS name, t.[Description4] AS english_name,' \
                     ' t.[Description2] AS description, s.[StatusDescription] AS status, t.[Comment] AS comment'
        from_database = 'FROM [JJPart_Part] AS t INNER JOIN [JJPart_PartStatus] AS s ON t.[StatusType]=s.[StatusID]'
        default_where = '(t.[StatusType]=90 OR t.[StatusType]=100)'
        if part_id is None and name is None and english_name is None and description is None:
            sql = '{0} {1} WHERE {2} ORDER BY t.[PartID]'.format(select_cmd, from_database, default_where)
        elif part_id is not None:
            sql = '{0} {1} WHERE {3} AND t.[PartID]={2}'.format(select_cmd, from_database, part_id, default_where)
        else:
            search_filter = ''
            if name is not None:
                search_filter += 't.[Description1] LIKE \'%{0}%\''.format(name)
            if english_name is not None:
                if len(search_filter) > 0:
                    search_filter += ' AND '
                search_filter += 't.[Description4] LIKE \'%{0}%\''.format(english_name)
            if description is not None:
                if len(search_filter) > 0:
                    search_filter += ' AND '
                search_filter += 't.[Description2] LIKE \'%{0}%\''.format(description)
            sql = '{1} {2} WHERE {3} AND {0} ORDER BY t.[PartID]'.format(search_filter, select_cmd,
                                                                         from_database, default_where)
        self.__c.execute(sql)
        return self.__c.fetchall()

    def get_files_2_part(self, part_id):
        sql = 'SELECT [FilePath] FROM [JJPart_FileRelation] WHERE [PartID]={0}'.format(part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append(r[0])
        return result

    def get_thumbnail_2_part(self, part_id, ver=None):
        sql = 'SELECT [Thumbnail], [Version] FROM [JJPart_PartThumbnail] ' \
              'WHERE [PartId]={0} ORDER BY [Version] DESC'.format(part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs[0][0]

    def get_children(self, part_id):
        sql = 'SELECT [Number] AS relation_index, [PartID] AS id, [Description1] AS name,' \
              ' [Description4] AS english_name, [StatusType] AS status, [Description2] AS description,' \
              ' [Comment] AS comment, [Quantity] AS qty_1,' \
              ' [ActualQty] AS qty_2, [PartRelationID] AS relation_id FROM [JJPart_ChildParts] ' \
              'WHERE [ParentPart]={0} ORDER BY [Number]'.format(part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs

    def get_parents(self, part_id):
        sql = 'SELECT b.[Number], b.[ParentPart], a.[Description1], a.[Description4], c.[StatusDescription],' \
              ' a.[Description2], b.[Comment], b.[Quantity], b.[ActualQty], b.[PartRelationID]' \
              ' FROM [JJPart_PartRelation] AS b INNER JOIN ([JJPart_Part] AS a' \
              ' INNER JOIN [JJPart_PartStatus] AS c ON a.[StatusType]=c.[StatusID])' \
              ' ON b.[ParentPart]=a.[PartID]' \
              ' WHERE b.[ChildPart]={0}' \
              ' ORDER BY b.[ParentPart], b.[PartRelationID]'.format(part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs

    def get_sub_tag_by_part_and_tag_name(self, part_id, tag_name):
        tt = self.get_tags(name=tag_name)
        if len(tt) < 1:
            return None
        sql = 'SELECT t.[tag_name] ' \
              'FROM [JJCom_Tag] AS t INNER JOIN [JJCom_PartTag] AS p ON t.[id]=p.[tag_id] ' \
              'WHERE t.[parent_id]={0} AND p.[part_id]={1}'.format(tt[0][0], part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        temp = []
        for r in rs:
            temp.append(r[0])
        return ','.join(temp)

    def close(self):
        try:
            if self.__c is not None:
                self.__c.close()
            if self.__conn is not None:
                self.__conn.close()
        except Exception as ex:
            print(f'Close Database Error: {ex}')

    def sort_one_tag_to_index(self, tag_id, target_index):
        sql = 'UPDATE [JJCom_Tag] SET [sort_index]={0} WHERE [id]={1}'.format(target_index, tag_id)
        self.__c.execute(sql)

    def set_tag_parent(self, tag_id, parent_id):
        if parent_id is not None:
            sql = 'UPDATE [JJCom_Tag] SET [parent_id]={0} WHERE [id]={1}'.format(parent_id, tag_id)
        else:
            sql = 'UPDATE [JJCom_Tag] SET [parent_id]=NULL WHERE [id]={0}'.format(tag_id)
        self.__c.execute(sql)

    def get_pick_record_throw_erp(self, erp_id, which_company=1, top=2):
        """ 获取巨轮智能的ERP领料记录 """
        sql_top = ''
        if top > 0:
            sql_top = ' LIMIT 0,{0}'.format(top)
        sql = 'SELECT [BillNumber], [Qty], [Price], [PickDate] ' \
              'FROM [JJStorage_ErpPickingRecord] WHERE [PartNumber]=\'{0}\' ' \
              'AND [PickDate] > \'2018-1-1\' ORDER BY [PickDate] DESC{1}'.format(erp_id, sql_top)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            sql = 'SELECT [BillNumber], [Qty], [Price], [PickDate] ' \
                  'FROM [JJStorage_ErpPickingRecord] WHERE [PartNumber]=\'{0}\' ' \
                  'ORDER BY [PickDate] DESC{1}'.format(erp_id, sql_top)
            self.__c.execute(sql)
            rs = self.__c.fetchall()
            if len(rs) < 1:
                return None
            else:
                return rs
        return rs

    def get_price_from_self_record(self, part_id, top=2):
        """ 获取本系统的价格记录信息 """
        sql_top = ''
        sql_top_1 = ''
        if top > 0:
            sql_top = ' ORDER BY [PartId], [Position] LIMIT 0,{0}'.format(top)
            sql_top_1 = ' LIMIT 0,{0}'.format(top)
        # 首先，从仓储数据进行检查
        sql = f'SELECT [UnitPrice], [Qty], [LastRecordDate] FROM [JJStorage_Storing] ' \
              f'WHERE [PartId]={part_id}{sql_top}'
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) > 0:
            result = []
            for r in rs:
                if r[0] is not None and r[0] > 0.0:
                    fade_qty = Decimal.from_float(r[1]) if type(r[1]) == float else r[1]
                    if fade_qty <= 0.001:
                        fade_qty = Decimal(1.0)
                    t0 = Decimal.from_float(r[0]) if type(r[0]) == float else r[0]
                    one_r = [0, t0 * fade_qty, Decimal.from_float(0.0), Decimal.from_float(0.0),
                             fade_qty, r[2], '库存']
                    result.append(one_r)
            if len(result) > 0:
                return result
        sql = 'SELECT i.[ListID], i.[PriceWithTax], i.[OtherCost], l.[TaxRate], ' \
              'i.[Amount], l.[QuotedDate], s.[Name] FROM ' \
              '[JJCost_QuotationItem] AS i INNER JOIN [JJCost_Quotation] AS l ON i.[ListID]=l.[QuotationID] ' \
              'INNER JOIN [JJCost_Supplier] AS s ON l.[SupplierID]=s.[SupplierID] ' \
              'WHERE [PartID]={0} ORDER BY l.[QuotedDate] DESC{1}'.format(part_id, sql_top_1)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs

    def get_erp_data(self, erp_code):
        sql = f'SELECT [ErpId], [Description], [Unit] FROM [JJPart_ZdErp] WHERE [ErpId]=\'{erp_code}\''
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return erp_code, '', ''
        return rs[0]
