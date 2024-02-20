from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (QDialog, QTableWidgetItem, QComboBox, QTableWidget, QMessageBox)

from Part import (Part, Tag)
from excel import ExcelHandler
from ui.ImportSettingDialog import *


class NImportSettingDialog(QDialog, Ui_Dialog):
    """
    self.__general_use = True 时，父对象，需要有fill_import_cache( self, _data, sheet_name )函数
    """

    def __init__(self, parent=None, title=None, database=None):
        self.__parent = parent
        self.__database = database
        super(NImportSettingDialog, self).__init__(parent)
        self.__title = title
        self.setup_ui()
        self.__mode = 'TXT'
        self.__txt_data = []
        self.__result = None
        self.__excel_file: ExcelHandler = None
        self.__default_data = None
        self.__excel_data = None
        self.__general_use = False
        self.__row_index_control = False
        self.__begin_row_index = 0
        self.__end_row_index = 65536

    def setup_ui(self):
        super(NImportSettingDialog, self).setupUi(self)
        if self.__title is not None:
            self.setWindowTitle(self.__title)
        self.v_box.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.v_box)
        self.sheetComboBox.currentIndexChanged.connect(self.__on_changed_index)
        self.beginRowLineEdit.setAlignment(Qt.AlignCenter)
        self.endLineEdit.setAlignment(Qt.AlignCenter)
        self.rowLimitCheckBox.stateChanged.connect(self.__set_row_line_edit_enable)

    def closeEvent(self, event):
        if self.__excel_file is not None:
            self.__excel_file.close()
        event.accept()

    def __set_row_line_edit_enable(self, is_checked):
        self.__row_index_control = is_checked
        self.beginRowLineEdit.setEnabled(is_checked)
        self.endLineEdit.setEnabled(is_checked)

    def __on_changed_index(self):
        if self.__excel_file is None:
            return
        count = self.dataConfigTableWidget.rowCount()
        if count < 1:
            return
        sheet_name = self.sheetComboBox.currentText()
        ss = self.__excel_file.get_datas(sheet_name)

        # 行设置
        row_n = self.__excel_file.get_max_rows(sheet_name)
        row_validator = QIntValidator(1, row_n)
        self.beginRowLineEdit.setText('1')
        self.beginRowLineEdit.setValidator(row_validator)
        self.endLineEdit.setText(str(row_n))
        self.endLineEdit.setValidator(row_validator)

        self.__excel_data = ss[1]
        for i in range(0, count):
            combo: QComboBox = self.dataConfigTableWidget.cellWidget(i, 1)
            combo.clear()
            combo.addItems(ss[0])
            combo.setCurrentIndex(-1)

    def accept(self):
        if self.__mode == 'EXCEL':
            self.__begin_row_index = int(self.beginRowLineEdit.text())
            self.__end_row_index = int(self.endLineEdit.text())
        ps = []
        n = ''
        count = self.dataConfigTableWidget.rowCount()
        column_text = ''
        if not self.__general_use:
            for i in range(0, count):
                combo: QComboBox = self.dataConfigTableWidget.cellWidget(i, 1)
                if combo.currentIndex() >= 0:
                    column_text = combo.currentText()
                    item: QTableWidgetItem = self.dataConfigTableWidget.item(i, 0)
                    n = item.text()
                    break
            all_data = None
            if self.__mode == 'TXT':
                all_data = self.__txt_data
            elif self.__mode == 'EXCEL' and not self.__general_use:
                all_data = self.__excel_data[column_text]
            if n == '零件号':
                for nn in all_data:
                    try:
                        if self.__mode == 'EXCEL':
                            if not self.__check_if_in_row_control(nn[0]):
                                continue
                            if type(nn[1]) == str:
                                nnn = nn[1].lstrip('0')
                                if len(nnn) < 1:
                                    continue
                            else:
                                nnn = f'{nn[1]}'
                        else:
                            nnn = nn.lstrip('0')
                        p_id = int(nnn.split('.')[0])
                        p = Part.get_parts(database=self.__database, part_id=p_id)
                        ps.extend(p)
                    except Exception as ex:
                        QMessageBox.warning(self, '数据异常', ex.__str__())
            else:
                t = Tag.get_tags(database=self.__database, name=n)
                if len(t) < 1:
                    raise Exception('没有对应的父标签')
                for nn in all_data:
                    if not self.__check_if_in_row_control(nn[0]):
                        continue
                    tt = Tag.get_tags(database=self.__database, name=nn[1], parent_id=t[0].tag_id)
                    if len(tt) < 1:
                        print('没有对应的Tag： ' + nn[1])
                        continue
                    p = Part.get_parts_from_tag(self.__database, tag_id=tt[0].tag_id)
                    if len(p) > 1:
                        for pp in p:
                            print(pp.part_id)
                    ps.extend(p)
            self.__parent.show_parts_from_outside(ps)
        else:
            # 获取默认值
            real_default_data = []
            for i in range(0, count):
                cell_item: QTableWidgetItem = self.dataConfigTableWidget.item(i, 2)
                real_default_data.append(cell_item.text())
            columns_text = []
            for i in range(0, count):
                combo: QComboBox = self.dataConfigTableWidget.cellWidget(i, 1)
                if combo.currentIndex() < 0:
                    columns_text.append(None)
                else:
                    columns_text.append(combo.currentText())
            c_count = len(columns_text)
            self.__result = []
            ref_key = list(self.__excel_data.keys())[0]
            ref_column_data = self.__excel_data[ref_key]
            cc = len(ref_column_data)
            for i in range(0, cc):
                temp_record = []
                ref_cell = ref_column_data[i]
                if not self.__check_if_in_row_control(ref_cell[0]):
                    continue
                for j in range(0, c_count):
                    column_header = columns_text[j]
                    if column_header is None:
                        temp_record.append(real_default_data[j])
                    else:
                        cell_data = self.__excel_data[column_header][i][1]
                        temp_record.append(cell_data)
                self.__result.append(temp_record)
            the_sheet_name = self.sheetComboBox.currentText()
            self.__parent.fill_import_cache(self.__result, sheet_name=the_sheet_name)
        self.close()

    def __check_if_in_row_control(self, row_nr):
        if self.__row_index_control:
            if self.__begin_row_index <= row_nr <= self.__end_row_index:
                return True
            else:
                return False
        else:
            return True

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

    def set_excel_mode(self, rows, excel_file, general_use=False, default_data=None):
        self.__mode = 'EXCEL'
        self.__excel_file = excel_file
        self.__general_use = general_use
        self.__default_data = default_data
        self.sheetComboBox.addItems(excel_file.get_sheets_name())
        self.dataConfigTableWidget.setColumnCount(3)
        self.dataConfigTableWidget.setHorizontalHeaderLabels(['类型', '数据', '默认值'])
        self.dataConfigTableWidget.setRowCount(len(rows))
        index = 0
        ll = len(rows)
        for i in range(0, ll):
            r = rows[i]
            item = QTableWidgetItem(r)
            item.setTextAlignment(Qt.AlignRight)
            self.dataConfigTableWidget.setItem(index, 0, item)
            combo = QComboBox()
            combo.setStyleSheet('QComboBox{margin:3px}')
            self.dataConfigTableWidget.setCellWidget(index, 1, combo)
            if default_data is not None:
                vv = default_data[i]
                if vv is None:
                    vv = ''
            else:
                vv = ''
            default_value_item = QTableWidgetItem(vv)
            item.setTextAlignment(Qt.AlignCenter)
            self.dataConfigTableWidget.setItem(index, 2, default_value_item)
            index += 1
        QTableWidget.resizeColumnToContents(self.dataConfigTableWidget, 0)
        QTableWidget.resizeRowsToContents(self.dataConfigTableWidget)
        self.sheetComboBox.setCurrentIndex(0)
        self.__on_changed_index()
