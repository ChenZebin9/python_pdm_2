# coding=gbk
import configparser

from db.MssqlHandler import MssqlHandler
from db.SqliteHandler import SqliteHandler
from Part import Part
import xlwt
import xlrd
import os
import sys
from tkinter import (filedialog, Tk)


class CalculateSupply:
    """
    ͨ�����п�棬�����ֳ������ϡ��ɹ���������
    requirement��һ���ֵ䣬keyΪ����ţ�valueΪ������

    do_calculate �ڼ���ʱ��
        1. mode - 0�����Ǽ��㣬Ҫ���ӹ��ģ���Ҫ���ϻ�ӱ�ע��
        2. mode - 1�����׼����Ҫ�ɹ������ϡ�
    """

    # ���ӹ������б�
    machining_parts = []
    # �ɹ����б�key - part_id��value - Ϊ�ֳ�����棬Ͷ�ϵ�����
    purchase_parts = {}

    def __init__(self, requirements, storage_database, part_database):
        self.__require_dict: dict = requirements
        self.__storage_database = storage_database
        self.__part_database = part_database
        self.__mode = 1
        # һЩ���ݵĴ���
        # ��ǰ�����������
        self.__current_part = None
        # ȫ�ֻ��� Excel �к�
        self.__global_r_index = 1

    def do_calculate(self, mode=1):
        self.__mode = mode
        if mode == 1:
            for k in self.__require_dict.keys():
                self.__do_calculate( k, self.__require_dict[k] )
        elif mode == 0:
            pass

    # parent_part ��Ҫ�γ�һ�����εĲ˵�
    def __do_calculate(self, part_id, qty, parent_part=None):
        part_s = Part.get_parts( self.__part_database, part_id=part_id )
        if len( part_s ) < 1:
            self.__current_part = None
            return
        else:
            self.__current_part = part_s[0]
        r = self.__compare_supply( part_id, qty )

        s_type = self.__current_part.get_specified_tag( self.__part_database, '��Դ' )
        parent_4_next = None
        if s_type == '����' or parent_part is not None:
            # ֻ����������Ž��м���
            to_be_new_part = Material( part_id, parent_part )
            if to_be_new_part in self.machining_parts:
                index = self.machining_parts.index( to_be_new_part )
                existed_part: Material = self.machining_parts[index]
                existed_part.add_qty( qty, r[0], r[1], r[2] )
                parent_4_next = existed_part
            else:
                to_be_new_part.set_qty( qty, r[0], r[1], r[2] )
                self.machining_parts.append( to_be_new_part )
                parent_4_next = to_be_new_part

        qty_list = [0.0, 0.0, 0.0]
        if part_id in self.purchase_parts:
            qty_list = self.purchase_parts[part_id]
        if r[0] > 0.0:
            qty_list[0] += r[0]
        if r[1] > 0.0:
            qty_list[1] += r[1]
        if r[2] <= 0.0:
            self.purchase_parts[part_id] = qty_list
            return
        rs = self.__get_children()
        if rs is None:
            qty_list[2] += r[2]
            self.purchase_parts[part_id] = qty_list
            return
        for c in rs:
            self.__do_calculate( c[0], c[1] * r[2], parent_4_next )

    """ 
    ����һ�����б���ʾ�������һ��Ҫ���ӹ������������û��Ҫ�ɹ������ϡ�
    �� mode = 1 ʱ���������Ҫ��ʧ��
    �� mode = 0 ʱ��Ҫ����ϸ�����㡣
    ���� None ʱ����ʾ���������mode = ?ʱ������Ҫ������
    """

    def __get_children(self):
        if self.__current_part is None:
            return
        children = self.__current_part.get_children( self.__part_database )
        if children is None:
            s_type = self.__current_part.get_specified_tag( self.__part_database, '��Դ' )
            if s_type == '����':
                return []
        else:
            result = []
            for c in children:
                m_type = c[1].get_specified_tag( self.__part_database, '��Դ' )
                if len( m_type ) <= 0 or (len( m_type ) > 0 and m_type != '�ӹ�'):
                    result.append( [c[1].get_part_id(), c[2]] )
            return result

    def __compare_supply(self, part_id, qty):
        r = self.__storage_database.get_storage( part_id )
        if r is None:
            return 0.0, 0.0, qty
        if r[0] < 0.0:
            qty -= r[0]
            in_site_stock = 0.0
        else:
            in_site_stock = r[0]
        in_storage_stock = r[1]
        # ��ȥ�Ѿ����������
        if part_id in self.purchase_parts:
            qty_list = self.purchase_parts[part_id]
            in_site_stock -= qty_list[0]
            in_storage_stock -= qty_list[1]
        if qty <= in_site_stock:
            return qty, 0.0, 0.0
        elif qty > in_site_stock:
            if qty - in_site_stock > in_storage_stock:
                return in_site_stock, in_storage_stock, qty - in_site_stock - in_storage_stock
            else:
                return in_site_stock, qty - in_site_stock, 0.0

    def do_material_summary(self):
        if len( self.machining_parts ) < 1:
            return
        temp = []
        for m in self.machining_parts:
            if m.parent is not None:
                p: Material = m.parent
                c = len( p.children )
                m.index = c + 1
                p.children.append( m )
        for m in self.machining_parts:
            if m.parent is None:
                c = len( temp )
                m.index = c + 1
                temp.append( m )
        self.machining_parts = temp

    def export_2_excel(self):
        """ �����ݵ���Ϊ Excel """
        workbook = xlwt.Workbook( encoding='utf8' )
        sh: xlwt.Worksheet = workbook.add_sheet( 'Pick & Purchase' )
        header_style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        header_style.font = font
        header_contents = ('�����', '����', '�ͺ�', '�ֳ�', '���', 'Ͷ��')
        header_count = len( header_contents )
        for i in range( 0, header_count ):
            sh.write( 0, i, header_contents[i], header_style )

        r_index = 1
        n_s = list( self.purchase_parts.keys() )
        n_s.sort()
        for k in n_s:
            qty_s = self.purchase_parts[k]
            sh.write( r_index, 0, k )
            p_s = self.__part_database.get_parts( part_id=k )
            if len( p_s ) > 0:
                p = p_s[0]
                sh.write( r_index, 1, f'{p[1]}' )
                if p[3] is not None:
                    sh.write( r_index, 2, f'{p[3]}' )
                for j in range( 0, 3 ):
                    sh.write( r_index, 3 + j, qty_s[j] )
            r_index += 1

        if self.machining_parts is not None and len( self.machining_parts ) > 0:
            sh_m: xlwt.Worksheet = workbook.add_sheet( 'Machining' )
            header_contents = ('���', '�����', '����', '�ͺ�', '����', '�ֳ�', '���', 'Ͷ��')
            header_count = len( header_contents )
            for i in range( 0, header_count ):
                sh_m.write( 0, i, header_contents[i], header_style )
            for m in self.machining_parts:
                self.__material_output( sh_m, m )

        target_file = filedialog.asksaveasfilename( title='����ͳ������', filetypes=[("EXCEL�ļ�", ".xls")] )
        if target_file is None or target_file == '':
            return
        if target_file.lower()[-4:] != '.xls':
            target_file = target_file + '.xls'
        workbook.save( target_file )
        print( f'��������{target_file} ��' )
        os.startfile( target_file )

    def __material_output(self, the_sheet: xlwt.Worksheet, the_material_data):
        r = self.__global_r_index
        the_sheet.write( r, 0, the_material_data.get_index() )
        the_sheet.write( r, 1, the_material_data.part_id )
        p_s = self.__part_database.get_parts( part_id=the_material_data.part_id )
        if len( p_s ) > 0:
            p = p_s[0]
            the_sheet.write( r, 2, f'{p[1]}' )
            if p[3] is not None:
                the_sheet.write( r, 3, f'{p[3]}' )
        the_sheet.write( r, 4, the_material_data.qty_requirement )
        the_sheet.write( r, 5, the_material_data.qty_in_site )
        the_sheet.write( r, 6, the_material_data.qty_in_storage )
        the_sheet.write( r, 7, the_material_data.qty_4_purchase )
        self.__global_r_index += 1
        if len( the_material_data.children ) < 1:
            return
        else:
            for c in the_material_data.children:
                self.__material_output( the_sheet, c )


class Material:
    """ ������ϻ����������� """

    def __init__(self, part_id, parent=None):
        # ������
        self.index = 1
        # �����
        self.part_id = part_id
        self.qty_requirement = 0.0
        # �ֳ�����漰Ͷ�ϵ�����
        self.qty_in_site = 0.0
        self.qty_in_storage = 0.0
        self.qty_4_purchase = 0.0
        # ��һ�� Material[]
        self.children = []
        # ��һ��
        self.parent: Material = parent

    def add_qty(self, require_qty, in_site_qty, in_storage_qty, purchase_qty):
        self.qty_requirement += require_qty
        self.qty_in_site += in_site_qty
        self.qty_in_storage += in_storage_qty
        self.qty_4_purchase += purchase_qty

    def set_qty(self, require_qty, in_site_qty, in_storage_qty, purchase_qty):
        self.qty_requirement = require_qty
        self.qty_in_site = in_site_qty
        self.qty_in_storage = in_storage_qty
        self.qty_4_purchase = purchase_qty

    def get_index(self):
        cur_index = f'{self.index}'
        if self.parent is None:
            return cur_index
        else:
            return self.parent.__create_index( cur_index )

    def __create_index(self, index_from_child):
        new_index = f'{self.index}.{index_from_child}'
        if self.parent is None:
            return new_index
        else:
            self.parent.__create_index( new_index )

    def __eq__(self, other):
        return self.part_id == other.part_id and self.parent == other.parent

    def __hash__(self):
        id_0 = self.part_id
        if self.parent is not None:
            id_0 += self.parent.part_id * 10000
        return hash( id_0 )


if __name__ == '__main__':
    # ��ȡ���ݿ�
    config = configparser.ConfigParser()
    if not config.read( 'pdm_config.ini', encoding='GBK' ):
        raise Exception( 'INI file not found.' )

    database_file = config.get( 'Database', 'DatabaseFile' )
    s_database = SqliteHandler( database_file )

    server = config.get( 'Online', 'server' )
    user = config.get( 'Online', 'user' )
    password = config.get( 'Online', 'password' )
    database_name = config.get( 'Online', 'database' )
    p_database = MssqlHandler( server, database_name, user, password )
    try:
        # ѡȡ��������
        root = Tk()
        root.withdraw()
        source_file = filedialog.askopenfilename( title='���������ļ�', filetypes=[("EXCEL�ļ�", ".xls")] )
        if source_file is None or len( source_file ) < 1:
            sys.exit( 0 )
        work_book = xlrd.open_workbook( source_file )
        sht = work_book.sheet_by_index( 0 )
        n_rows = sht.nrows
        source_data = {}
        for i in range( 1, n_rows ):
            one_row = sht.row_values( i, 0, 3 )
            source_data[one_row[0]] = one_row[2]
        if len( source_data ) < 1:
            sys.exit( 0 )
        obj = CalculateSupply( source_data, s_database, p_database )
        print( '��ʼͳ��(mode=1)...' )
        obj.do_calculate( mode=1 )
        obj.do_material_summary()
        obj.export_2_excel()
    finally:
        s_database.close()
        p_database.close()
