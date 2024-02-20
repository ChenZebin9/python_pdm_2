# coding=gbk
from datetime import datetime

from PyQt5.QtCore import (Qt, QDate, QItemSelectionModel, QModelIndex, QDateTime)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QCursor)
from PyQt5.QtWidgets import (QDialog, QAbstractItemView, QMenu, QMessageBox)

from ui3.HandlePickMaterialDialog import *
from Com import str_2_dict


class NHandlePickMaterialDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None, database=None, operator=None):
        self.__parent = parent
        self.__database = database
        self.__operator = operator
        # �б������
        self.__material_data = QStandardItemModel()
        super(NHandlePickMaterialDialog, self).__init__(parent)
        super(NHandlePickMaterialDialog, self).setupUi(self)

        # �Ҽ��˵�
        self.__menu_4_material_table_edit = QMenu(parent=self.materialTableView)
        self.__roll_back_material_action = self.__menu_4_material_table_edit.addAction('����')

        self.setModal(True)
        self.setup_ui()
        self.init_data()

        # ��Ҫ�����������
        self.__selected_indexes = None
        self.__material_2_be_handled = []

        # �Ƿ���и��µ�Flag
        self.__update_flag = True

    def setup_ui(self):
        self.setWindowTitle('����')
        self.setLayout(self.v_1_layout)

        self.beginDateEdit.setCalendarPopup(True)
        self.endDateEdit.setCalendarPopup(True)
        self.beginDateEdit.dateChanged.connect(self.__update_material_list)
        self.endDateEdit.dateChanged.connect(self.__update_material_list)

        self.materialTableView.setModel(self.__material_data)
        self.materialTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.materialTableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.materialTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.endDateEdit.setDisplayFormat('yyyy/MM/dd')
        self.beginDateEdit.setDisplayFormat('yyyy/MM/dd')

        # �����Ҽ��˵�
        self.__roll_back_material_action.triggered.connect(self.__do_roll_back)
        self.materialTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.materialTableView.customContextMenuRequested.connect(self.__on_custom_context_menu_requested)

    def init_data(self):
        self.__update_flag = False
        today = QDate.currentDate()
        begin_day = today.addDays(-15)
        self.endDateEdit.setDate(today)
        self.beginDateEdit.setDate(begin_day)
        self.__update_flag = True
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
        ����ʵ���ϵ��˿⹤��
        :return:
        """
        try:
            resp = QMessageBox.question(self, 'ѯ��', '�Ƿ�Ҫ��ѡ�������ݽ������ϴ���',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if resp == QMessageBox.No:
                return
            now = QDateTime.currentDateTime()
            bill_name = 'P{0}'.format(now.toString('yyMMdd'))
            bill_name = self.__database.get_available_supply_operation_bill(bill_name)
            self.__database.create_put_back_material_record(
                bill_name, self.__operator, now.toString('yyyy-MM-dd hh:mm:ss'), self.__material_2_be_handled)
            QMessageBox.information(self, '', '������ϵĲ�����', QMessageBox.Yes)
            c = int(len(self.__selected_indexes) / 10)
            for i in range(c):
                first_index: QModelIndex = self.__selected_indexes[i * 10]
                self.__material_data.removeRow(first_index.row())
        except Exception as ex:
            QMessageBox.warning(self, '����ʱ����', ex.__str__())

    def __update_material_list(self):
        if not self.__update_flag:
            return
        pick_records = self.__database.get_pick_material_record(self.beginDateEdit.text(), self.endDateEdit.text())
        self.__material_data.clear()
        self.__material_data.setHorizontalHeaderLabels(
            ['����', '��Ŀ��', '�����', '����', '����', '����', '��ͬ��', '��λ', '���', '��¼��'])
        if pick_records is None:
            QMessageBox.information(self.__parent, '', '��ʱ��Σ�û�г�����¼��')
            return
        for r in pick_records:
            other_data_s = str_2_dict(r[6])
            if 'RollBack' in other_data_s:
                if other_data_s['RollBack'] == 'Y':
                    # �ѱ����ϵľͲ�Ҫ����ʾ��
                    continue
            erp_code = r[3]
            if float(r[5]) < 0.0:
                # ����С��0��Ҳ��Ҫ��ʾ
                continue
            # ���ݺš���������Ŀ�š������
            one_row_in_table = [QStandardItem(r[0]), QStandardItem('{0}'.format(r[1])),
                                QStandardItem('{:08d}'.format(r[2]))]
            part_info = self.__database.get_part_info_quick(r[2])
            if part_info is None:
                raise Exception('û�и�����ŵ������Ϣ��')
            description = ' '.join(part_info[:3])
            # ���������
            one_row_in_table.append(QStandardItem(description.strip()))
            # ����������
            tt = datetime.strptime(r[4], "%Y-%m-%d %H:%M:%S") if type(r[4]) == str else r[4]
            one_row_in_table.append(QStandardItem(tt.strftime('%Y/%m/%d')))
            # ����
            qty_item = QStandardItem(r[5])
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            qty_item.setData(float(r[5]), Qt.DisplayRole)
            one_row_in_table.append(qty_item)
            # �������ݣ���ͬ�š���λ�����
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
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                float_price = float(other_data_s['Price'])
                price_item.setData('{0:.2f}'.format(float_price), Qt.DisplayRole)
            else:
                price_item = QStandardItem('')
            one_row_in_table.append(price_item)
            record_id_item = QStandardItem(r[7])
            record_id_item.setData(r[7], Qt.DisplayRole)
            one_row_in_table.append(record_id_item)
            if r[2] <= 1:
                # ʹ���������������ERP���������д���
                code = 2
                if actual_storage == 'F':
                    code = 1
                elif actual_storage == 'E' or actual_storage == 'D':
                    code = 0
                info = self.__database.get_erp_info(erp_code, which_erp=code)
                if info is not None:
                    item: QStandardItem = one_row_in_table[3]
                    item.setText(info[1])
            self.__material_data.appendRow(one_row_in_table)
        self.materialTableView.resizeColumnsToContents()
        self.materialTableView.horizontalHeader().setStretchLastSection(True)
        self.materialTableView.horizontalHeader().setSectionsClickable(True)
        self.materialTableView.horizontalHeader().setSortIndicatorShown(True)
