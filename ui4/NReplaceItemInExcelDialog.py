# coding=gbk

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QComboBox, QHeaderView, QMessageBox, QTableWidget, QCheckBox, \
    QAbstractItemView

from ui4.NAssemblyToolWindow import PartSelectDialog
from Part import Part
from db.DatabaseHandler import DatabaseHandler
from ui4.ReplaceItemInExcelDialog import Ui_Dialog
import xlwings as xw


class NReplaceItemInExcelDialog(QDialog, Ui_Dialog):
    RightButtonWidth = 80
    BottomButtonWidth = 80
    Alphabet = ('A', 'B', 'C', 'D', 'E', 'F', 'G',
                'H', 'I', 'J', 'K', 'L', 'M', 'N',
                'O', 'P', 'Q', 'R', 'S', 'T',
                'U', 'V', 'W', 'X', 'Y', 'Z')

    def __init__(self, parent, database: DatabaseHandler):
        super(NReplaceItemInExcelDialog, self).__init__(parent)
        self.__database: DatabaseHandler = database
        self.__columns = (
            '序号', '名称', '描述', '数量', '类别', '品牌', '标准', '巨轮中德ERP物料编码', '巨轮智能ERP物料编码',
            '外部编码',
            '来源', '单位', '产品', '配料策略', '统计策略')
        self.__mode_widget_group = []
        self.__project_1_mode = {1: 0, 2: 1, 3: 2, 4: 4, 5: 6, 6: 5, 7: 9, 8: 7, 9: 10, 10: 13, 11: 3, 12: 11}
        self.__project_2_mode = {1: 0, 2: 1, 3: 2, 4: 5, 5: 6, 6: 11, 7: 3, 8: 7, 12: 4, 13: 13}
        self.setup_ui()

    def setup_ui(self):
        super(NReplaceItemInExcelDialog, self).setupUi(self)
        self.groupBox.setLayout(self.g_v_layout)
        self.__mode_widget_group = [self.listMode1CheckButton, self.listMode2CheckButton]
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setLayout(self.m_v_layout)
        self.b_h_layout.setAlignment(Qt.AlignRight)
        self.insertButton.setFixedWidth(NReplaceItemInExcelDialog.RightButtonWidth)
        self.removeButton.setFixedWidth(NReplaceItemInExcelDialog.RightButtonWidth)
        self.searchButton.setFixedWidth(NReplaceItemInExcelDialog.BottomButtonWidth)
        self.closeButton.setFixedWidth(NReplaceItemInExcelDialog.BottomButtonWidth)

        self.projectTableWidget.setColumnCount(3)
        self.projectTableWidget.setHorizontalHeaderLabels(['列数', '数据', '默认值'])
        self.add_column_project()

        QTableWidget.resizeColumnsToContents(self.projectTableWidget)
        self.projectTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.closeButton.clicked.connect(self.close)
        self.searchButton.clicked.connect(self.do_search)
        self.insertButton.clicked.connect(self.add_column_project)
        self.removeButton.clicked.connect(self.remove_column_project)
        for w in self.__mode_widget_group:
            the_w: QCheckBox = w
            the_w.stateChanged.connect(self.project_mode_changed)

    def project_mode_changed(self, status):
        """
        对应清单对应表变更响应函数
        :param status:
        :return:
        """
        the_w: QCheckBox = self.sender()
        if status:
            i = self.__mode_widget_group.index(the_w)
            self.__fill_project_table(i)
            for w in self.__mode_widget_group:
                if w is the_w:
                    continue
                w.setCheckState(False)
        self.insertButton.setEnabled(not status)
        self.removeButton.setEnabled(not status)
        self.projectTableWidget.setEditTriggers(
            QAbstractItemView.NoEditTriggers if status else QAbstractItemView.AllEditTriggers)
        for r in range(self.projectTableWidget.rowCount()):
            w: QComboBox = self.projectTableWidget.cellWidget(r, 1)
            w.setEnabled(not status)

    def __fill_project_table(self, mode):
        """
        填写对应列表
        :param mode:
        :return:
        """
        p_t = {}
        if mode == 0:
            p_t = self.__project_1_mode
        elif mode == 1:
            p_t = self.__project_2_mode
        _l = len(p_t.keys())
        if _l < 1:
            return
        self.projectTableWidget.setRowCount(0)
        i = 0
        for k in p_t.keys():
            c_n = NReplaceItemInExcelDialog.Alphabet[k - 1]
            c_i = p_t[k]
            self.add_column_project(c1=c_n, c2=c_i)

    def close(self) -> bool:
        return super(NReplaceItemInExcelDialog, self).close()

    def do_search(self):
        try:
            project_dict = {}
            for i in range(self.projectTableWidget.rowCount()):
                i_widget: QComboBox = self.projectTableWidget.cellWidget(i, 1)
                if i_widget.currentIndex() >= 0:
                    i_column_item = self.projectTableWidget.item(i, 0)
                    i_column = int(NReplaceItemInExcelDialog.Alphabet.index(i_column_item.text()) + 1)
                    default_value_item = self.projectTableWidget.item(i, 2)
                    default_value = default_value_item.text()
                    project_dict[i_widget.currentText()] = (i_column, default_value)
            if '序号' not in project_dict.keys():
                raise Exception('没有设定<序号>列。')
            if '数量' not in project_dict.keys():
                raise Exception('没有设定<数量>列。')
            wb = xw.books.active
            select_range = wb.selection
            select_row_index = select_range.row  # 仅识别第一个单元格的行号
            id_column = project_dict['序号'][0]
            part_id = int(xw.Range((select_row_index, id_column)).value)
            qty_column = project_dict['数量'][0]
            part_qty = project_dict['数量'][1]
            if qty_column != 0:
                part_qty = xw.Range((select_row_index, qty_column)).value

            identical_parts = self.__database.get_identical_parts(part_id, keep_original=1)
            if identical_parts is None or len(identical_parts[0]) < 1:
                raise Exception('没有可代替的物料！')
            part_dict = {}
            for p_id in identical_parts[0]:
                ps = Part.get_parts(self.__database, part_id=p_id)
                if len(ps) > 0:
                    p: Part = ps[0]
                    part_dict[p] = part_qty
            part_id_format = '{:08d}'.format(part_id)
            dialog = PartSelectDialog(self, self.__database, part_dict)
            dialog.setWindowTitle(f'选择替代 <{part_id_format}> 的零件')
            resp = dialog.exec_()
            if resp != QDialog.Accepted:
                return
            neu_p: Part = dialog.selected_data[0]
            if neu_p.get_part_id() == part_id:
                raise Exception('选择了物料本身，无进行替代。')
            for k in project_dict:
                v = project_dict[k][0]  # 列位置
                if k == '序号':
                    xw.Range((select_row_index, v)).value = neu_p.get_part_id()
                elif k == '名称':
                    xw.Range((select_row_index, v)).value = neu_p.name
                elif k == '描述':
                    xw.Range((select_row_index, v)).value = neu_p.description
                elif k == '数量':
                    continue
                else:
                    tag_value = neu_p.get_specified_tag(self.__database, k)
                    xw.Range((select_row_index, v)).value = tag_value
        except Exception as ex:
            QMessageBox.warning(self, '搜索时异常', str(ex))

    def add_column_project(self, c1='A', c2=-1, c3=''):
        r_c = self.projectTableWidget.rowCount()
        self.projectTableWidget.insertRow(r_c)
        column_index_item = QTableWidgetItem(c1)
        column_index_item.setTextAlignment(Qt.AlignCenter)
        self.projectTableWidget.setItem(r_c, 0, column_index_item)
        combo = QComboBox()
        combo.addItems(self.__columns)
        combo.setCurrentIndex(c2)
        combo.setStyleSheet('QComboBox{margin:3px}')
        self.projectTableWidget.setCellWidget(r_c, 1, combo)
        default_value_item = QTableWidgetItem(c3)
        default_value_item.setTextAlignment(Qt.AlignCenter)
        self.projectTableWidget.setItem(r_c, 2, default_value_item)

    def remove_column_project(self):
        rc = self.projectTableWidget.currentRow()
        if rc >= 0:
            self.projectTableWidget.removeRow(rc)
