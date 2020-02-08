""" 一些基础的数据类 """
import os.path
from decimal import Decimal

from PyQt5.QtCore import (QThread, pyqtSignal)

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
        pdm_records = database.get_price_from_self_record( part_id=part_id, top=1 )
        if pdm_records is not None:
            r = pdm_records[0]
            price = (r[1] + r[2]) / (Decimal.from_float( 1.0 ) + r[3]) / r[4]
            return float( price )
        return float( 0.0 )

    def get_tags(self, database):
        rr = database.get_tags_2_part( self.__part_id )
        for r in rr:
            t = Tag( r[0], r[1], r[2], r[3], database=database )
            self.tags.append( t )

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
        self.sort_index = sort_index
        self.children = []
        self.__search = False
        self.__whole_name = name
        if database is not None and parent_id is not None:
            self.__build_whole_name( database, parent_id )

    def __build_whole_name(self, database, parent):
        ts = database.get_tags( tag_id=parent )
        t = ts[0]
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
        t_list = sorted( self.children, key=lambda c: c.name )
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
        self.__result = {}
        self.__stop_flag = False
        self.__db_type = database[0]
        self.__database = database[1]
        self.__sum_price = 0.0

        # 当前在运算的 Part
        self.__current_part = None

    def set_data(self, part_id, stat_type):
        self.__part_id = part_id
        """ [all, purchase, assembly]，只有一个是 True """
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
        p: Part = Part.get_parts( self.__database, part_id=self.__current_part )[0]
        if self.__stop_flag:
            return
        children = p.get_children( self.__database )
        if children is None:
            self.__add_2_result( self.__current_part, qty )
            return
        for c in children:
            if self.__stop_flag:
                return

            # 注明时采购时，就不要再往下查询
            pur_type = c[1].get_specified_tag( self.__database, '来源' )
            # 根据类别和设置进行判断
            p_type = c[1].get_specified_tag( self.__database, '类别' )

            self.__current_part = c[1].get_part_id()
            if self.__stat_type[0]:
                # 完全的统计
                self.__do_statistics( qty * c[2] )
            elif self.__stat_type[1]:
                # 统计要投料（采购）的
                if p_type == '图纸' or p_type == '文档':
                    continue
                if pur_type == '采购':
                    self.__add_2_result( c[1].get_part_id(), qty * c[2] )
                    continue
                self.__do_statistics( qty * c[2] )
            elif self.__stat_type[2]:
                # 统计要装配的
                if p_type == '图纸' or p_type == '文档':
                    continue
                if pur_type == '自制' or pur_type == '采购' or pur_type == '装配':
                    self.__add_2_result( c[1].get_part_id(), qty * c[2] )
                    continue
                self.__do_statistics( qty * c[2] )

    def __add_2_result(self, part_id, qty):
        if part_id in self.__result:
            self.__result[part_id] += qty
        else:
            self.__result[part_id] = qty


class Product:
    """ 代表一个产品 """

    def __init__(self, product_id, actual_status, product_comment, status_comment, config):
        self.product_id = product_id
        self.actual_status = actual_status
        self.product_comment = product_comment
        self.status_comment = status_comment
        self.config = config
        self.tags = []
        self.children = []

    @staticmethod
    def get_products(database, product_id=None, product_comment=None, status_comment=None, config=None, top=False):
        rs = database.get_products( product_id, product_comment, status_comment, config, top )
        result = []
        for r in rs:
            pp = Product( r[0], r[2], r[7], r[8], r[9] )
            t_children = pp.get_children( database )
            if t_children is not None:
                pp.children.extend( t_children )
            result.append( pp )
        return result

    def get_children(self, database, mode=0):
        """
        mode = 0: 查找子清单
        mode = 1: 查找父清单
        """
        rs = None
        if mode == 0:
            rs = database.get_children( self.product_id )
        elif mode == 1:
            rs = database.get_parent( self.product_id )
        if rs is None:
            return None
        result = []
        for r in rs:
            pp = Product( r[0], r[2], r[7], r[8], r[9] )
            result.append( pp )
        return result

    def get_tags(self, database):
        self.tags.clear()
        rr = database.get_tags_2_product( self.product_id )
        for r in rr:
            t = Tag( r[0], r[1], r[2], r[3], database=database )
            self.tags.append( t )

    @staticmethod
    def get_products_from_tag(database, tag_id):
        rs = database.get_products_2_tag( tag_id )
        result = []
        for r in rs:
            pp = Product( r[0], r[2], r[7], r[8], r[9] )
            result.append( pp )
        return result

    def __eq__(self, other):
        return self.product_id == other.product_id

    def __hash__(self):
        return hash( self.product_id )
