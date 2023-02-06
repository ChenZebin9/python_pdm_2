""" 一些基础的数据类 """
import os.path
from decimal import Decimal
import datetime

from PyQt5.QtCore import (QThread, pyqtSignal, Qt)
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from db.DatabaseHandler import DatabaseHandler


class Part:
    """ 代表一个Item """

    def __init__(self, part_id, name, english_name, status, description=None, comment=None):
        self.__part_id = part_id
        self.part_id = '{:08d}'.format( part_id )
        self.name = name
        self.english_name = english_name
        self.status = status
        self.description = description
        self.comment = comment
        self.tags = []

        # 仓储的相关数据
        self.position: str = ''
        self.qty: float = 0.0
        self.last_storing_date: datetime = None
        self.unit_price: Decimal = Decimal.from_float( 0.0 )

    @staticmethod
    def get_parts(database, part_id=None, name=None, english_name=None, description=None):
        rs = database.get_parts( part_id, name, english_name, description )
        result = []
        for r in rs:
            p = Part( r[0], r[1], r[2], r[4], description=r[3], comment=r[5] )
            result.append( p )
        return result

    @staticmethod
    def get_parts_from_tag(database, tag_id):
        rs = database.get_parts_2_tag( tag_id )
        result = []
        for r in rs:
            p = Part( r[0], r[1], r[2], r[4], description=r[3], comment=r[5] )
            result.append( p )
        return result

    @staticmethod
    def get_unit_price(database: DatabaseHandler, part_id):
        # 查找库存里的数据
        storing_data = database.get_storing( part_id )
        if storing_data is not None:
            pos_list = ('D', 'E', 'F', 'A')  # 以此顺序进行查询
            for p in pos_list:
                for s in storing_data:
                    if s[1] == p and s[4] is not None and s[4] > 0.0001:
                        return float( s[4] )
        # 通过领料记录来查询数据
        """
        p_obj = Part.get_parts( database, part_id=part_id )
        if len( p_obj ) >= 1:
            p = p_obj[0]
            erp_nr = p.get_specified_tag( database, '巨轮智能ERP物料编码' )
            if len( erp_nr ) > 0:
                erp_pick_records = database.get_pick_record_throw_erp( erp_nr, top=0 )
                if erp_pick_records is not None:
                    all_price = 0.0
                    all_qty = 0.0
                    for r in erp_pick_records:
                        all_price += float( r[2] )
                        all_qty += float( r[1] )
                    if all_qty <= 0.0:
                        return 0.0
                    return float( all_price / all_qty )
        """
        # 通过PDM的记录来查询数据
        pdm_records = database.get_price_from_self_record( part_id=part_id, top=1 )
        if pdm_records is not None:
            r = pdm_records[0]
            f1 = Decimal.from_float( r[1] ) if type( r[1] ) == float else r[1]
            f2 = Decimal.from_float( r[2] ) if type( r[2] ) == float else r[2]
            f3 = Decimal.from_float( r[3] ) if type( r[3] ) == float else r[3]
            f4 = Decimal.from_float( r[4] ) if type( r[4] ) == float else r[4]
            price = (f1 + f2) / (Decimal.from_float( 1.0 ) + f3) / f4
            return float( price )
        return float( 0.0 )

    def get_tags(self, database):
        rr = database.get_tags_2_part( self.__part_id )
        for r in rr:
            t = Tag( r[0], r[1], r[2], r[3], database=database )
            self.tags.append( t )

    def get_tags_id(self, database):
        """
        获取tag零件的所有id
        :param database:
        :return:
        """
        result = []
        rr = database.get_tags_2_part( self.__part_id )
        for r in rr:
            result.append( r[0] )
        return result

    def get_specified_tag(self, database, tag_name):
        """ 根据给定的tag名称，查找其子tag所指定的part """
        rs = database.get_sub_tag_by_part_and_tag_name( self.__part_id, tag_name )
        if rs is None:
            return ''
        else:
            return rs

    def get_part_id(self):
        return self.__part_id

    def get_children(self, database, mode=0):
        """
        mode = 0: 查找子清单
        mode = 1: 查找父清单
        """
        if mode == 0:
            rs = database.get_children( self.__part_id )
        else:
            rs = database.get_parents( self.__part_id )
        if rs is None:
            return None
        result = []
        for r in rs:
            p = Part( r[1], r[2], r[3], r[4], description=r[5], comment=r[6] )
            one_r = (r[0], p, r[7], r[8], r[9])
            result.append( one_r )
        """
        r[0] - relation_id
        p - Part
        r[7] - qty_1
        r[8] - qty_2
        r[9] - relation_index, 在清单中的排位
        """
        return result

    def get_related_files(self, database):
        relation_files = database.get_files_2_part( self.__part_id )
        result = {}
        for f in relation_files:
            ss = os.path.splitext( f )[1][1:]
            ss = ss.upper()
            if ss in result.keys():
                v = result[ss]
                v.append( f )
            else:
                result[ss] = [f, ]
        return result

    def get_storing_data(self, database):
        """
        获取零件的库存信息，并生成新的Part对象
        :param database:
        :return: 新生成的零件的、带有库存信息的新对象
        """
        r_s = database.get_storing( part_id=self.__part_id, position=None )
        if r_s is None:
            return None
        storing_part = []
        for r in r_s:
            p = Part( self.__part_id, self.name, self.english_name, self.status, self.description, self.comment )
            p.position = r[1]
            p.qty = r[2]
            p.last_storing_date = r[3]
            p.unit_price = r[4]
            storing_part.append( p )
        return storing_part

    def get_erp_info(self, database):
        """
        获取中德ERP中德物料描述信息
        :param database: 数据库
        :return: 物料编码，物料描述，单位；or None
        """
        erp_code = self.get_specified_tag( database, '巨轮中德ERP物料编码' )
        if len( erp_code ) < 1:
            return None
        return database.get_erp_info( erp_code )

    def __eq__(self, other):
        return self.part_id == other.part_id

    def __hash__(self):
        return hash( self.__part_id )


class Tag:
    """ 代表一个Tag """

    def __init__(self, tag_id, name, parent_id, sort_index, database=None):
        self.tag_id = tag_id
        self.name = name
        self.parent_id = parent_id
        self.parent_name = ''
        self.sort_index = sort_index
        self.children = []
        self.__search = False
        self.__whole_name = name
        if database is not None and parent_id is not None:
            self.__build_whole_name( database, parent_id )

    def __build_whole_name(self, database, parent):
        ts = database.get_tags( tag_id=parent )
        t = ts[0]
        self.parent_name = t[1]
        self.__whole_name = '{0} > {1}'.format( t[1], self.__whole_name )
        if t[2] is not None:
            self.__build_whole_name( database, t[2] )

    def search_children(self, database):
        if self.__search:
            return
        self.__search = True
        rr = database.get_tags( parent_id=self.tag_id )
        for r in rr:
            t = Tag( r[0], r[1], r[2], r[3], database=database )
            self.children.append( t )

    def sort_children_by_name(self, database):
        if len( self.children ) < 1:
            return False, None
        t_list = sorted( self.children, key=lambda c: c.name.lower() )
        index = 1
        for t in t_list:
            t.sort_index = index
            database.sort_one_tag_to_index( t.tag_id, index )
            index += 1
        self.children = t_list
        return True, t_list

    @staticmethod
    def get_tags(database, tag_id=None, name=None, parent_id=None):
        rs = database.get_tags( tag_id, name, parent_id )
        result = []
        for r in rs:
            t = Tag( r[0], r[1], r[2], r[3], database=database )
            result.append( t )
        return result

    @staticmethod
    def add_one_tag_2_part(database, tag_name, part_id, parent_tag_id=None):
        test_tag = database.get_tags( name=tag_name, parent_id=parent_tag_id )
        """
        tag_exist = 0 新建了 tag，并进行了链接；
        tag_exist = 1 使用原有的 tag，并进行了链接；
        tag_exist = 2 使用原有的 tag，但已经有了链接。
        """
        tag_exist = 0
        if len( test_tag ) < 1:
            # 新创建一个 Tag
            the_tag_id = database.create_one_tag( tag_name, parent_tag_id )
        else:
            # 使用原有的 Tag
            the_tag_id = test_tag[0][0]
            tag_exist = 1
        rs = database.set_tag_2_part( the_tag_id, part_id )
        if not rs:
            tag_exist = 2
        return the_tag_id, tag_exist

    def get_whole_name(self):
        return self.__whole_name

    def __str__(self):
        return self.__whole_name


class DoStatistics( QThread ):
    """ 实施统计功能的类 """

    clean_part_list_signal = pyqtSignal()
    finish_statistics_signal = pyqtSignal( bool, float )
    # 增加一个项目到清单中，参数意义：part_d, 数量, 单价
    add_2_part_list_signal = pyqtSignal( int, float, float )

    def __init__(self, database):
        super().__init__()
        self.__part_id = None
        self.__stat_type = None
        self.__database = None
        self.__result = {}  # 最终统计结果
        self.__ignore_part = {}  # 由于某些物料打包采购了，则在统计结果排除相应的子项
        self.__stop_flag = False
        self.__db_type = database[0]
        self.__database = database[1]
        self.__sum_price = 0.0

        # 当前在运算的 Part
        self.__current_part = None

        # 预存各种tag的id
        # 来源
        self.__purchase_tag = self.__database.get_tag_id( '采购', '来源' )
        self.__no_standard_tag = self.__database.get_tag_id( '自制', '来源' )
        self.__assembly_tag = self.__database.get_tag_id( '装配', '来源' )
        # 类别
        self.__dwg_type_tag = self.__database.get_tag_id( '图纸', '类别' )
        self.__doc_type_tag = self.__database.get_tag_id( '文档', '类别' )
        # 统计策略
        self.__package_purchase_tag = self.__database.get_tag_id( '打包', '统计策略' )

    def set_data(self, part_id, stat_type):
        self.__part_id = part_id
        """ 统计方式，[完全, 投料, 装配, 是否计算金额]，前三个只有一个是 True """
        self.__stat_type = stat_type
        self.__result.clear()
        self.__stop_flag = False
        self.__current_part = part_id

    def stop(self):
        self.__stop_flag = True

    def run(self):
        self.__sum_price = 0.0
        self.clean_part_list_signal.emit()
        self.__do_statistics( 1.0 )
        if self.__stop_flag:
            return
        p_list = []
        p_list.extend( self.__result.keys() )
        p_list.sort()
        for i in p_list:
            if self.__stop_flag:
                return
            qty = self.__result[i]
            # 判断是否被打包在某个单元中，如果是，则将其移除
            if len( self.__ignore_part ) > 0:
                if i in self.__ignore_part:
                    i_qty = self.__ignore_part[i]
                    t_qty = i_qty - qty
                    if t_qty <= 0:
                        qty = qty - i_qty
                        self.__ignore_part.pop( i )
                    else:
                        qty = 0
                        self.__ignore_part[i] = t_qty
            if qty <= 0.0:
                continue
            unit_price = 0.0
            if self.__stat_type[-1]:
                unit_price = Part.get_unit_price( self.__database, i )
                self.__sum_price += unit_price * qty
            self.add_2_part_list_signal.emit( i, qty, unit_price )
        temp_sum_price = 0.0
        if self.__stat_type[-1]:
            temp_sum_price = self.__sum_price
        self.finish_statistics_signal.emit( self.__stop_flag, temp_sum_price )

    def __do_statistics(self, qty):
        """ 实际的统计，返回 True 表示被中断了 """
        tt = Part.get_parts( self.__database, part_id=self.__current_part )
        if len( tt ) < 1:
            return
        p: Part = tt[0]
        if self.__stop_flag:
            return
        children = p.get_children( self.__database )
        if children is None:
            self.__add_2_result( self.__current_part, qty )
            return
        for c in children:
            if self.__stop_flag:
                return
            the_part: Part = c[1]

            # 根据类别和设置进行判断
            all_tags = the_part.get_tags_id( self.__database )
            self.__current_part = c[1].get_part_id()
            if self.__stat_type[0]:
                # 完全的统计
                self.__do_statistics( qty * c[2] )
            elif self.__stat_type[1]:
                # 判断是不是打包采购的物品
                if self.__package_purchase_tag in all_tags:
                    self.__add_2_ignore_dict( c[1].get_part_id(), qty * c[2] )
                # 统计要投料（采购）的
                if (self.__dwg_type_tag in all_tags) or (self.__doc_type_tag in all_tags):
                    continue
                if self.__purchase_tag in all_tags:
                    self.__add_2_result( c[1].get_part_id(), qty * c[2] )
                    continue
                if self.__no_standard_tag in all_tags:
                    # 由于自制零件，有可能直接从外部采购，也有可能采购胚料，再进行外协加工。
                    if not self.__stat_type[-1]:
                        # 在不用累计价格的情况下，则不进行分析
                        self.__add_2_result( c[1].get_part_id(), qty * c[2] )
                        continue
                    else:
                        unit_price = Part.get_unit_price( self.__database, c[1].get_part_id() )
                        if unit_price > 0.001:
                            # 有找到单价，则不再进行向下分析
                            self.__add_2_result( c[1].get_part_id(), qty * c[2] )
                            continue
                self.__do_statistics( qty * c[2] )
            elif self.__stat_type[2]:
                # 统计要装配的
                if (self.__dwg_type_tag in all_tags) or (self.__doc_type_tag in all_tags):
                    continue
                if (self.__assembly_tag in all_tags) or (self.__no_standard_tag in all_tags):
                    self.__add_2_result( c[1].get_part_id(), qty * c[2] )
                    continue
                self.__do_statistics( qty * c[2] )

    def __add_2_ignore_dict(self, part_id, qty):
        tt = Part.get_parts( self.__database, part_id=part_id )
        if len( tt ) < 1:
            return
        p: Part = tt[0]
        if self.__stop_flag:
            return
        children = p.get_children( self.__database )
        if children is not None:
            for c in children:
                the_part: Part = c[1]
                c_part_id = the_part.get_part_id()
                c_qty = qty * c[2]
                if c_part_id in self.__ignore_part:
                    self.__ignore_part[c_part_id] += c_qty
                else:
                    self.__ignore_part[c_part_id] = c_qty

    def __add_2_result(self, part_id, qty):
        if part_id in self.__result:
            self.__result[part_id] += qty
        else:
            self.__result[part_id] = qty


class TagTreeBuilder( QThread ):
    """ 创意一个Tag的树型数据，以作为MVC中的M """

    model_created = pyqtSignal( QStandardItemModel )

    def __init__(self, database):
        super( TagTreeBuilder, self ).__init__()
        self.__tag_id = None
        self.__tag_name = None
        self.__parent_id = None
        self.tag_tree_model = QStandardItemModel()
        self.__database_type = database[0]
        self.__database = database[1]

    def set_search_arg(self, tag_id=None, name=None, parent_id=None):
        self.__tag_id = tag_id
        self.__tag_name = name
        self.__parent_id = parent_id

    def run(self):
        self.tag_tree_model.clear()
        self.tag_tree_model.setHorizontalHeaderLabels(['标签'])
        tags = Tag.get_tags( self.__database, tag_id=self.__tag_id, name=self.__tag_name, parent_id=self.__parent_id )
        for t in tags:
            node = QStandardItem( t.name )
            node.setData( t, Qt.UserRole )
            self.tag_tree_model.appendRow( node )
            t.search_children( self.__database )
            for c in t.children:
                c_node = QStandardItem( c.name )
                c_node.setData( c, Qt.UserRole )
                node.appendRow( c_node )
        self.model_created.emit(self.tag_tree_model)
