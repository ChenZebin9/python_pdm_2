# coding=gbk

from PyQt5.QtCore import (Qt, QDate, QItemSelectionModel, QModelIndex)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QCursor)
from PyQt5.QtWidgets import (QDialog, QAbstractItemView, QMenu, QMessageBox)

from ui3.HandlePickMaterialDialog import *
from Com import str_2_dict


class NHandlePickMaterialDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None, database=None, operator=None):
        self.__parent = parent
        self.__database = database
        self.__operator = operator
        # 列表的数据
        self.__material_data = QStandardItemModel()
        super(NHandlePickMaterialDialog, self).__init__(parent)
        super(NHandlePickMaterialDialog, self).setupUi(self)

        # 右键菜单
        self.__menu_4_material_table_edit = QMenu(parent=self.materialTableView)
        self.__roll_back_material_action = self.__menu_4_material_table_edit.addAction('退料')

        self.setModal(True)
        self.setup_ui()
        self.init_data()

        # 将要被处理的数据
        self.__selected_indexes = None
        self.__material_2_be_handled = []

    def setup_ui(self):
        self.setWindowTitle('退料')
        self.setLayout(self.v_1_layout)

        self.beginDateEdit.setCalendarPopup(True)
        self.endDateEdit.setCalendarPopup(True)
        self.beginDateEdit.dateChanged.connect(self.__update_material_list)
        self.endDateEdit.dateChanged.connect(self.__update_material_list)

        self.materialTableView.setModel(self.__material_data)
        self.materialTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.materialTableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.materialTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置右键菜单
        self.__roll_back_material_action.triggered.connect(self.__do_roll_back)
        self.materialTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.materialTableView.customContextMenuRequested.connect(self.__on_custom_context_menu_requested)

    def init_data(self):
        today = QDate.currentDate()
        self.endDateEdit.setDate(today)
        self.beginDateEdit.setDate(today.addDays(-15))
        self.__update_material_list()
        self.materialTableView.setFocus()

    def __on_custom_context_menu_requested(self, pos):
        if self.sender() is self.materialTableView:
            self.__material_2_be_handled.clear()
            select_model: QItemSelectionModel = self.materialTableView.selectionModel()
            indexes = select_model.selectedIndexes()
            self.__selected_indexes = indexes
            c = int(len(indexes))
            if c > 0:
                cc = int(len(indexes) / 10)
                for i in range(cc):
                    record_id_item: QStandardItem = self.__material_data.itemFromIndex(indexes[i * 10 + 9])
                    self.__material_2_be_handled.append(record_id_item.data(Qt.DisplayRole))
                self.__menu_4_material_table_edit.exec(QCursor.pos())

    def __do_roll_back(self):
        """
        进行实质上的退库工作
        :return:
        """
        resp = QMessageBox.question(self, '询问', '是否要将选定的数据进行退料处理？',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp == QMessageBox.No:
            return
        today = QDate.currentDate()
        bill_name = 'P{0}'.format(today.toString('yyMMdd'))
        bill_name = self.__database.get_available_supply_operation_bill(bill_name)
        self.__database.create_put_back_material_record(
            bill_name, self.__operator, today.toString('yyyy-MM-dd'), self.__material_2_be_handled)
        QMessageBox.information(self, '', '完成退料的操作。', QMessageBox.Yes)
        c = int(len(self.__selected_indexes) / 10)
        for i in range(c):
            first_index: QModelIndex = self.__selected_indexes[i * 10]
            self.__material_data.removeRow(first_index.row())

    def __update_material_list(self):
        pick_records = self.__database.get_pick_material_record(self.beginDateEdit.text(), self.endDateEdit.text())
        self.__material_data.clear()
        self.__material_data.setHorizontalHeaderLabels(
            ['单号', '项目号', '零件号', '描述', '日期', '数量', '合同号', '仓位', '金额', '记录号'])
        if pick_records is None:
            return
        for r in pick_records:
            other_data_s = str_2_dict(r[6])
            if 'RollBack' in other_data_s:
                if other_data_s['RollBack'] == 'Y':
                    # 已被退料的就不要再显示了
                    continue
            erp_code = r[3]
            if float(r[5]) < 0.0:
                # 数量小于0，也不要显示
                continue
            # 单据号、（需求）项目号、零件号
            one_row_in_table = [QStandardItem(r[0]), QStandardItem('{0}'.format(r[1])),
                                QStandardItem('{:08d}'.format(r[2]))]
            part_info = self.__database.get_part_info_quick(r[2])
            if part_info is None:
                raise Exception('没有该零件号的相关信息。')
            description = ' '.join(part_info[:3])
            # 零件的描述
            one_row_in_table.append(QStandardItem(description.strip()))
            # 操作的日期
            one_row_in_table.append(QStandardItem(r[4].strftime('%Y/%m/%d')))
            # 数量
            qty_item = QStandardItem(r[5])
            qty_item.setData(float(r[5]), Qt.DisplayRole)
            one_row_in_table.append(qty_item)
            # 其它数据：合同号、仓位、金额
            if 'Contract' in other_data_s:
                one_row_in_table.append(QStandardItem(other_data_s['Contract']))
            else:
                one_row_in_table.append(QStandardItem(''))
            actual_storage = 'E'
            if 'FromStorage' in other_data_s:
                one_row_in_table.append(QStandardItem(other_data_s['FromStorage']))
                actual_storage = other_data_s['FromStorage'][-1:]
            else:
                one_row_in_table.append(QStandardItem(''))
            if 'Price' in other_data_s:
                price_item = QStandardItem(other_data_s['Price'])
                float_price = float(other_data_s['Price'])
                price_item.setData(float_price, Qt.DisplayRole)
            else:
                price_item = QStandardItem('')
            one_row_in_table.append(price_item)
            record_id_item = QStandardItem(r[7])
            record_id_item.setData(r[7], Qt.DisplayRole)
            one_row_in_table.append(record_id_item)
            if r[2] <= 1:
                # 使用了虚拟零件，用ERP的描述进行代替
                info = self.__database.get_erp_info(erp_code, jl_erp=(actual_storage == 'F'))
                if info is not None:
                    item: QStandardItem = one_row_in_table[3]
                    item.setText(info[1])
            self.__material_data.appendRow(one_row_in_table)
        self.materialTableView.resizeColumnsToContents()
        self.materialTableView.horizontalHeader().setStretchLastSection(True)
        self.materialTableView.horizontalHeader().setSectionsClickable(True)
        self.materialTableView.horizontalHeader().setSortIndicatorShown(True)
