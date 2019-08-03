# coding=gbk
import sys

import clr
import win32con
import win32ui
from PyQt5.QtCore import (Qt, QDate, QModelIndex)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QDialog, QApplication, QLineEdit, QDateEdit, QMessageBox, QDialogButtonBox)

from excel.ExcelHandler import (ExcelHandler2)
from ui.CreatePickBillDialog import *
from ui.NImportSettingDialog import (NImportSettingDialog)


class NCreatePickBillDialog(QDialog, Ui_Dialog):

    """ 通过导入Excel文件的数据，实现巨轮的领料单的打印输出。 """

    Column_names = ('合同号', '物料描述', '单位', '数量', '备注')

    def __init__(self, parent=None):
        self.__parent = parent
        super(NCreatePickBillDialog, self).__init__(parent)
        self.__timeSelector = QDateEdit()
        self.__billNrLineEdit = QLineEdit()
        self.__operatorLineEdit = QLineEdit()
        self.__table_modal = QStandardItemModel()
        self.__one_import_data = []
        self.setup_ui()

    def setup_ui(self):
        super(NCreatePickBillDialog, self).setupUi(self)
        self.setLayout( self.mainVLayout )

        self.__timeSelector.setCalendarPopup(True)
        self.__timeSelector.setAlignment(Qt.AlignCenter)
        self.__timeSelector.setDate(QDate.currentDate())
        self.__billNrLineEdit.setAlignment(Qt.AlignCenter)
        self.__operatorLineEdit.setAlignment(Qt.AlignCenter)
        self.formLayout.addRow("日期：", self.__timeSelector)
        self.formLayout.addRow("单号：", self.__billNrLineEdit)
        self.formLayout.addRow("操作者：", self.__operatorLineEdit)

        self.midRightHL.setAlignment(Qt.AlignTop)

        self.addButton.clicked.connect(self.__add_items)
        self.removeButton.clicked.connect(self.__remove_item)

        self.__table_modal.setHorizontalHeaderLabels( NCreatePickBillDialog.Column_names )
        self.itemsTableView.setModel(self.__table_modal)

        self.theDialogButtonBox.clicked.connect(self.__buttonBox_clicked)

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
            excel = ExcelHandler2(file_name)
            dialog.set_excel_mode(NCreatePickBillDialog.Column_names, excel, True)
            dialog.exec_()
            if len(self.__one_import_data):
                for r in self.__one_import_data:
                    one_row_in_table = []
                    for i in range(len(NCreatePickBillDialog.Column_names)):
                        ii = QStandardItem(r[i])
                        one_row_in_table.append(ii)
                    self.__table_modal.appendRow(one_row_in_table)
                self.itemsTableView.resizeColumnsToContents()
        except Exception as ex:
            QMessageBox.warning(self, '', str(ex), QMessageBox.Ok)

    def __remove_item(self):
        resp = QMessageBox.question(self, '确认', '确定要移除这些行？', QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.No:
            return
        indexes = self.itemsTableView.selectedIndexes()
        removed_row_cc = 0
        row_to_remove = []
        for i in indexes:
            ii: QModelIndex = i
            row_to_remove.append(ii.row())
        row_to_remove.sort()
        for i in row_to_remove:
            self.__table_modal.removeRow(i - removed_row_cc)
            removed_row_cc += 1

    def __buttonBox_clicked(self, button):
        if button is self.theDialogButtonBox.button(QDialogButtonBox.Ok):
            self.__do_accept()
        elif button is self.theDialogButtonBox.button(QDialogButtonBox.Cancel):
            self.__do_close()

    def __do_accept(self):
        try:
            r_n = self.__table_modal.rowCount()
            if r_n < 1:
                raise Exception('没有要输出的数据')
            datas = []
            c_n = len(NCreatePickBillDialog.Column_names)
            for i in range(r_n):
                row_data = []
                for j in range(c_n):
                    cell: QStandardItem = self.__table_modal.item(i, j)
                    row_data.append(cell.text())
                datas.append(row_data)
            pdf_creator = CreatePickBill(datas, 'OPS项目部', self.__operatorLineEdit.text(),
                                         self.__timeSelector.text(), self.__billNrLineEdit.text())
            # 选择要保存到的文件
            dlg = win32ui.CreateFileDialog(0, None, None, win32con.OFN_OVERWRITEPROMPT, 'Pdf Files (*.pdf)|*.pdf||')
            to_save_file = None
            if dlg.DoModal() == win32con.IDOK:
                to_save_file = dlg.GetPathName()
            if to_save_file is None:
                QMessageBox.warning(self, '取消', '终止输出！', QMessageBox.Ok)
                return
            if to_save_file.lower()[-4:] != '.pdf':
                to_save_file += '.pdf'
            pdf_creator.DoPrint(to_save_file)
            QMessageBox.information(self, '完成', '输出至 {0} 文件。'.format(to_save_file), QMessageBox.Ok)
            self.close()
        except Exception as ex:
            QMessageBox.warning(self, '', str( ex ), QMessageBox.Ok )

    def __do_close(self):
        self.close()

    def fill_import_cache(self, data):
        self.__one_import_data = data.copy()


if __name__ == '__main__':
    clr.FindAssembly( 'dlls/PdfLib.dll' )
    clr.AddReference( 'dlls/PdfLib' )
    from PdfLib import CreatePickBill
    app = QApplication(sys.argv)
    theDialog = NCreatePickBillDialog(parent=None)
    theDialog.show()
    sys.exit(app.exec_())
