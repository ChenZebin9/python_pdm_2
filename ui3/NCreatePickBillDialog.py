# coding=gbk
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

clr.FindAssembly( 'dlls/PdfLib.dll' )
clr.AddReference( 'dlls/PdfLib' )
import PdfLib


class NCreatePickBillDialog( QDialog, Ui_Dialog ):
    """ 通过导入Excel文件的数据，实现巨轮的领料单的打印输出。 """

    Column_names = ('合同号', '零件号', '中德物料编码', '物料描述', '数量', '单位')

    def __init__(self, database, parent=None):
        self.__parent = parent
        self.__database: DatabaseHandler = database
        super( NCreatePickBillDialog, self ).__init__( parent )
        self.__timeSelector = QDateEdit()
        self.__billNrLineEdit = QLineEdit()
        self.__operatorLineEdit = QLineEdit()
        self.__table_modal = QStandardItemModel()
        self.__one_import_data = []
        self.setup_ui()

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

        self.__table_modal.setHorizontalHeaderLabels( NCreatePickBillDialog.Column_names )
        self.itemsTableView.setModel( self.__table_modal )

        self.theDialogButtonBox.clicked.connect( self.__buttonBox_clicked )

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
                        erp_code = the_part.get_specified_tag( database=self.__database, tag_name='巨轮中德ERP物料编码' )
                        if len( erp_code ) > 0:
                            one_row_in_table.append( QStandardItem( erp_code ) )
                            erp_info = self.__database.get_erp_data( erp_code )
                            one_row_in_table.append( QStandardItem( erp_info[1] ) )
                            one_row_in_table.append( QStandardItem( r[3] ) )
                            one_row_in_table.append( QStandardItem( erp_info[2] ) )
                    elif r[2] is not None and len( r[2] ) > 0:
                        one_row_in_table.append( QStandardItem( '' ) )
                        one_row_in_table.append( QStandardItem( r[2] ) )
                        erp_info = self.__database.get_erp_data( r[2] )
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
            datas = []
            c_n = (0, 3, 4, 5, 2)
            for i in range( r_n ):
                row_data = []
                for j in c_n:
                    cell: QStandardItem = self.__table_modal.item( i, j )
                    if cell is None:
                        row_data.append('')
                    else:
                        row_data.append( cell.text() )
                datas.append( row_data )
            pdf_creator = PdfLib.CreatePickBill( datas, '中德OPS项目部', self.__operatorLineEdit.text(),
                                                 self.__timeSelector.text(), self.__billNrLineEdit.text() )
            # 选择要保存到的文件
            dlg = win32ui.CreateFileDialog( 0, None, None, win32con.OFN_OVERWRITEPROMPT, 'Pdf Files (*.pdf)|*.pdf||' )
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
        except Exception as ex:
            QMessageBox.warning( self, '', str( ex ), QMessageBox.Ok )

    def __do_close(self):
        self.close()

    def fill_import_cache(self, data):
        self.__one_import_data = data.copy()


def run_function(the_database_setting):
    app = QApplication( sys.argv )
    database_handler = MssqlHandler( *the_database_setting[1:] )
    the_dialog = NCreatePickBillDialog( database_handler )
    the_dialog.show()
    sys.exit( app.exec_() )
