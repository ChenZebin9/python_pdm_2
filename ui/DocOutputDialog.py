import os
import shutil
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QCursor, QColor, QBrush
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QAbstractItemView, QMenu,
                             QMessageBox, QTableWidgetItem, QCheckBox, QLineEdit,
                             QFileDialog)


class DocOutputDialog(QDialog):

    def __init__(self, parent=None, vault=None, sw_app=None):
        self.__parent = parent
        super(QDialog, self).__init__(parent=parent)
        self.okButton = QPushButton('输出', self)
        self.closeButton = QPushButton('关闭', self)
        self.docTable = QTableWidget(self)
        self.__vault = vault
        self.__sw_app = sw_app
        self.__menu_4_doc_table = QMenu(parent=self.docTable)
        self.__del_from_doc_table = self.__menu_4_doc_table.addAction('删除')
        self.__clean_from_doc_table = self.__menu_4_doc_table.addAction('清空')
        self.__select_file_menu_item = self.__menu_4_doc_table.addAction('选择路径')
        self.__2d_check = QCheckBox('2D')
        self.__2d_check.setChecked(True)
        self.__3d_check = QCheckBox('3D')
        self.__use_3d_version = QCheckBox('使用3D的版本号')
        self.__output_dir_line_edit = QLineEdit(self)
        self.__select_output_dir = QPushButton('浏览')
        self.__del_from_doc_table.triggered.connect(self.__del_item)
        self.__clean_from_doc_table.triggered.connect(self.__clean_items)
        self.__select_file_menu_item.triggered.connect(self.__select_file)

        # 设置输出任务的线程
        self.__do_output_thread = DoOutput(self.__sw_app)
        self.__do_output_thread.all_task_done_signal.connect(self.__output_task_end)
        self.__do_output_thread.one_task_done_signal.connect(self.__on_one_task_done)
        self.all_task_done = True

        # 输出的清单
        self.__output_parts = []
        self.__current_row = -1

        self.init_ui()

    def __output_task_end(self):
        self.all_task_done = True
        if self.isVisible():
            QMessageBox.information(self, '', '所有任务都完成。', QMessageBox.Ok)
        self.__parent.set_status_bar_text('所有技术资料输出任务完成。')

    def __on_one_task_done(self, r1, r2, ok, error):
        if len(error) > 0:
            print(error)
        w: QTableWidget = self.docTable.cellWidget(r1, 2)
        i: QTableWidgetItem = self.docTable.item(r1, 0)
        ww: QTableWidgetItem = w.item(r2, 2)
        if ok:
            color = QColor(144, 238, 144)
        else:
            color = QColor(255, 0, 0)
        ww.setBackground(QBrush(color))
        self.docTable.scrollToItem(i)

    def init_ui(self):
        self.setWindowTitle('技术资料输出')
        v_box = QVBoxLayout(self)

        h_box = QHBoxLayout(self)
        h_box.setAlignment(Qt.AlignRight)
        h_box.addWidget(self.okButton)
        h_box.addWidget(self.closeButton)

        h_box_1 = QHBoxLayout(self)
        h_box_1.addWidget(self.__2d_check)
        h_box_1.addWidget(self.__3d_check)
        h_box_1.addWidget(self.__use_3d_version)
        h_box_1.addWidget(self.__output_dir_line_edit)
        h_box_1.addWidget(self.__select_output_dir)
        self.__select_output_dir.clicked.connect(self.__on_select_output_dir)
        self.__2d_check.stateChanged.connect(self.__setting_change)
        self.__3d_check.stateChanged.connect(self.__setting_change)
        self.__use_3d_version.stateChanged.connect(self.__setting_change)

        self.docTable.setColumnCount(3)
        self.docTable.setHorizontalHeaderLabels(['序号', '名称', '文件'])
        self.docTable.setEditTriggers( QAbstractItemView.NoEditTriggers )
        self.docTable.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.docTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.docTable.customContextMenuRequested.connect(self.__on_custom_context_menu_requested)

        v_box.addLayout(h_box_1)
        v_box.addWidget(self.docTable)
        v_box.addLayout(h_box)
        self.setLayout(v_box)

        self.closeButton.clicked.connect(lambda: self.hide())
        self.okButton.clicked.connect(self.__do_output)

        self.setGeometry(100, 100, 800, 400)
        self.setWindowModality(Qt.NonModal)

    def __do_output(self):
        if len(self.__output_dir_line_edit.text()) < 1:
            QMessageBox.warning(self, '', '没有选择输出目录。', QMessageBox.Ok)
            return
        model_dir = self.__output_dir_line_edit.text() + r'\models'
        drawings_dir = self.__output_dir_line_edit.text() + r'\drawings'
        docs_dir = self.__output_dir_line_edit.text() + r'\documents'
        if not os.path.exists(model_dir):
            os.mkdir(model_dir)
        if not os.path.exists(drawings_dir):
            os.mkdir(drawings_dir)
        if not os.path.exists(docs_dir):
            os.mkdir(docs_dir)
        row_count = self.docTable.rowCount()
        root_folder = self.__vault.GetRootFolder()

        task_list = []
        for i in range(row_count):
            id_ = self.docTable.item(i, 0)
            name = self.docTable.item(i, 1)
            w: QTableWidget = self.docTable.cellWidget(i, 2)
            c_row_count = w.rowCount()
            for j in range(c_row_count):
                item: QTableWidgetItem = w.item(j, 0)
                d = item.data(Qt.UserRole)
                if d:
                    continue
                t = item.text()
                v = w.item(j, 1).text()
                p = w.item(j, 2).text()
                save2_type = ''
                if t == 'SLDPRT' or t == 'SLDASM':
                    full_name = '{0}\\{1}.{2}-{3}.STEP'.format(model_dir, id_.text(), v, name.text())
                    save2_type = 'STEP'
                elif t == 'SLDDRW':
                    full_name = '{0}\\{1}.{2}-{3}.PDF'.format(drawings_dir, id_.text(), v, name.text())
                    save2_type = 'PDF'
                else:
                    full_name = '{0}\\{1}.{2}-{3}.{4}'.format(docs_dir, id_.text(), v, name.text(), t)
                source = root_folder + p
                one_task = [i, j, save2_type, source, full_name]
                task_list.append(one_task)
        self.__do_output_thread.set_task_list(task_list)
        self.all_task_done = False
        self.__do_output_thread.start()

    def __on_select_output_dir(self):
        path = QFileDialog.getExistingDirectory(parent=self, caption='选择输出目录')
        self.__output_dir_line_edit.setText(path)

    def __del_item(self):
        result = QMessageBox.question(self, '', '确定要删除？', QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            item = self.docTable.item(self.__current_row, 0)
            if item is None:
                return
            id_ = item.text()
            self.__output_parts.remove(id_)
            self.docTable.removeRow(self.__current_row)

    def __setting_change(self, v):
        """ v=2 时，checkBox被选择；v=0时，checkBox被不选择 """
        if self.sender() is self.__2d_check:
            pass
        elif self.sender() is self.__3d_check:
            pass
        elif self.sender() is self.__use_3d_version:
            pass

    def __select_file(self):
        pass

    def __clean_items(self):
        self.docTable.clear()
        self.docTable.setRowCount(0)
        self.docTable.setHorizontalHeaderLabels(['序号', '名称', '文件'])
        self.__output_parts.clear()

    def __on_custom_context_menu_requested(self, pos):
        if self.docTable.rowCount() < 1:
            return
        item = self.docTable.itemAt(pos)
        if item is not None:
            self.__current_row = item.row()
        self.__del_from_doc_table.setVisible(False if item is None else True)
        self.__select_file_menu_item.setVisible(False if item is None else True)
        self.__menu_4_doc_table.exec(QCursor.pos())

    @staticmethod
    def create_version(the_str):
        status_flag = 'P'
        if the_str[1] == '已审批' or the_str[1] == '已批准':
            status_flag = ''
        lock_status = 'E'
        if the_str[2] == '否':
            lock_status = ''
        return '{0}{1}{2}'.format(the_str[3], status_flag, lock_status)

    def __config_output_data(self, table: QTableWidget, datas=None):
        all_row_height = 2
        if datas is not None:
            """ 要往table里面添加数据 """
            part_version = '-1 _'
            _2d_file = '_ _ _'
            _3d_file = '_ _ _'
            temp_items = []
            for k in datas.keys():
                vv = datas[k]
                for v in vv:
                    # 版本号的获取
                    file_version = '-1'
                    try:
                        if self.__vault is not None:
                            file_info = list( self.__vault.GetFileStatus( v ) )
                            file_version = DocOutputDialog.create_version(file_info)
                    except Exception as e:
                        mes = '读取{0}文件的信息失败: {1}'.format( v, e )
                        print( mes )
                    if k == 'SLDASM':  # SLDASM 为最优先的版本号
                        part_version = '{0} SLSASM'.format(file_version)
                    elif k == 'SLDPRT':  # SLDPRT 为次优先的版本号，但不与之前的重复
                        post_f = part_version.split(' ')[1]
                        if post_f != 'SLDASM' and post_f != 'SLDPRT':
                            part_version = '{0} SLDPRT'.format(file_version)
                    elif part_version.split(' ')[1] == '_':
                        part_version = '{0} {1}'.format(file_version, k)

                    # 登记输出文档
                    file_2d_s = _2d_file.split(' ')
                    file_3d_s = _3d_file.split(' ')
                    set_2d_flag = False
                    set_3d_flag = False
                    if k == 'SLDASM':
                        if file_3d_s[0] != 'SLDASM':
                            set_3d_flag = True
                    elif k == 'SLDPRT':
                        if file_3d_s[0] != 'SLDASM' and file_3d_s[0] != 'SLDPRT':
                            set_3d_flag = True
                    elif k == 'PDF':
                        if file_2d_s[0] != 'PDF':
                            set_2d_flag = True
                    elif k == 'SLDDRW':
                        if file_2d_s[0] != 'SLDDRW' and file_2d_s[0] != 'PDF':
                            set_2d_flag = True
                    else:
                        set_2d_flag = True
                    if set_2d_flag:
                        _2d_file = '{0} {1} {2}'.format( k, file_version, v )
                    if set_3d_flag:
                        _3d_file = '{0} {1} {2}'.format( k, file_version, v )

                    item_s = [QTableWidgetItem( k ), QTableWidgetItem( file_version ), QTableWidgetItem( v )]
                    temp_items.append(item_s)

            for i in temp_items:
                r_c = table.rowCount()
                table.insertRow( r_c )
                t = i[0].text()
                p = i[2].text()
                not_output_flag = True
                if t == 'SLDASM' or t == 'SLDPRT':
                    if self.__3d_check.isChecked():
                        if _3d_file.startswith(t) and _3d_file.endswith(p):
                            not_output_flag = False
                else:
                    if self.__use_3d_version.isChecked():
                        part_version_s = part_version.split(' ')
                        i[1].setText(part_version_s[0])
                    if self.__2d_check.isChecked():
                        if _2d_file.startswith(t) and  _2d_file.endswith(p):
                            not_output_flag = False
                DocOutputDialog.__set_output_flag( i, not_output_flag )
                table.setItem(r_c, 0, i[0])
                table.setItem(r_c, 1, i[1])
                table.setItem(r_c, 2, i[2])
                all_row_height += table.rowHeight( r_c )
            return all_row_height
        else:
            """ 要修改table里面的数据 """
            pass

    @staticmethod
    def __set_output_flag(items, not_output):
        for i in items:
            i.setData( Qt.UserRole, not_output )
            if not not_output:
                continue
            i.setBackground(QBrush(QColor(255, 165, 0)))

    def add_doc_list(self, data):
        for d in data:
            p_num = d[0]
            if p_num in self.__output_parts:
                QMessageBox.warning(self, '未添加', '{0}零件已存在，未添加。'.format(p_num), QMessageBox.Ok)
                continue
            self.__output_parts.append(p_num)
            row_count = self.docTable.rowCount()
            self.docTable.insertRow(row_count)
            first_item = QTableWidgetItem(p_num)
            first_item.setData(Qt.UserRole, d)
            self.docTable.setItem(row_count, 0, first_item)
            self.docTable.setItem(row_count, 1, QTableWidgetItem(d[1]))

            cell_table = QTableWidget(self.docTable)
            cell_table.horizontalHeader().setVisible(False)
            cell_table.setColumnCount(3)
            cell_table.setHorizontalHeaderLabels(['类型', '版本', '路径'])
            all_row_height = self.__config_output_data(cell_table, d[2])
            QTableWidget.resizeColumnsToContents( cell_table )
            QTableWidget.resizeRowsToContents( cell_table )
            cell_table.setFixedHeight(all_row_height)
            self.docTable.setCellWidget(row_count, 2, cell_table)

        QTableWidget.resizeColumnsToContents( self.docTable )
        QTableWidget.resizeRowsToContents( self.docTable )
        self.docTable.setColumnWidth(2, 500)


class DoOutput(QThread):
    """
    执行输出任务。
    one_task_done_signal 信号的参数定义：
        int - 任务列表的总行（PART）地址
        int - 任务列表的子行（DOCUMENT）地址
        bool - 是否执行成功
        str - 错误代码
    """
    one_task_done_signal = pyqtSignal(int, int, bool, str)
    all_task_done_signal = pyqtSignal()

    def __init__(self, sw_app):
        super().__init__()
        self.__app = sw_app
        self.__task_list = None

    def __del__(self):
        self.wait()

    def set_task_list(self, task_list):
        self.__task_list = task_list

    def run(self):
        """ 进行任务操作 """
        try:
            if not self.__app.IsAppRunning():
                self.__app.RunApp()
            for task in self.__task_list:
                try:
                    save2_type = task[2]
                    if save2_type == 'STEP':
                        self.__app.SaveToStep( task[4], task[3] )
                    elif save2_type == 'PDF':
                        self.__app.SaveToPdf( task[4], task[3], False )
                    else:
                        shutil.copy( task[3], task[4] )
                    self.one_task_done_signal.emit(task[0], task[1], True, '')
                except Exception as e:
                    mes = '输出{0}时出错：{1}'.format(task[3], e)
                    self.one_task_done_signal.emit(task[0], task[1], False, mes)
        finally:
            self.__app.CloseApp()
            self.all_task_done_signal.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = DocOutputDialog()
    dialog.show()
    sys.exit(app.exec_())
