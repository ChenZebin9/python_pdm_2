import os
import time
from PyQt5.QtGui import QIntValidator, QPixmap, QCursor
from PyQt5.QtWidgets import (QFrame, QLabel, QTextEdit,
                             QListWidget, QHBoxLayout, QFormLayout, QVBoxLayout,
                             QPushButton, QComboBox, QTableWidget,
                             QTableWidgetItem, QListWidgetItem,
                             QMenu)
from PyQt5.QtCore import (QThread, pyqtSignal)
from Part import Part, DoStatistics
from ui.MyTreeWidget import *
from db.SqliteHandler import SqliteHandler


class PartInfoPanel( QFrame ):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.idLineEdit = QLineEdit( self )
        self.nameLineEdit = QLineEdit( self )
        self.englishNameLineEdit = QLineEdit( self )
        self.descriptionLineEdit = QLineEdit( self )
        self.commentTextEdit = QTextEdit( self )
        self.tagListWidget = QListWidget( self )
        self.__init_ui()

    def __init_ui(self):
        self.commentTextEdit.setTabChangesFocus( True )

        hbox = QHBoxLayout( self )

        formlayout = QFormLayout( self )
        formlayout.setLabelAlignment( Qt.AlignRight )
        formlayout.addRow( '序号', self.idLineEdit )
        formlayout.addRow( '名称', self.nameLineEdit )
        formlayout.addRow( '英文名称', self.englishNameLineEdit )
        formlayout.addRow( '描述', self.descriptionLineEdit )
        formlayout.addRow( '备注', self.commentTextEdit )

        tagLayout = QVBoxLayout( self )
        tagLabel = QLabel( '标签' )
        tagLabel.setAlignment( Qt.AlignCenter )
        tagLayout.addWidget( tagLabel )
        tagLayout.addWidget( self.tagListWidget )

        hbox.addLayout( formlayout )
        hbox.addLayout( tagLayout )

        self.setLayout( hbox )
        self.setFixedSize( 600, 200 )

    def set_part_info(self, part):
        self.idLineEdit.setText(part.part_id)
        self.idLineEdit.setEnabled(False)
        self.nameLineEdit.setText(part.name)
        self.englishNameLineEdit.setText(part.english_name)
        self.descriptionLineEdit.setText(part.description)
        self.commentTextEdit.setText(part.comment)
        self.tagListWidget.clear()
        for t in part.tags:
            one_item = QListWidgetItem(t.get_whole_name(), parent=self.tagListWidget)
            one_item.setData(Qt.UserRole, t)
            self.tagListWidget.addItem(one_item)


class PartInfoPanelInMainWindow(QFrame):

    def __init__(self, parent=None, work_folder=None):
        self.__work_folder = work_folder
        self.__parent = parent
        self.__vault = None
        super().__init__(parent)
        self.partInfo = PartInfoPanel(parent)
        self.imageLabel = QLabel(self)
        self.relationFilesList = QListWidget(self)
        self.__setup_ui()

    def __setup_ui(self):
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.partInfo)
        self.imageLabel.setFixedSize(200, 200)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        hbox.addWidget(self.imageLabel)
        hbox.addWidget(self.relationFilesList)
        self.relationFilesList.itemDoubleClicked.connect(self.__open_file)
        self.relationFilesList.itemSelectionChanged.connect(self.__linked_file_changed)
        self.setLayout(hbox)

    def set_part_info(self, part, database):
        self.partInfo.set_part_info(part)
        files_list = database.get_files_2_part(part.get_part_id())
        self.relationFilesList.clear()
        self.relationFilesList.addItems(files_list)
        img_data = database.get_thumbnail_2_part(part.get_part_id())
        if img_data is not None:
            img = QPixmap()
            img.loadFromData(img_data)
            n_img = img.scaled(200, 200, aspectRatioMode=Qt.KeepAspectRatio)
            self.imageLabel.setPixmap(n_img)
        else:
            self.imageLabel.clear()

    def __open_file(self, item: QListWidgetItem):
        file_name = item.text()
        full_path = '{0}\\{1}'.format(self.__work_folder, file_name)
        if os.path.exists(full_path):
            os.startfile(full_path)
        else:
            QMessageBox.information( self.__parent, '无法打开', '{0}文件不存在'.format( full_path ), QMessageBox.Ok )

    def set_vault(self, vault):
        self.__vault = vault

    def __linked_file_changed(self):
        try:
            item = self.relationFilesList.currentItem()
            if self.__vault is None:
                return
            file_name = item.text()
            datas_ = self.__vault.GetFileStatus(file_name)
            datas = list(datas_)
            self.__parent.set_status_bar_text(file_name + ' ' + datas[0])
        except Exception as e:
            self.__parent.set_status_bar_text('Error: {0}'.format(e))


class ChildrenTablePanel(QFrame):

    """
    mode = 0: 子清单
    mode = 1: 父清单
    """

    def __init__(self, parent=None, database=None, mode=0):
        super().__init__(parent)
        self.__parent = parent
        self.__database = database
        self.__mode = mode
        self.__select_part_id = None
        self.childrenTableWidget = QTableWidget(self)
        self.addItemButton = QPushButton(self)
        self.deleteItemButton = QPushButton(self)
        self.saveAllItemsButton = QPushButton(self)
        self.go2ItemButton = QPushButton(self)
        self.__init_ui()

    def __init_ui(self):
        self.addItemButton.setText('添加')
        self.deleteItemButton.setText('删除')
        self.saveAllItemsButton.setText('保存')
        self.go2ItemButton.setText('跳转...')
        h_box = QHBoxLayout(self)
        v_box = QVBoxLayout(self)
        v_box.setAlignment(Qt.AlignTop)
        if self.__mode == 0:
            v_box.addWidget(self.addItemButton)
            v_box.addWidget(self.deleteItemButton)
            v_box.addWidget(self.saveAllItemsButton)
        else:
            self.addItemButton.setVisible(False)
            self.deleteItemButton.setVisible(False)
            self.saveAllItemsButton.setVisible(False)
        v_box.addWidget(self.go2ItemButton)
        h_box.addLayout(v_box)
        h_box.addWidget(self.childrenTableWidget)
        self.setLayout(h_box)
        # 表格的选择
        self.childrenTableWidget.itemSelectionChanged.connect(self.__table_select_changed)
        # 按键的动作响应
        self.go2ItemButton.clicked.connect(self.__go_2_part)

    def __table_select_changed(self):
        item = self.childrenTableWidget.currentItem()
        if item is None:
            self.__select_part_id = None
            return
        row_index = item.row()
        ii: QTableWidgetItem = self.childrenTableWidget.item(row_index, 1)
        if ii is not None:
            ii_text = ii.text().lstrip('0')
            self.__select_part_id = int(ii_text)
        else:
            self.__select_part_id = None

    def __go_2_part(self):
        self.__parent.do_when_part_list_select(self.__select_part_id)

    def set_part_children(self, part: Part, database):
        self.__select_part_id = None
        if self.__mode == 0:
            result = part.get_children(database)
        else:
            result = part.get_children(database, mode=1)
        self.childrenTableWidget.setColumnCount( 8 )
        self.childrenTableWidget.setHorizontalHeaderLabels(
            ['序号', '零件号', '名称', '描述', '统计数量', '实际数量', '状态', '备注'] )
        r_number = len( result ) if result is not None else 0
        self.childrenTableWidget.setRowCount( r_number )
        if r_number < 1:
            return
        index = 0
        for r in result:
            index_item = QTableWidgetItem(str(r[0]))
            p = r[1]
            id_item = QTableWidgetItem( p.part_id )
            id_item.setData(Qt.UserRole, r[4])
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            name_item = QTableWidgetItem( p.name )
            name_item.setFlags( name_item.flags() & ~Qt.ItemIsEditable )
            status_item = QTableWidgetItem( p.status )
            status_item.setFlags( status_item.flags() & ~Qt.ItemIsEditable )
            description_item = QTableWidgetItem( p.description )
            description_item.setFlags( description_item.flags() & ~Qt.ItemIsEditable )
            comment_item = QTableWidgetItem( p.comment )
            qty_1_item = QTableWidgetItem(str(r[2]))
            qty_1_item.setData(Qt.UserRole, r[2])
            qty_1_item.setTextAlignment(Qt.AlignHCenter)
            qty_2_item = QTableWidgetItem(str(r[3]))
            qty_2_item.setData(Qt.UserRole, r[4])
            qty_2_item.setTextAlignment(Qt.AlignHCenter)
            self.childrenTableWidget.setItem( index, 0, index_item)
            self.childrenTableWidget.setItem( index, 1, id_item )
            self.childrenTableWidget.setItem( index, 2, name_item )
            self.childrenTableWidget.setItem( index, 3, description_item )
            self.childrenTableWidget.setItem( index, 4, qty_1_item )
            self.childrenTableWidget.setItem( index, 5, qty_2_item )
            self.childrenTableWidget.setItem( index, 6, status_item )
            self.childrenTableWidget.setItem( index, 7, comment_item )
            index += 1
        QTableWidget.resizeColumnsToContents( self.childrenTableWidget )
        QTableWidget.resizeRowsToContents( self.childrenTableWidget )


class TagViewPanel(QFrame):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.parent = parent
        self.__database = database
        self.filterLineEdit = QLineEdit(self)
        self.cleanTextPushButton = QPushButton(self)
        self.tagTreeWidget = MyTreeWidget2(self, database)
        self.tagFilterListWidget = QListWidget( self )
        """ 进行标签查看的右键菜单 """
        self.__menu_4_tag_tree = QMenu(parent=self.tagTreeWidget)
        self.__add_tag_2_filter = self.__menu_4_tag_tree.addAction('添加至过滤')
        self.__add_tag_2_filter.triggered.connect(self.__on_add_2_filter)
        self.__current_selected_tag = None
        """ 进行标签编辑时的右键菜单 """
        self.__selected_tag_in_edit_mode = None
        self.__menu_4_tag_tree_edit = QMenu(parent=self.tagTreeWidget)
        self.__create_new_tag = self.__menu_4_tag_tree_edit.addAction('插入')
        self.__del_tag = self.__menu_4_tag_tree_edit.addAction('删除')
        self.__rename_tag = self.__menu_4_tag_tree_edit.addAction('重命名')
        self.__cut_tag = self.__menu_4_tag_tree_edit.addAction('剪切')
        self.__paste_tag_into = self.__menu_4_tag_tree_edit.addAction('粘帖')
        # 用于右键菜单的 item
        self.__item_this_time = None
        self.__create_new_tag.triggered.connect(self.tagTreeWidget.create_new_tag)
        self.__del_tag.triggered.connect(self.tagTreeWidget.del_tag)
        self.__rename_tag.triggered.connect(self.tagTreeWidget.rename_tag)
        self.__cut_tag.triggered.connect(self.tagTreeWidget.cut_tag)
        self.__paste_tag_into.triggered.connect(lambda: self.tagTreeWidget.paste_tag_into(self.__item_this_time))
        """ 标签过来清单的右键菜单 """
        self.__menu_4_tag_list = QMenu(parent=self.tagFilterListWidget)
        self.__del_tag_from_filter = self.__menu_4_tag_list.addAction('删除')
        self.__clean_tag_from_filter = self.__menu_4_tag_list.addAction('清空')
        self.__del_tag_from_filter.triggered.connect(self.__on_del_from_filter)
        self.__clean_tag_from_filter.triggered.connect(self.__on_clean_filter)

        self.__edit_mode = False

        self.__init_ui()

    def set_status_message(self, text):
        self.parent.set_status_bar_text(text)

    def set_mode(self, edit_mode):
        self.__edit_mode = edit_mode
        self.tagTreeWidget.set_edit_mode(edit_mode)

    def __init_ui(self):
        self.cleanTextPushButton.setText( '清空' )
        self.cleanTextPushButton.clicked.connect(lambda: self.filterLineEdit.setText(None))
        self.tagFilterListWidget.setFixedHeight(100)
        v_box = QVBoxLayout(self)

        filter_h_box = QHBoxLayout(self)
        filter_h_box.addWidget(QLabel('过滤'))
        filter_h_box.addWidget(self.filterLineEdit)
        filter_h_box.addWidget(self.cleanTextPushButton)

        v_box.addLayout(filter_h_box)
        v_box.addWidget(self.tagTreeWidget)
        v_box.addWidget(self.tagFilterListWidget)

        self.setLayout(v_box)

        self.tagTreeWidget.setHeaderLabels(['标签'])
        self.tagTreeWidget.itemSelectionChanged.connect(self.__select_tag)
        self.tagTreeWidget.itemExpanded.connect(self.__when_item_expand)
        self.filterLineEdit.textChanged.connect(self.__do_search)
        self.tagTreeWidget.setContextMenuPolicy( Qt.CustomContextMenu )
        self.tagTreeWidget.customContextMenuRequested.connect(self.__on_custom_context_menu_requested)

        self.tagFilterListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tagFilterListWidget.customContextMenuRequested.connect(self.__on_custom_context_menu_requested)

    def __on_custom_context_menu_requested(self, pos):
        if self.sender() is self.tagTreeWidget:
            self.__item_this_time = self.tagTreeWidget.itemAt(pos)
            if not self.__edit_mode:
                if self.__item_this_time is None:
                    self.__current_selected_tag = None
                    return
                t = self.__item_this_time.data(0, Qt.UserRole)
                self.__current_selected_tag = t
                self.__menu_4_tag_tree.exec(QCursor.pos())
            else:
                self.tagTreeWidget.item_when_right_click(self.__item_this_time)
                shown = self.__item_this_time is not None
                self.__rename_tag.setVisible(shown)
                self.__cut_tag.setVisible(shown and not self.tagTreeWidget.clipper_not_empty())
                self.__del_tag.setVisible(shown)
                self.__paste_tag_into.setVisible(self.tagTreeWidget.clipper_not_empty())
                self.__menu_4_tag_tree_edit.exec(QCursor.pos())
        elif self.sender() is self.tagFilterListWidget:
            if self.tagFilterListWidget.count() < 1:
                return
            item = self.tagFilterListWidget.itemAt(pos)
            if item is None:
                self.__del_tag_from_filter.setVisible(False)
            else:
                self.__del_tag_from_filter.setVisible(True)
            self.__menu_4_tag_list.exec(QCursor.pos())

    def __on_add_2_filter(self):
        if self.__current_selected_tag is None:
            return
        item = QListWidgetItem(self.__current_selected_tag.get_whole_name(), parent=self.tagFilterListWidget)
        item.setData(Qt.UserRole, self.__current_selected_tag)
        self.tagFilterListWidget.addItem(item)
        self.__search_by_tag()

    def __on_del_from_filter(self):
        c_r = self.tagFilterListWidget.currentRow()
        item = self.tagFilterListWidget.takeItem(c_r)
        del item
        self.__search_by_tag()

    def __on_clean_filter(self):
        self.tagFilterListWidget.clear()

    def __search_by_tag(self):
        if self.tagFilterListWidget.count() < 1:
            return
        result = set()
        for i in range(0, self.tagFilterListWidget.count()):
            item = self.tagFilterListWidget.item(i)
            t: Tag = item.data(Qt.UserRole)
            ps = Part.get_parts_from_tag(self.__database, t.tag_id)
            ps_s = set(ps)
            if len(result) < 1:
                result = ps_s
            else:
                result = result.intersection(ps_s)
            if len(ps_s) < 1:
                return
        r_list = list(result)
        self.parent.show_parts_from_outside(r_list)

    def fill_data(self, tags):
        self.tagTreeWidget.clear()
        for t in tags:
            t.search_children(self.__database)
            node = QTreeWidgetItem(self.tagTreeWidget)
            node.setText(0, t.name)
            node.setData(0, Qt.UserRole, t)
            self.tagTreeWidget.addTopLevelItem(node)
            for c in t.children:
                n_node = QTreeWidgetItem(node)
                n_node.setText(0, c.name)
                n_node.setData(0, Qt.UserRole, c)
                node.addChild(n_node)

    def __select_tag(self):
        if self.__edit_mode:
            node = self.tagTreeWidget.currentItem()
            if node is None:
                self.__selected_tag_in_edit_mode = None
            else:
                self.__selected_tag_in_edit_mode = node
            return
        node = self.tagTreeWidget.currentItem()
        t = node.data(0, Qt.UserRole)
        self.parent.do_when_tag_tree_select(t.tag_id)

    def __when_item_expand(self, item: QTreeWidgetItem):
        data = item.data(0, Qt.UserRole)
        for cc in data.children:
            cc.search_children(self.__database)
            if len(cc.children) < 1:
                continue
            for c in cc.children:
                node = QTreeWidgetItem(self.tagTreeWidget)
                node.setText(0, c.name)
                node.setData(0, Qt.UserRole, c)

    def __do_search(self, filter_text):
        if filter_text == '':
            filter_text = None
        tags = Tag.get_tags(self.__database, name=filter_text)
        self.fill_data(tags)

    def clipboard_is_not_empty(self):
        return self.tagTreeWidget.clipper_not_empty()

    def get_current_selected_tag(self):
        # 当前所选的 Tag
        node = self.__selected_tag_in_edit_mode
        if node is None:
            return None
        the_tag = node.data(0, Qt.UserRole)
        return the_tag


class PartTablePanel( QFrame ):

    # 要改为 static 变量才能实现 connect？
    __stop_above_thread_signal = pyqtSignal()

    def __init__(self, parent=None, database=None, columns=None):
        super().__init__(parent)
        self.__database = database
        self.__parent = parent
        self.__columns = columns
        self.__display_range = []
        self.idLineEdit = QLineEdit(self)
        self.nameComboBox = QComboBox(self)
        self.nameLineEdit = QLineEdit(self)
        self.desLineEdit = QLineEdit( self )
        self.cleanPushButton = QPushButton(self)

        self.partList = QTableWidget(self)
        self.partList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.partList.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 一个填写单元格信息的线程
        self.__fill_part_info_thread = FillPartInfo(database.copy())
        self.__stop_above_thread_signal.connect(self.__fill_part_info_thread.stop)
        self.__fill_part_info_thread.one_cell_2_fill_signal.connect(self.__fill_one_cell)
        self.__fill_part_info_thread.all_cells_done_signal.connect(self.__all_cells_filled)

        self.__init_ui()
        self.__current_selected_part = None

    def __init_ui(self):
        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout(self)

        hbox.addWidget(QLabel('序号'))
        self.idLineEdit.setValidator(QIntValidator())
        self.idLineEdit.setMaxLength(4)
        self.idLineEdit.setAlignment(Qt.AlignRight)
        self.idLineEdit.textChanged.connect(self.__do_search)
        hbox.addWidget(self.idLineEdit)
        self.nameComboBox.addItems(['中文名称', '英文名称'])
        self.nameComboBox.setCurrentIndex(0)
        hbox.addWidget(self.nameComboBox)
        self.nameLineEdit.textChanged.connect(self.__do_search)
        hbox.addWidget(self.nameLineEdit)
        hbox.addWidget(QLabel('描述'))
        self.desLineEdit.textChanged.connect( self.__do_search )
        hbox.addWidget( self.desLineEdit )
        self.cleanPushButton.setText('清空')
        self.cleanPushButton.clicked.connect( self.__clean_input )
        hbox.addWidget(self.cleanPushButton)

        vbox.addLayout(hbox)
        vbox.addWidget(self.partList)
        self.setLayout(vbox)
        if self.__parent is not None:
            self.partList.itemSelectionChanged.connect(self.__selected_part)

    def __selected_part(self):
        selected_row = self.partList.currentRow()
        item = self.partList.item(selected_row, 0)
        self.__current_selected_part = 0
        if item is not None:
            t = item.text()
            part_num = int(t.lstrip('0'))
            self.__current_selected_part = part_num
            self.__parent.do_when_part_list_select(part_num)

    def set_display_columns(self, columns):
        self.__columns = columns

    def get_current_selected_parts(self):
        """ 获取所有选择了的part的ID """
        items = self.partList.selectedItems()
        result = []
        rr = []
        for item in items:
            r = item.row()
            if r in rr:
                continue
            rr.append(r)
            i = self.partList.item(r, 0)
            id_ = i.data(Qt.UserRole)
            result.append(id_)
        return result

    def get_current_selected_part(self):
        return self.__current_selected_part

    def __do_search(self):
        part_id = None if self.idLineEdit.text() == '' else int(self.idLineEdit.text())
        name = None
        english_name = None
        tt = self.nameLineEdit.text().strip()
        if self.nameComboBox.currentIndex() == 0:
            name = None if tt == '' else tt
        else:
            english_name = None if tt == '' else tt
        tt = self.desLineEdit.text().strip()
        description = None if tt == '' else tt
        parts = []
        if self.__display_range is not None and len( self.__display_range ) > 0:
            tt = []
            if part_id is None and name is None and english_name is None and description is None:
                parts.extend(self.__display_range)
            else:
                if part_id is not None:
                    for p in self.__display_range:
                        if p.part_id == part_id:
                            tt.append(p)
                else:
                    tt.extend(self.__display_range)
                if name is not None:
                    for p in tt:
                        if p.name.find(name) > -1:
                            parts.append(p)
                else:
                    parts.extend(tt)
                tt.clear()
                if english_name is not None:
                    for p in parts:
                        if p.english_name.find(english_name) > -1:
                            tt.append(p)
                else:
                    tt.extend(parts)
                parts.clear()
                if description is not None:
                    for p in tt:
                        if p.description is not None and p.description.find(description) > -1:
                            parts.append(p)
                else:
                    parts.extend(tt)
        else:
            parts = Part.get_parts(self.__database, part_id=part_id,
                                   name=name, english_name=english_name, description=description)
        self.set_list_data(parts)

    def set_list_header_4_statistics(self):
        # 为统计进行一些准备
        fact_columns = list(self.__columns[1])
        fact_columns.append('数量')
        self.partList.setColumnCount(len(fact_columns))
        self.partList.setHorizontalHeaderLabels(list(fact_columns))
        self.partList.setRowCount(0)

    def add_one_part_4_statistics(self, part_id, qty):
        p: Part = Part.get_parts(self.__database, part_id=part_id)[0]
        r_c = self.partList.rowCount()
        self.partList.insertRow(r_c)
        columns_flags = self.__columns[0]
        columns_name = self.__columns[1]
        column_index = 0
        if columns_flags[0] == 1:
            id_item = QTableWidgetItem(p.part_id)
            id_item.setData(Qt.UserRole, p.get_part_id())
            self.partList.setItem(r_c, column_index, id_item)
            column_index += 1
        if columns_flags[1] == 1:
            name_item = QTableWidgetItem(p.name)
            self.partList.setItem(r_c, column_index, name_item)
            column_index += 1
        if columns_flags[2] == 1:
            english_item = QTableWidgetItem(p.english_name)
            self.partList.setItem(r_c, column_index, english_item)
            column_index += 1
        if columns_flags[3] == 1:
            description_item = QTableWidgetItem(p.description)
            self.partList.setItem(r_c, column_index, description_item)
            column_index += 1
        if columns_flags[4] == 1:
            status_item = QTableWidgetItem(p.status)
            self.partList.setItem(r_c, column_index, status_item)
            column_index += 1

        # 其它信息，可配置的
        for j in range(5, 11):
            if columns_flags[j] == 1:
                sss = p.get_specified_tag(self.__database, columns_name[column_index])
                ss = QTableWidgetItem(sss)
                self.partList.setItem(r_c, column_index, ss)
                column_index += 1

        if columns_flags[11] == 1:
            comment_item = QTableWidgetItem(p.comment)
            self.partList.setItem(r_c, column_index, comment_item)
            column_index += 1

        qty_item = QTableWidgetItem(str(qty))
        self.partList.setItem(r_c, column_index, qty_item)

    def set_list_data(self, parts):
        columns_flags = self.__columns[0]
        columns_name = self.__columns[1]
        self.partList.setColumnCount(len(columns_name))
        self.partList.setHorizontalHeaderLabels(list(columns_name))
        r_number = len(parts) if parts is not None else 0
        self.partList.setRowCount(r_number)
        if r_number < 1:
            return
        index = 0
        the_begin_column_index = 0
        other_column_count = 0
        for j in range(5, 11):
            if columns_flags[j] == 1:
                other_column_count += 1
        for p in parts:
            column_index = 0
            if columns_flags[0] == 1:
                id_item = QTableWidgetItem(p.part_id)
                id_item.setData(Qt.UserRole, p.get_part_id())
                self.partList.setItem( index, column_index, id_item )
                column_index += 1
            if columns_flags[1] == 1:
                name_item = QTableWidgetItem(p.name)
                self.partList.setItem( index, column_index, name_item )
                column_index += 1
            if columns_flags[2] == 1:
                english_item = QTableWidgetItem(p.english_name)
                self.partList.setItem( index, column_index, english_item )
                column_index += 1
            if columns_flags[3] == 1:
                description_item = QTableWidgetItem( p.description )
                self.partList.setItem( index, column_index, description_item )
                column_index += 1
            if columns_flags[4] == 1:
                status_item = QTableWidgetItem( p.status )
                self.partList.setItem( index, column_index, status_item )
                column_index += 1

            # 其它信息，可配置的
            the_begin_column_index = column_index
            column_index += other_column_count

            if columns_flags[11] == 1:
                comment_item = QTableWidgetItem(p.comment)
                self.partList.setItem( index, column_index, comment_item )
            index += 1
        QTableWidget.resizeColumnsToContents(self.partList)
        QTableWidget.resizeRowsToContents( self.partList )
        self.partList.clearSelection()
        if other_column_count >= 1:
            if self.__fill_part_info_thread.isRunning():
                self.__stop_above_thread_signal.emit()
            while self.__fill_part_info_thread.isRunning():
                time.sleep(0.1)
            self.__parent.set_status_bar_text('开始填充。')
            self.__fill_part_info_thread.set_data(columns_flags, columns_name,
                                                  the_begin_column_index, parts)
            self.__fill_part_info_thread.start()

    def __fill_one_cell(self, row_index, column_index, text):
        item = QTableWidgetItem(text)
        self.partList.setItem(row_index, column_index, item)

    def __all_cells_filled(self, is_paused):
        if is_paused:
            self.__parent.set_status_bar_text('填充中断。')
            return
        self.__parent.set_status_bar_text('填充完毕。')
        QTableWidget.resizeColumnsToContents( self.partList )
        QTableWidget.resizeRowsToContents( self.partList )
        self.partList.clearSelection()

    def get_current_parts_id(self):
        result = []
        cc = self.partList.rowCount()
        for i in range(cc):
            item = self.partList.item(i, 0)
            id_ = item.data( Qt.UserRole )
            result.append( id_ )
        return tuple(result)

    def set_display_range(self, parts):
        self.__display_range = parts

    def __clean_input(self):
        self.idLineEdit.setText(None)
        self.nameLineEdit.setText(None)
        self.desLineEdit.setText( None )


class FillPartInfo(QThread):
    """
    执行Part信息的填入
    all_cells_done_signal 所有信息都填写完毕
    one_cell_2_fill_signal 填写一个单元
        int - 行号
        int - 列号
        str - 数值
    """
    all_cells_done_signal = pyqtSignal(bool)
    one_cell_2_fill_signal = pyqtSignal(int, int, str)

    def __init__(self, database):
        super().__init__()
        self.__c_f = None
        self.__c_n = None
        self.__c_i = None
        self.__parts = None
        self.__stop_flag = False
        self.__db_type = database[0]
        self.__sqlite3_file = None
        if database[0] == 'MSSQL':
            self.__database = database[1]
        elif database[0] == 'SQLite3':
            self.__sqlite3_file = database[1]

    def set_data(self, columns_flag, columns_name, column_index, parts,):
        self.__c_f = columns_flag
        self.__c_n = columns_name
        self.__c_i = column_index
        self.__parts = parts
        self.__stop_flag = False

    def stop(self):
        self.__stop_flag = True

    # sqlite3 对象不能在不同的线程中使用，在run中才算另一个线程，仅在__init__赋值时，视为同一线程。
    def run(self):
        try:
            if self.__sqlite3_file is not None:
                self.__database = SqliteHandler(self.__sqlite3_file)
            index = 0
            for p in self.__parts:
                if self.__stop_flag:
                    break
                cc = self.__c_i
                for j in range(5, 11):
                    if self.__c_f[j] == 1:
                        ss = p.get_specified_tag( self.__database, self.__c_n[cc] )
                        self.one_cell_2_fill_signal.emit(index, cc, ss)
                        cc += 1
                index += 1
        finally:
            self.all_cells_done_signal.emit(self.__stop_flag)


class PartStructurePanel(QFrame):

    # 用户暂停统计线程
    __stop_above_thread_signal = pyqtSignal()

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.__database = database
        self.__parent = parent
        self.__structureTree = QTreeWidget(self)

        # 一个进行物料统计的线程
        self.__statistics_thread = DoStatistics(database.copy())
        # 统计线程的设置
        self.__statistics_thread.clean_part_list_signal.connect(self.__parent.set_ready_for_statistics_display)
        self.__statistics_thread.add_2_part_list_signal.connect(self.__parent.add_one_item_to_statistics_list)
        self.__statistics_thread.finish_statistics_signal.connect(self.__parent.show_statistics_finish_flag)
        self.__stop_above_thread_signal.connect(self.__statistics_thread.stop)

        self.__init_ui()

    def __init_ui(self):
        v_box = QVBoxLayout(self)
        v_box.addWidget(self.__structureTree)
        self.setLayout(v_box)
        self.__structureTree.itemExpanded.connect( self.__when_item_expand )
        self.__structureTree.itemSelectionChanged.connect(self.__select_part)

    def fill_data(self, part, children):
        self.__structureTree.setColumnCount(2)
        self.__structureTree.setHeaderLabels(['项目', '数量'])
        self.__structureTree.clear()
        root = QTreeWidgetItem(self.__structureTree)
        root.setText(0, '{0} {1}'.format(part.part_id, part.name))
        root.setText(1, '1.0')
        root.setData(0, Qt.UserRole, part)
        self.__structureTree.addTopLevelItem(root)
        for c in children:
            node = QTreeWidgetItem()
            p = c[1]
            qty = c[2]
            node.setText(0, '{0} {1}'.format(p.part_id, p.name))
            node.setText(1, '{0}'.format(qty))
            node .setData(0, Qt.UserRole, p)
            root.addChild(node)
        self.__structureTree.resizeColumnToContents(0)

    def __when_item_expand(self, item: QTreeWidgetItem):
        c_count = item.childCount()
        for i in range(0, c_count):
            cc = item.child(i)
            pp = cc.data(0, Qt.UserRole)
            children = pp.get_children(self.__database)
            if children is None:
                continue
            nodes = []
            for c in children:
                node = QTreeWidgetItem()
                p = c[1]
                qty = c[2]
                node.setText( 0, '{0} {1}'.format( p.part_id, p.name ) )
                node.setText( 1, '{0}'.format( qty ) )
                node.setData( 0, Qt.UserRole, p )
                nodes.append(node)
            cc.addChildren(nodes)
        self.__structureTree.resizeColumnToContents(0)

    def __select_part(self):
        item = self.__structureTree.currentItem()
        if item is None:
            return
        p = item.data(0, Qt.UserRole)
        if self.__parent is not None:
            self.__parent.do_when_part_list_select(p.get_part_id())
            stat_setting = self.__parent.get_statistics_setting()
            if stat_setting[0]:
                # 启动一次统计
                if self.__statistics_thread.isRunning():
                    self.__stop_above_thread_signal.emit()
                while self.__statistics_thread.isRunning():
                    time.sleep(0.1)
                self.__parent.set_status_bar_text('开始统计。')
                self.__statistics_thread.set_data(p.get_part_id(), stat_setting[1:])
                self.__statistics_thread.start()
