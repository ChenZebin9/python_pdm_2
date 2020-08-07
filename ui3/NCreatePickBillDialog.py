# coding=gbk
import os
import sys

import clr
import win32con
import win32ui
from PyQt5.QtCore import (Qt, QDate, QModelIndex)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QDialog, QApplication, QLineEdit, QDateEdit, QMessageBox, QDialogButtonBox)

from excel.ExcelHandler import (ExcelHandler2, ExcelHandler3)
from ui3.CreatePickBillDialog import *
from ui.NImportSettingDialog import (NImportSettingDialog)
from db.MssqlHandler import MssqlHandler
from db.DatabaseHandler import DatabaseHandler
from Part import Part
from db.jl_erp import JL_ERP_Database

clr.FindAssembly( 'dlls/PdfLib.dll' )
clr.AddReference( 'dlls/PdfLib' )
import PdfLib


class NCreatePickBillDialog( QDialog, Ui_Dialog ):
    """ 通过导入Excel文件的数据，实现巨轮的领料单的打印输出。 """

    Column_names_1 = ('合同号', '零件号', '中德物料编码', '物料描述', '单位', '数量')
    Column_names_2 = ('合同号', '零件号', '巨轮物料编码', '物料描述', '单位', '数量')

    def __init__(self, database, parent=None):
        self.__parent = parent
        self.__database: DatabaseHandler = database
        super( NCreatePickBillDialog, self ).__init__( parent )
        self.__timeSelector = QDateEdit()
        self.__billNrLineEdit = QLineEdit()
        self.__operatorLineEdit = QLineEdit()
        self.__table_modal = QStandardItemModel()
        self.__one_import_data = []
        # 默认的合同号
        self.__default_product_id = ''
        # 从哪个库房
        self.__from_storage = 'D'
        self.setup_ui()
        # 预先打开巨轮ERP的连接
        self.__jl_erp_database = JL_ERP_Database()

    def setup_ui(self):
        super( NCreatePickBillDialog, self ).setupUi( self )
        self.setLayout( self.mainVLayout )

        self.__timeSelector.setCalendarPopup( True )
        self.__timeSelector.setAlignment( Qt.AlignCenter )
        self.__timeSelector.setDate( QDate.currentDate() )
        self.__billNrLineEdit.setAlignment( Qt.AlignCenter )
        self.__operatorLineEdit.setAlignment( Qt.AlignCenter )
        self.formLayout.addRow( "日期：", self.__timeSelector )
        self.formLayout.addRow( "单号：", self.__billNrLineEdit )
        self.formLayout.addRow( "操作者：", self.__operatorLineEdit )

        self.midRightHL.setAlignment( Qt.AlignTop )

        self.addButton.clicked.connect( self.__add_items )
        self.removeButton.clicked.connect( self.__remove_item )

        self.theDialogButtonBox.clicked.connect( self.__buttonBox_clicked )

    def set_config(self, config_dict: dict):
        """
        进行某些设置
        :param config_dict: dict，一个设置的字典
        :return:
        """
        if '操作者' in config_dict:
            self.__operatorLineEdit.setText( config_dict['操作者'] )
        if '合同号' in config_dict:
            self.__default_product_id = config_dict['合同号']
        if '仓库' in config_dict:
            self.__from_storage = config_dict['仓库']
        else:
            self.__from_storage = 'D'
        self.__billNrLineEdit.setText( config_dict['清单'] )
        # 设置列表的表头
        self.__table_modal.setHorizontalHeaderLabels(
            NCreatePickBillDialog.Column_names_1 if self.__from_storage != 'F' else NCreatePickBillDialog.Column_names_2 )
        self.itemsTableView.setModel( self.__table_modal )

    def add_items(self, the_items):
        """
        支持从外部对话框添加项目
        :param the_items: list，一个包括有项目信息的列表 ([零件号，物料编码，物料描述，单位])
        :return:
        """
        for r in the_items:
            one_row_in_table = [QStandardItem( self.__default_product_id ),
                                QStandardItem( r[0] ),
                                QStandardItem( r[1] ),
                                QStandardItem( r[2] ),
                                QStandardItem( r[3] ),
                                QStandardItem( '0' )]
            self.__table_modal.appendRow( one_row_in_table )
        self.itemsTableView.resizeColumnsToContents()

    def __add_items(self):
        try:
            open_flags = win32con.OFN_FILEMUSTEXIST
            fspec = 'Excel Files (*.xls, *.xlsx)|*.xls;*.xlsx||'
            dlg = win32ui.CreateFileDialog( 1, None, None, open_flags, fspec )
            selected_file = None
            if dlg.DoModal() == win32con.IDOK:
                selected_file = dlg.GetPathName()
            if selected_file is None:
                return
            file_name = selected_file
            self.__one_import_data.clear()
            dialog = NImportSettingDialog( self, '领料数据', None )
            if selected_file[-3:].upper() == 'XLS':
                excel = ExcelHandler2( file_name )
            else:
                excel = ExcelHandler3( file_name )
            config_settings = ('合同号', '零件号', '物料编码', '数量')
            dialog.set_excel_mode( config_settings, excel, True )
            dialog.exec_()
            if len( self.__one_import_data ):
                for r in self.__one_import_data:
                    # 合同号，零件号，中德物料编码，数量
                    one_row_in_table = [QStandardItem( r[0] )]
                    if r[1] is not None and len( r[1] ) > 0:
                        tt = float( r[1] )
                        part_id = int( tt )
                        one_row_in_table.append( QStandardItem( '{:08d}'.format( part_id ) ) )
                        the_part: Part = Part.get_parts( database=self.__database, part_id=part_id )[0]
                        if self.__from_storage != 'F':
                            erp_code = the_part.get_specified_tag( database=self.__database, tag_name='巨轮中德ERP物料编码' )
                        else:
                            erp_code = the_part.get_specified_tag( database=self.__database, tag_name='巨轮智能ERP物料编码' )
                        if len( erp_code ) > 0:
                            one_row_in_table.append( QStandardItem( erp_code ) )
                            if self.__from_storage != 'F':
                                erp_info = self.__database.get_erp_data( erp_code )
                            else:
                                erp_info = self.__jl_erp_database.get_erp_data( erp_code )
                            one_row_in_table.append( QStandardItem( erp_info[1] ) )
                            one_row_in_table.append( QStandardItem( r[3] ) )
                            one_row_in_table.append( QStandardItem( erp_info[2] ) )
                    elif r[2] is not None and len( r[2] ) > 0:
                        one_row_in_table.append( QStandardItem( '' ) )
                        one_row_in_table.append( QStandardItem( r[2] ) )
                        if self.__from_storage != 'F':
                            erp_info = self.__database.get_erp_data( r[2] )
                        else:
                            erp_info = self.__jl_erp_database.get_erp_data( r[2] )
                        one_row_in_table.append( QStandardItem( erp_info[1] ) )
                        one_row_in_table.append( QStandardItem( r[3] ) )
                        one_row_in_table.append( QStandardItem( erp_info[2] ) )
                    self.__table_modal.appendRow( one_row_in_table )
                self.itemsTableView.resizeColumnsToContents()
        except Exception as ex:
            QMessageBox.warning( self, '', str( ex ), QMessageBox.Ok )

    def __remove_item(self):
        resp = QMessageBox.question( self, '确认', '确定要移除这些行？', QMessageBox.Yes | QMessageBox.No )
        if resp == QMessageBox.No:
            return
        indexes = self.itemsTableView.selectedIndexes()
        removed_row_cc = 0
        row_to_remove = []
        for i in indexes:
            ii: QModelIndex = i
            row_to_remove.append( ii.row() )
        row_to_remove.sort()
        for i in row_to_remove:
            self.__table_modal.removeRow( i - removed_row_cc )
            removed_row_cc += 1

    def __buttonBox_clicked(self, button):
        if button is self.theDialogButtonBox.button( QDialogButtonBox.Ok ):
            self.__do_accept()
        elif button is self.theDialogButtonBox.button( QDialogButtonBox.Cancel ):
            self.__do_close()

    def __do_accept(self):
        try:
            r_n = self.__table_modal.rowCount()
            if r_n < 1:
                raise Exception( '没有要输出的数据' )
            data_4_paper = []
            items_4_database = []
            c_n = (0, 3, 4, 5, 2)
            for i in range( r_n ):
                row_data = []
                part_id_cell: QStandardItem = self.__table_modal.item( i, 1 )
                part_id = int( part_id_cell.text().lstrip( '0' ) )
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
                            QMessageBox.warning( self, '数据有误', f'\"{row_data[1]}\"的数量有误或为零，请确认！' )
                            return
                    else:
                        if cell is None:
                            row_data.append( '' )
                        else:
                            row_data.append( cell.text() )
                record = [row_data[0], part_id, row_data[-1], qty_value]
                data_4_paper.append( row_data )
                items_4_database.append( record )
            bill_name = self.__billNrLineEdit.text()
            data_4_database = [bill_name, self.__operatorLineEdit.text(), self.__timeSelector.text(),
                               '出库单', self.__from_storage, items_4_database]
            self.__database.create_picking_record( data_4_database )
            pdf_creator = PdfLib.CreatePickBill( data_4_paper, '中德OPS项目部' if self.__from_storage != 'F' else 'OPS项目部',
                                                 self.__operatorLineEdit.text(),
                                                 self.__timeSelector.text(), self.__billNrLineEdit.text() )
            # 选择要保存到的文件
            dlg = win32ui.CreateFileDialog( 0, None, f'{bill_name}.pdf', win32con.OFN_OVERWRITEPROMPT,
                                            'Pdf Files (*.pdf)|*.pdf||' )
            to_save_file = None
            if dlg.DoModal() == win32con.IDOK:
                to_save_file = dlg.GetPathName()
            if to_save_file is None:
                QMessageBox.warning( self, '取消', '终止输出！', QMessageBox.Ok )
                return
            if to_save_file.lower()[-4:] != '.pdf':
                to_save_file += '.pdf'
            pdf_creator.DoPrint( to_save_file )
            QMessageBox.information( self, '完成', '输出至 {0} 文件。'.format( to_save_file ), QMessageBox.Ok )
            self.close()
            resp = QMessageBox.question( self, '询问', f'是否打开{to_save_file}文件？', QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes )
            if resp == QMessageBox.Yes:
                os.startfile( to_save_file )
        except Exception as ex:
            QMessageBox.warning( self, '', str( ex ), QMessageBox.Ok )
        finally:
            self.__jl_erp_database.close()

    def __do_close(self):
        self.__jl_erp_database.close()
        self.close()

    def fill_import_cache(self, data):
        self.__one_import_data = data.copy()

    def is_zd_erp(self):
        """
        是否进行中德ERP的操作？
        :return: TRUE or FALSE
        """
        return self.__from_storage != 'F'


def run_function(the_database_setting):
    app = QApplication( sys.argv )
    database_handler = MssqlHandler( *the_database_setting[1:] )
    the_dialog = NCreatePickBillDialog( database_handler )
    the_dialog.show()
    sys.exit( app.exec_() )
