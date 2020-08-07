# coding=gbk
import sys

import win32con
import win32ui
from PyQt5.QtCore import (Qt, QDate, QModelIndex)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QDialog, QApplication, QLineEdit, QDateEdit, QLabel, QMessageBox, QDialogButtonBox)

from Part import Part
from excel.ExcelHandler import ExcelHandler2, ExcelHandler3
from ui.NImportSettingDialog import NImportSettingDialog
from ui3.CreateRequirementDialog import *


class NCreateRequirementDialog( QDialog, Ui_Dialog ):
    """
    ����������Ҫ�ĶԻ���
    """

    Column_names = ['�����', '����', '����', '�е����ϱ���', '��Դ', '����', '��ע']

    def __init__(self, parent=None, database=None, config_dict=None):
        self.__parent = parent
        self.__database = database
        self.__one_import_data = []
        super( NCreateRequirementDialog, self ).__init__( parent )
        self.who_do_this = QLabel( self )
        self.billNrLabel = QLabel( self )
        if config_dict is not None:
            if 'Operator' in config_dict:
                self.who_do_this.setText( config_dict['Operator'] )
        self.when_required = QDateEdit( self )
        self.commentLineEdit = QLineEdit( self )
        self.__data_modal = QStandardItemModel()
        self.setup_ui()
        self.init_data()

    def setup_ui(self):
        super( NCreateRequirementDialog, self ).setupUi( self )
        self.setLayout( self.v1_layout )
        self.v3_layout.setAlignment( Qt.AlignTop )
        self.f2_layout.addRow( '����', self.billNrLabel )
        self.f2_layout.addRow( '������', self.who_do_this )
        self.f2_layout.addRow( '����', self.when_required )
        self.when_required.setCalendarPopup( True )
        self.when_required.setDate( QDate.currentDate() )
        self.when_required.setAlignment( Qt.AlignCenter )
        self.f2_layout.addRow( 'ȫ�ֱ�ע', self.commentLineEdit )

        self.__data_modal.setHorizontalHeaderLabels( NCreateRequirementDialog.Column_names )
        self.dataTableView.setModel( self.__data_modal )

        # ��Ӧ����
        self.addItemButton.clicked.connect( self.__add_items )
        self.removeItemButton.clicked.connect( self.__remove_items )
        self.when_required.dateChanged.connect( self.__set_bill_num_auto )
        self.buttonBox.clicked.connect( self.__buttonBox_clicked )

    def init_data(self):
        self.__set_bill_num_auto()

    def __set_bill_num_auto(self):
        date_text = self.when_required.text()
        date_data = date_text.split( '/' )
        the_date = QDate( int( date_data[0] ), int( date_data[1] ), int( date_data[2] ) )
        bill_nr = 'K{0}'.format( the_date.toString( 'yyMMdd' ) )
        bills = self.__database.get_require_bill( prefix=bill_nr )
        if bills is None:
            self.billNrLabel.setText( bill_nr + '-1' )
        else:
            c = len( bills ) + 1
            self.billNrLabel.setText( bill_nr + '-' + str( c ) )

    def add_items(self, parts):
        """
        �ɹ��ⲿ�����������
        :param parts: [Part]
        :return:
        """
        for p in parts:
            part_id = p
            erp_id = self.__database.get_sub_tag_by_part_and_tag_name( p, '�����е�ERP���ϱ���' )
            self.__add_one_item( [part_id, erp_id, 0.0, None] )
        self.dataTableView.resizeColumnsToContents()

    def __add_one_item(self, data):
        """
        ���һ������
        :param data: [����ţ��е����ϱ��룬��������ע]
        :return:
        """
        one_row_in_table = []
        if data[0] is not None:
            tt = float( data[0] )
            part_id = int( tt )
            one_row_in_table.append( QStandardItem( '{:08d}'.format( part_id ) ) )
            the_part: Part = Part.get_parts( database=self.__database, part_id=part_id )[0]
            erp_code = the_part.get_specified_tag( database=self.__database, tag_name='�����е�ERP���ϱ���' )
            one_row_in_table.append( QStandardItem( the_part.name ) )
            one_row_in_table.append( QStandardItem( the_part.description ) )
            one_row_in_table.append( QStandardItem( erp_code ) )
            source = the_part.get_specified_tag( database=self.__database, tag_name='��Դ' )
            one_row_in_table.append( QStandardItem( source ) )
        else:
            one_row_in_table.append( QStandardItem( '00000001' ) )
            one_row_in_table.append( QStandardItem( '' ) )
            erp_code = data[1]
            item_description = self.__database.get_erp_data( erp_code )
            one_row_in_table.append( QStandardItem( item_description[1] ) )
            one_row_in_table.append( QStandardItem( erp_code ) )
            one_row_in_table.append( QStandardItem( '' ) )
        qty_data = ''
        if type( data[2] ) == float or type( data[2] ) == int:
            qty_data = '%.2f' % data[2]
        elif type( data[2] ) == str:
            f = float( data[2] )
            qty_data = "%.2f" % f
        one_row_in_table.append( QStandardItem( qty_data ) )
        one_row_in_table.append( QStandardItem( data[3] ) )
        self.__data_modal.appendRow( one_row_in_table )

    def __add_items(self):
        """
        �����Ӱ�ť����Ӧ����
        :return:
        """
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
            dialog = NImportSettingDialog( self, '��������', None )
            if selected_file[-3:].upper() == 'XLS':
                excel = ExcelHandler2( file_name )
            else:
                excel = ExcelHandler3( file_name )
            config_settings = ('�����', '���ϱ���', '����', '��ע')
            dialog.set_excel_mode( config_settings, excel, True )
            dialog.exec_()
            if len( self.__one_import_data ):
                for r in self.__one_import_data:
                    # ����ţ��е����ϱ��룬��������ע
                    self.__add_one_item( r )
                self.dataTableView.resizeColumnsToContents()
        except Exception as ex:
            QMessageBox.critical( self, '�����Ŀ����', str( ex ), QMessageBox.Ok, QMessageBox.Ok )

    def __remove_items(self):
        """
        ����Ƴ���ť����Ӧ����
        :return:
        """
        resp = QMessageBox.question( self, 'ȷ��', 'ȷ��Ҫ�Ƴ���Щ�У�', QMessageBox.Yes | QMessageBox.No, QMessageBox.No )
        if resp == QMessageBox.No:
            return
        indexes = self.dataTableView.selectedIndexes()
        removed_row_cc = 0
        row_to_remove = []
        for i in indexes:
            ii: QModelIndex = i
            row_to_remove.append( ii.row() )
        row_to_remove.sort()
        for i in row_to_remove:
            self.__data_modal.removeRow( i - removed_row_cc )
            removed_row_cc += 1

    def fill_import_cache(self, data):
        """
        �����������ķ���
        :param data:
        :return:
        """
        self.__one_import_data = data.copy()

    def __buttonBox_clicked(self, button):
        if button is self.buttonBox.button( QDialogButtonBox.Ok ):
            self.__do_accept()
        elif button is self.buttonBox.button( QDialogButtonBox.Cancel ):
            self.__do_close()

    def __do_accept(self):
        """
        ��� OK ��ť����Ӧ����
        :return:
        """
        try:
            # �����嵥
            operator = self.who_do_this.text()
            if operator is None or len( operator ) < 1:
                operator = '(����)'
            bill_name = self.billNrLabel.text()
            the_date = self.when_required.text()
            the_bill_data = [bill_name, the_date, operator]
            # �����嵥��Ŀ
            r_n = self.__data_modal.rowCount()
            if r_n < 1:
                raise Exception( 'û��Ҫ���������' )
            items_data = []
            global_comment = self.commentLineEdit.text()
            if global_comment is None or len( global_comment ) < 1:
                global_comment = None
            for i in range( r_n ):
                row_data = []
                cell: QStandardItem = self.__data_modal.item( i, 0 )
                part_id = int( cell.text().lstrip( '0' ) )
                row_data.append( part_id )
                cell: QStandardItem = self.__data_modal.item( i, 3 )
                if cell.text() is None or len( cell.text() ) < 1:
                    row_data.append( None )
                else:
                    row_data.append( cell.text() )
                cell: QStandardItem = self.__data_modal.item( i, 5 )
                may_error = False
                qty_value = 0.0
                if cell is None:
                    may_error = True
                else:
                    qty_value = float( cell.text() )
                    if qty_value <= 0:
                        may_error = True
                if may_error:
                    raise Exception( f'\"{row_data[0]}/{row_data[1]}\"�����������Ϊ�㣬��ȷ�ϣ�' )
                else:
                    row_data.append( qty_value )
                cell: QStandardItem = self.__data_modal.item( i, 6 )
                item_comment = ''
                if global_comment is not None:
                    item_comment = global_comment
                if cell.text() is not None and len( cell.text() ) > 0:
                    item_comment += ' {0}'.format( cell.text() )
                row_data.append( item_comment )
                items_data.append( row_data )
            self.__database.insert_requirements( the_bill_data, items_data )
            QMessageBox.information( self, '���', '��������������ɣ�', QMessageBox.Ok, QMessageBox.Ok )
            self.close()
        except Exception as e:
            QMessageBox.warning( self, '', str( e ), QMessageBox.Ok, QMessageBox.Ok )

    def closeEvent(self, event):
        self.parent().flag_when_requirement_dialog_close()
        event.accept()

    def __do_close(self):
        """
        ��� Cancel ��ť����Ӧ����
        :return:
        """
        self.close()


if __name__ == '__main__':
    app = QApplication( sys.argv )
    config = {'Operator': '�����'}
    the_dialog = NCreateRequirementDialog( parent=None, database=None, config_dict=config )
    the_dialog.show()
    sys.exit( app.exec_() )
