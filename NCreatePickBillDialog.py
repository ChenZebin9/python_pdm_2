# coding=gbk
from ui.CreatePickBillDialog import *
from PyQt5.QtWidgets import (QDialog, QApplication, QLineEdit, QDateEdit, QMessageBox, QFileDialog, QHeaderView)
from PyQt5.QtCore import (Qt, QDate)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
import sys
import clr
from excel.ExcelHandler import (ExcelHandler2)
from ui.NImportSettingDialog import (NImportSettingDialog)


class NCreatePickBillDialog(QDialog, Ui_Dialog):

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

    def __add_items(self):
        try:
            temp_names = QFileDialog.getOpenFileName(self, '选择数据文件', '', 'Excel files(*.xls)')
            if len(temp_names[0]) < 1:
                return
            file_name = temp_names[0]
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
        print('Remove items')

    def accept(self):
        try:
            pdf_creator = CreatePickBill(self.__one_import_data, 'OPS项目部', self.__operatorLineEdit.text(),
                                         self.__timeSelector.text(), self.__billNrLineEdit.text())
            pdf_creator.DoPrint('D:/aaa.pdf')
            print( '成功生成！' )
            self.close()
        except Exception as ex:
            QMessageBox.warning(self, '', str( ex ), QMessageBox.Ok )

    def closeEvent(self, event):
        event.accept()

    def fill_import_cache(self, data):
        self.__one_import_data = data.copy()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clr.FindAssembly( 'PdfLib.dll' )
    clr.AddReference( 'PdfLib' )
    from PdfLib import *
    theDialog = NCreatePickBillDialog(parent=None)
    theDialog.show()
    sys.exit(app.exec_())
