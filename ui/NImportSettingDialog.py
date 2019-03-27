from ui.ImportSettingDialog import *
from PyQt5.QtWidgets import (QDialog, QTableWidgetItem, QComboBox, QTableWidget)
from PyQt5.QtCore import Qt
from Part import (Part, Tag)


class NImportSettingDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None, title=None, database=None):
        self.__parent = parent
        self.__database = database
        super(NImportSettingDialog, self).__init__(parent)
        self.__title = title
        self.setup_ui()
        self.__mode = 'TXT'
        self.__txt_data = []
        self.__result = None
        self.__excel_file = None
        self.__excel_data = None

    def setup_ui(self):
        super(NImportSettingDialog, self).setupUi(self)
        if self.__title is not None:
            self.setWindowTitle(self.__title)
        self.v_box.setContentsMargins(5, 5, 5, 5)
        self.setLayout( self.v_box )
        self.sheetComboBox.currentIndexChanged.connect(self.__on_changed_index)

    def closeEvent(self, event):
        if self.__excel_file is not None:
            self.__excel_file.close()
        event.accept()

    def __on_changed_index(self):
        if self.__excel_file is None:
            return
        count = self.dataConfigTableWidget.rowCount()
        if count < 1:
            return
        sheet_name = self.sheetComboBox.currentText()
        ss = self.__excel_file.get_datas(sheet_name)
        self.__excel_data = ss[1]
        for i in range(0, count):
            combo: QComboBox = self.dataConfigTableWidget.cellWidget(i, 1)
            combo.clear()
            combo.addItems(ss[0])
            combo.setCurrentIndex(-1)

    def accept(self):
        ps = []
        n = ''
        count = self.dataConfigTableWidget.rowCount()
        column_text = ''
        for i in range( 0, count ):
            combo: QComboBox = self.dataConfigTableWidget.cellWidget( i, 1 )
            if combo.currentIndex() >= 0:
                column_text = combo.currentText()
                item: QTableWidgetItem = self.dataConfigTableWidget.item( i, 0 )
                n = item.text()
                break
        all_data = None
        if self.__mode == 'TXT':
            all_data = self.__txt_data
        elif self.__mode == 'EXCEL':
            all_data = self.__excel_data[column_text]
        if n == '零件号':
            for nn in all_data:
                if type(nn) == str:
                    nn = nn.lstrip('0')
                    if len(nn) < 1:
                        continue
                p_id = int(nn)
                p = Part.get_parts(database=self.__database, part_id=p_id)
                ps.extend(p)
        else:
            t = Tag.get_tags(database=self.__database, name=n)
            if len(t) < 1:
                raise Exception('没有对应的父标签')
            for nn in all_data:
                tt = Tag.get_tags(database=self.__database, name=nn, parent_id=t[0].tag_id)
                if len(tt) < 1:
                    print('没有对应的Tag： ' + nn)
                    continue
                p = Part.get_parts_from_tag(self.__database, tag_id=tt[0].tag_id)
                ps.extend(p)
        self.__parent.show_parts_from_outside(ps)
        self.close()

    def get_result(self):
        return self.__result

    def set_txt_mode(self, rows, file_name):
        self.__mode = 'TXT'
        self.sheetComboBox.setEnabled(False)
        f = open(file_name, 'r')
        lines = f.readlines()
        for line in lines:
            self.__txt_data.append(line.strip())
        f.close()
        self.dataConfigTableWidget.setColumnCount(2)
        self.dataConfigTableWidget.setHorizontalHeaderLabels(['类型', '数据'])
        self.dataConfigTableWidget.setRowCount(len(rows))
        index = 0
        for r in rows:
            item = QTableWidgetItem(r)
            self.dataConfigTableWidget.setItem(index, 0, item)
            combo = QComboBox()
            combo.addItem('数据')
            combo.setStyleSheet('QComboBox{margin:3px}')
            combo.setCurrentIndex(-1)
            self.dataConfigTableWidget.setCellWidget(index, 1, combo)
            index += 1
        QTableWidget.resizeColumnToContents(self.dataConfigTableWidget, 0)
        QTableWidget.resizeRowsToContents(self.dataConfigTableWidget)

    def set_excel_mode(self, rows, excel_file):
        self.__mode = 'EXCEL'
        self.__excel_file = excel_file
        self.sheetComboBox.addItems(excel_file.get_sheets_name())
        self.dataConfigTableWidget.setColumnCount( 2 )
        self.dataConfigTableWidget.setHorizontalHeaderLabels( ['类型', '数据'] )
        self.dataConfigTableWidget.setRowCount( len( rows ) )
        index = 0
        for r in rows:
            item = QTableWidgetItem(r)
            item.setTextAlignment(Qt.AlignRight)
            self.dataConfigTableWidget.setItem(index, 0, item)
            combo = QComboBox()
            combo.setStyleSheet( 'QComboBox{margin:3px}' )
            self.dataConfigTableWidget.setCellWidget( index, 1, combo )
            index += 1
        QTableWidget.resizeColumnToContents( self.dataConfigTableWidget, 0 )
        QTableWidget.resizeRowsToContents( self.dataConfigTableWidget )
        self.sheetComboBox.setCurrentIndex( 0 )
        self.__on_changed_index()
