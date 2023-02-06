# coding=gbk

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QComboBox, QHeaderView, QMessageBox, QTableWidget

from ui4.NAssemblyToolWindow import PartSelectDialog
from Part import Part
from db.DatabaseHandler import DatabaseHandler
from ui4.ReplaceItemInExcelDialog import Ui_Dialog
import xlwings as xw


class NReplaceItemInExcelDialog(QDialog, Ui_Dialog):

    def __init__(self, parent, database: DatabaseHandler):
        super(NReplaceItemInExcelDialog, self).__init__(parent)
        self.__database: DatabaseHandler = database
        self.__columns = (
            '���', '����', '����', '����', '���', 'Ʒ��', '��׼', '�����е�ERP���ϱ���', '��������ERP���ϱ���',
            '�ⲿ����',
            '��Դ', '��λ', '��Ʒ', '���ϲ���', 'ͳ�Ʋ���')
        self.setup_ui()

    def setup_ui(self):
        super(NReplaceItemInExcelDialog, self).setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setLayout(self.m_v_layout)
        self.v_layout.setAlignment(Qt.AlignTop)
        self.b_h_layout.setAlignment(Qt.AlignRight)
        self.insertButton.setFixedWidth(40)
        self.removeButton.setFixedWidth(40)
        self.searchButton.setFixedWidth(80)
        self.closeButton.setFixedWidth(80)

        self.projectTableWidget.setColumnCount(3)
        self.projectTableWidget.setHorizontalHeaderLabels(['����', '����', 'Ĭ��ֵ'])
        self.projectTableWidget.setRowCount(2)

        column_index = 1
        ll = len(self.__columns)
        for i in range(0, 2):
            column_index_item = QTableWidgetItem(str(column_index))
            column_index_item.setTextAlignment(Qt.AlignCenter)
            self.projectTableWidget.setItem(i, 0, column_index_item)
            combo = QComboBox()
            combo.addItems(self.__columns)
            combo.setCurrentIndex(-1)
            combo.setStyleSheet('QComboBox{margin:3px}')
            self.projectTableWidget.setCellWidget(i, 1, combo)
            default_value_item = QTableWidgetItem('')
            default_value_item.setTextAlignment(Qt.AlignCenter)
            self.projectTableWidget.setItem(i, 2, default_value_item)
            column_index += 1
        QTableWidget.resizeColumnsToContents(self.projectTableWidget)
        self.projectTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.closeButton.clicked.connect(self.close)
        self.searchButton.clicked.connect(self.do_search)
        self.insertButton.clicked.connect(self.add_column_project)
        self.removeButton.clicked.connect(self.remove_column_project)

    def close(self) -> bool:
        return super(NReplaceItemInExcelDialog, self).close()

    def do_search(self):
        try:
            project_dict = {}
            for i in range(self.projectTableWidget.rowCount()):
                i_widget: QComboBox = self.projectTableWidget.cellWidget(i, 1)
                if i_widget.currentIndex() >= 0:
                    i_column_item = self.projectTableWidget.item(i, 0)
                    i_column = int(i_column_item.text())
                    default_value_item = self.projectTableWidget.item(i, 2)
                    default_value = default_value_item.text()
                    project_dict[i_widget.currentText()] = (i_column, default_value)
            if '���' not in project_dict.keys():
                raise Exception('û���趨<���>�С�')
            if '����' not in project_dict.keys():
                raise Exception('û���趨<����>�С�')
            wb = xw.books.active
            select_range = wb.selection
            select_row_index = select_range.row  # ��ʶ���һ����Ԫ����к�
            id_column = project_dict['���'][0]
            part_id = int(xw.Range((select_row_index, id_column)).value)
            qty_column = project_dict['����'][0]
            part_qty = project_dict['����'][1]
            if qty_column != 0:
                part_qty = xw.Range((select_row_index, qty_column)).value

            identical_parts = self.__database.get_identical_parts(part_id, keep_original=1)
            if identical_parts is None or len(identical_parts[0]) < 1:
                raise Exception('û�пɴ�������ϣ�')
            part_dict = {}
            for p_id in identical_parts[0]:
                ps = Part.get_parts(self.__database, part_id=p_id)
                if len(ps) > 0:
                    p: Part = ps[0]
                    part_dict[p] = part_qty
            part_id_format = '{:08d}'.format(part_id)
            dialog = PartSelectDialog(self, self.__database, part_dict)
            dialog.setWindowTitle(f'ѡ����� <{part_id_format}> �����')
            resp = dialog.exec_()
            if resp != QDialog.Accepted:
                return
            neu_p: Part = dialog.selected_data[0]
            if neu_p.get_part_id() == part_id:
                raise Exception('ѡ�������ϱ����޽��������')
            for k in project_dict:
                v = project_dict[k][0]  # ��λ��
                if k == '���':
                    xw.Range((select_row_index, v)).value = neu_p.get_part_id()
                elif k == '����':
                    xw.Range((select_row_index, v)).value = neu_p.name
                elif k == '����':
                    xw.Range((select_row_index, v)).value = neu_p.description
                elif k == '����':
                    continue
                else:
                    tag_value = neu_p.get_specified_tag(self.__database, k)
                    xw.Range((select_row_index, v)).value = tag_value
            # QMessageBox.information(self, '', '��������')
        except Exception as ex:
            QMessageBox.warning(self, '�쳣', str(ex))

    def add_column_project(self):
        r_c = self.projectTableWidget.rowCount()
        self.projectTableWidget.setRowCount(r_c + 1)
        column_index_item = QTableWidgetItem('0')
        column_index_item.setTextAlignment(Qt.AlignCenter)
        self.projectTableWidget.setItem(r_c, 0, column_index_item)
        combo = QComboBox()
        combo.addItems(self.__columns)
        combo.setCurrentIndex(-1)
        combo.setStyleSheet('QComboBox{margin:3px}')
        self.projectTableWidget.setCellWidget(r_c, 1, combo)
        default_value_item = QTableWidgetItem('')
        default_value_item.setTextAlignment(Qt.AlignCenter)
        self.projectTableWidget.setItem(r_c, 2, default_value_item)

    def remove_column_project(self):
        pass
