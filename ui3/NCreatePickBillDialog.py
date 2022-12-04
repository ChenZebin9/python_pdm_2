# coding=gbk
import os
import sys

import clr
from PyQt5.QtCore import (Qt, QDate, QModelIndex)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QDialog, QApplication, QLineEdit, QDateEdit, QMessageBox, QDialogButtonBox, QFileDialog)

import Com
from excel.ExcelHandler import (ExcelHandler2, ExcelHandler3)
from ui3.CreatePickBillDialog import *
from ui.NImportSettingDialog import (NImportSettingDialog)
from db.MssqlHandler import MssqlHandler
from db.DatabaseHandler import DatabaseHandler
from ui3.NErpItemSelector import NErpItemSelector
from Part import Part
from db.jl_erp import JL_ERP_Database

clr.FindAssembly( 'dlls/PdfLib.dll' )
clr.AddReference( 'dlls/PdfLib' )
import PdfLib


class NCreatePickBillDialog( QDialog, Ui_Dialog ):
    """ ͨ������Excel�ļ������ݣ�ʵ�־��ֵ����ϵ��Ĵ�ӡ����� """

    Column_names_1 = ('��ͬ��', '�����', '�е����ϱ���', '��������', '��λ', '����')
    Column_names_2 = ('��ͬ��', '�����', '�������ϱ���', '��������', '��λ', '����')

    def __init__(self, database, parent=None):
        self.__parent = parent
        self.__database: DatabaseHandler = database
        super( NCreatePickBillDialog, self ).__init__( parent )
        self.__timeSelector = QDateEdit()
        self.__billNrLineEdit = QLineEdit()
        self.__operatorLineEdit = QLineEdit()
        self.__table_modal = QStandardItemModel()
        self.__one_import_data = []
        # Ĭ�ϵĺ�ͬ��
        self.__default_product_id = ''
        # ���ĸ��ⷿ
        self.__from_storage = 'D'
        self.setup_ui()
        # Ԥ�ȴ򿪾���ERP������
        self.__jl_erp_database = None
        # ��¼��ǰ��������ÿһ�е�Ψһ��ֵ
        self.__record_index = 0
        # ÿһ�е����⴦�������0-���ս����ȥ��
        self.__special_mark = {}

    def get_default_storage(self):
        """
        ��ȡĬ�ϵĲֿ�
        :return:
        """
        return self.__from_storage

    def setup_ui(self):
        super( NCreatePickBillDialog, self ).setupUi( self )
        self.setLayout( self.mainVLayout )

        self.__timeSelector.setCalendarPopup( True )
        self.__timeSelector.setDisplayFormat( 'yyyy-MM-dd' )
        self.__timeSelector.setAlignment( Qt.AlignCenter )
        self.__timeSelector.setDate( QDate.currentDate() )
        self.__billNrLineEdit.setAlignment( Qt.AlignCenter )
        self.__operatorLineEdit.setAlignment( Qt.AlignCenter )
        self.formLayout.addRow( "���ڣ�", self.__timeSelector )
        self.formLayout.addRow( "���ţ�", self.__billNrLineEdit )
        self.formLayout.addRow( "�����ߣ�", self.__operatorLineEdit )

        self.midRightHL.setAlignment( Qt.AlignTop )

        self.addButton.clicked.connect( self.__add_items )
        self.freeAddButton.clicked.connect( self.__add_items )
        self.removeButton.clicked.connect( self.__remove_item )

        self.theDialogButtonBox.clicked.connect( self.__buttonBox_clicked )

        header_goods = self.itemsTableView.horizontalHeader()
        header_goods.sectionClicked.connect( self.__sort_by_column )

    def __sort_by_column(self, column):
        header_goods = self.itemsTableView.horizontalHeader()
        i = header_goods.sortIndicatorOrder()
        if i == 0:
            self.__table_modal.sort( column, Qt.AscendingOrder )
        else:
            self.__table_modal.sort( column, Qt.DescendingOrder )

    def set_config(self, config_dict: dict):
        """
        ����ĳЩ����
        :param config_dict: dict��һ�����õ��ֵ�
        :return:
        """
        if '������' in config_dict:
            self.__operatorLineEdit.setText( config_dict['������'] )
        if '��ͬ��' in config_dict:
            self.__default_product_id = config_dict['��ͬ��']
        if '�ֿ�' in config_dict:
            self.__from_storage = config_dict['�ֿ�']
        else:
            self.__from_storage = 'D'
        self.__billNrLineEdit.setText( config_dict['�嵥'] )
        # �����б�ı�ͷ
        self.__table_modal.setHorizontalHeaderLabels(
            NCreatePickBillDialog.Column_names_1 if self.__from_storage != 'F' else
            NCreatePickBillDialog.Column_names_2 )
        self.itemsTableView.setModel( self.__table_modal )

    def add_items(self, the_items):
        """
        ֧�ִ��ⲿ�Ի��������Ŀ
        :param the_items: list��һ����������Ŀ��Ϣ���б� ([����ţ����ϱ��룬������������λ������])
        :return:
        """
        for r in the_items:
            if len( r ) < 5:
                qty = 0.
            else:
                qty = r[4]
            id_item = QStandardItem( r[0] )
            id_item.setData( self.__record_index, Qt.UserRole + 1 )
            self.__record_index += 1
            one_row_in_table = [QStandardItem( self.__default_product_id ),
                                id_item,
                                QStandardItem( r[1] ),
                                QStandardItem( r[2] ),
                                QStandardItem( r[3] ),
                                QStandardItem( '{0:.2f}'.format( qty ) )]
            self.__table_modal.appendRow( one_row_in_table )
        self.itemsTableView.resizeColumnsToContents()

    def __add_items(self):
        try:
            if self.sender() is self.addButton:
                f_spec = 'Excel Files (*.xls, *.xlsx)'
                previous_path = Com.get_property_value( 'load_path' )
                ini_path = previous_path if previous_path != '' else '.'
                file_name, _ = QFileDialog.getOpenFileName( self, caption='ѡ�������ļ�',
                                                            filter=f_spec, directory=ini_path )
                if file_name == '':
                    return
                load_path = os.path.dirname( file_name )
                Com.save_property_value( 'load_path', load_path )
                self.__one_import_data.clear()
                dialog = NImportSettingDialog( self, '��������', None )
                if file_name[-3:].upper() == 'XLS':
                    excel = ExcelHandler2( file_name )
                else:
                    excel = ExcelHandler3( file_name )
                config_settings = ('��ͬ��', '�����', '���ϱ���', '����')
                the_default_data = (self.__default_product_id, None, None, None)
                dialog.set_excel_mode( config_settings, excel, True, default_data=the_default_data )
                dialog.exec_()
            elif self.sender() is self.freeAddButton:
                self.__one_import_data.clear()
                dlg = NErpItemSelector( self.__database, self )
                if self.__from_storage == 'F':
                    dlg.setWindowTitle( '�Ӿ��ֲֿ�ѡ��' )
                    dlg.is_zd_erp = False
                dlg.exec_()
            if len( self.__one_import_data ):
                for r in self.__one_import_data:
                    # ��ͬ�ţ�����ţ��е����ϱ��룬����
                    one_row_in_table = [QStandardItem( r[0] )]
                    if r[1] is not None and len( r[1] ) > 0:
                        tt = float( r[1] )
                        part_id = int( tt )
                        id_item = QStandardItem( '{:08d}'.format( part_id ) )
                        id_item.setData( self.__record_index, Qt.UserRole + 1 )
                        self.__record_index += 1
                        one_row_in_table.append( id_item )
                        the_part: Part = Part.get_parts( database=self.__database, part_id=part_id )[0]
                        if self.__from_storage != 'F':
                            erp_code = the_part.get_specified_tag( database=self.__database, tag_name='�����е�ERP���ϱ���' )
                        else:
                            erp_code = the_part.get_specified_tag( database=self.__database, tag_name='��������ERP���ϱ���' )
                        if len( erp_code ) > 0:
                            one_row_in_table.append( QStandardItem( erp_code ) )
                            if self.__from_storage != 'F':
                                erp_info = self.__database.get_erp_data( erp_code )
                            else:
                                if self.__jl_erp_database is None:
                                    self.__jl_erp_database = JL_ERP_Database()
                                erp_info = self.__jl_erp_database.get_erp_data( erp_code )
                            one_row_in_table.append( QStandardItem( erp_info[1] ) )
                            one_row_in_table.append( QStandardItem( erp_info[2] ) )
                            one_row_in_table.append( QStandardItem( r[3] ) )
                    elif r[2] is not None and len( r[2] ) > 0:
                        one_row_in_table.append( QStandardItem( '' ) )
                        id_item = QStandardItem( r[2] )
                        id_item.setData( self.__record_index, Qt.UserRole + 1 )
                        self.__record_index += 1
                        one_row_in_table.append( id_item )
                        if self.__from_storage != 'F':
                            erp_info = self.__database.get_erp_data( r[2] )
                        else:
                            if self.__jl_erp_database is None:
                                self.__jl_erp_database = JL_ERP_Database()
                            erp_info = self.__jl_erp_database.get_erp_data( r[2] )
                        one_row_in_table.append( QStandardItem( erp_info[1] ) )
                        one_row_in_table.append( QStandardItem( erp_info[2] ) )
                        one_row_in_table.append( QStandardItem( r[3] ) )
                    self.__table_modal.appendRow( one_row_in_table )
                self.itemsTableView.resizeColumnsToContents()
        except Exception as ex:
            QMessageBox.warning( self, '', str( ex ), QMessageBox.Ok )

    def __remove_item(self):
        resp = QMessageBox.question( self, 'ȷ��', 'ȷ��Ҫ�Ƴ���Щ�У�', QMessageBox.Yes | QMessageBox.No )
        if resp == QMessageBox.No:
            return
        indexes = self.itemsTableView.selectedIndexes()
        removed_row_cc = 0
        m = []
        for i in indexes:
            ii: QModelIndex = i
            m.append( ii.row() )
        m.sort()
        a = sorted( set( m ), key=m.index )
        for i in a:
            self.__table_modal.removeRow( i - removed_row_cc )
            removed_row_cc += 1

    def __buttonBox_clicked(self, button):
        if button is self.theDialogButtonBox.button( QDialogButtonBox.Ok ):
            self.__do_accept()
        elif button is self.theDialogButtonBox.button( QDialogButtonBox.Cancel ):
            self.__do_close()

    def __do_accept(self):
        except_type = -1
        record_index = -1
        try:
            r_n = self.__table_modal.rowCount()
            if r_n < 1:
                raise Exception( 'û��Ҫ���������' )
            data_4_paper = []
            items_4_database = []
            c_n = (0, 3, 4, 5, 2)
            for i in range( r_n ):
                row_data = []
                part_id_cell: QStandardItem = self.__table_modal.item( i, 1 )
                record_index = part_id_cell.data( Qt.UserRole + 1 )
                part_id = int( part_id_cell.text().lstrip( '0' ) )
                qty_value = 0.0
                for j in c_n:
                    cell: QStandardItem = self.__table_modal.item( i, j )
                    if j == 5:
                        may_error = False
                        if cell is None:
                            may_error = True
                        else:
                            qty_value = float( cell.text() )
                            if qty_value <= 0:
                                may_error = True
                            else:
                                row_data.append( '%.1f' % qty_value )
                        if may_error:
                            QMessageBox.warning( self, '��������', f'\"{row_data[1]}\"�����������Ϊ�㣬��ȷ�ϣ�' )
                            return
                    else:
                        if cell is None:
                            row_data.append( '' )
                        else:
                            row_data.append( cell.text() )
                record = [row_data[0], part_id, row_data[-1], qty_value, record_index]
                data_4_paper.append( row_data )
                items_4_database.append( record )
            bill_name = self.__billNrLineEdit.text()
            data_4_database = [bill_name, self.__operatorLineEdit.text(), self.__timeSelector.text(),
                               '���ⵥ', self.__from_storage, items_4_database]
            resp = self.__database.create_picking_record( data_4_database, self.__special_mark )
            if resp is not None:
                except_type = resp[0]
                record_index = resp[2]
                raise Exception( resp[1] )
            if self.__from_storage == 'F':
                department_name = '����OPS��Ŀ��'
            elif self.__from_storage == 'A':
                department_name = 'OPS�����ֳ�'
            else:
                department_name = '�е�OPS��Ŀ��'
            pdf_creator = PdfLib.CreatePickBill( data_4_paper, department_name,
                                                 self.__operatorLineEdit.text(),
                                                 self.__timeSelector.text(), self.__billNrLineEdit.text() )
            save_path = Com.get_property_value( 'save_path' )
            ini_path = f'./{bill_name}.pdf' if save_path == '' else f'{save_path}{bill_name}.pdf'
            to_save_file, _ = QFileDialog.getSaveFileName( self, caption='�����ļ�', filter='Pdf Files (*.pdf)',
                                                           directory=ini_path )
            if to_save_file is '':
                QMessageBox.warning( self, 'ȡ��', '��ֹ�����', QMessageBox.Ok )
                return
            save_path = os.path.dirname( to_save_file )
            Com.save_property_value( 'save_path', save_path )
            if to_save_file.lower()[-4:] != '.pdf':
                to_save_file += '.pdf'
            pdf_creator.DoPrint( to_save_file )
            QMessageBox.information( self, '���', '����� {0} �ļ���'.format( to_save_file ), QMessageBox.Ok )
            self.close()
            resp = QMessageBox.question( self, 'ѯ��', f'�Ƿ��{to_save_file}�ļ���', QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes )
            if resp == QMessageBox.Yes:
                os.startfile( to_save_file )
        except Exception as ex:
            if except_type == 0:
                resp = QMessageBox.question( self, '�����쳣', str( ex ),
                                             QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.No )
                if resp == QMessageBox.Yes:
                    self.__special_mark[record_index] = 0
            elif except_type == 1:
                QMessageBox.warning( self, '�������ϵ�ʱ�쳣', str( ex ), QMessageBox.Ok )
        finally:
            if self.__jl_erp_database is not None:
                self.__jl_erp_database.close()

    def __do_close(self):
        if self.__jl_erp_database is not None:
            self.__jl_erp_database.close()
        self.close()

    def fill_import_cache(self, data):
        self.__one_import_data = data.copy()

    def is_zd_erp(self):
        """
        �Ƿ�����е�ERP�Ĳ�����
        :return: TRUE or FALSE
        """
        return self.__from_storage != 'F'


def run_function(the_database_setting):
    app = QApplication( sys.argv )
    database_handler = MssqlHandler( *the_database_setting[1:] )
    the_dialog = NCreatePickBillDialog( database_handler )
    the_dialog.show()
    sys.exit( app.exec_() )
