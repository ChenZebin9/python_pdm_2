from PyQt5.QtWidgets import (QFrame, QLineEdit, QLabel, QTextEdit,
                             QListWidget, QHBoxLayout, QFormLayout, QVBoxLayout,
                             QPushButton, QTreeWidget, QComboBox, QTableWidget,
                             QAbstractItemView, QTableWidgetItem, QListWidgetItem,
                             QTreeWidgetItem, QMessageBox, QMenu)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QPixmap, QCursor
from Part import Part, Tag
import os


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

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.__parent = parent
        self.__database = database
        self.childrenTableWidget = QTableWidget(self)
        self.addItemButton = QPushButton(self)
        self.deleteItemButton = QPushButton(self)
        self.saveAllItemsButton = QPushButton(self)
        self.__init_ui()

    def __init_ui(self):
        self.addItemButton.setText('添加')
        self.deleteItemButton.setText('删除')
        self.saveAllItemsButton.setText('保存')
        h_box = QHBoxLayout(self)
        v_box = QVBoxLayout(self)
        v_box.setAlignment(Qt.AlignTop)
        v_box.addWidget(self.addItemButton)
        v_box.addWidget(self.deleteItemButton)
        v_box.addWidget(self.saveAllItemsButton)
        h_box.addLayout(v_box)
        h_box.addWidget(self.childrenTableWidget)
        self.setLayout(h_box)

    def set_part_children(self, part : Part, database):
        result = part.get_children(database)
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
        self.tagTreeWidget = QTreeWidget(self)
        self.tagFilterListWidget = QListWidget( self )

        self.__menu_4_tag_tree = QMenu(parent=self.tagTreeWidget)
        self.__add_tag_2_filter = self.__menu_4_tag_tree.addAction('添加至过滤')
        self.__add_tag_2_filter.triggered.connect(self.__on_add_2_filter)
        self.__current_selected_tag = None

        self.__menu_4_tag_list = QMenu(parent=self.tagFilterListWidget)
        self.__del_tag_from_filter = self.__menu_4_tag_list.addAction('删除')
        self.__clean_tag_from_filter = self.__menu_4_tag_list.addAction('清空')
        self.__del_tag_from_filter.triggered.connect(self.__on_del_from_filter)
        self.__clean_tag_from_filter.triggered.connect(self.__on_clean_filter)

        self.__init_ui()

    def __init_ui(self):
        self.cleanTextPushButton.setText( '清空' )
        self.cleanTextPushButton.clicked.connect(lambda: self.filterLineEdit.setText(None))
        self.tagFilterListWidget.setFixedHeight(100)
        vbox = QVBoxLayout(self)

        filterHBox = QHBoxLayout(self)
        filterHBox.addWidget(QLabel('过滤'))
        filterHBox.addWidget(self.filterLineEdit)
        filterHBox.addWidget(self.cleanTextPushButton)

        vbox.addLayout(filterHBox)
        vbox.addWidget(self.tagTreeWidget)
        vbox.addWidget(self.tagFilterListWidget)

        self.setLayout(vbox)

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
            item = self.tagTreeWidget.itemAt(pos)
            if item is None:
                self.__current_selected_tag = None
                return
            t = item.data(0, Qt.UserRole)
            self.__current_selected_tag = t
            self.__menu_4_tag_tree.exec(QCursor.pos())
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


class PartTablePanel( QFrame ):

    def __init__(self, parent=None, database=None, columns=None):
        super().__init__(parent)
        self.__database = database
        self.__parent = parent
        self.__columns = columns
        self.__display_range = []
        self.idLineEdit = QLineEdit(self)
        self.nameComboBox = QComboBox(self)
        self.nameLineEdit = QLineEdit(self)
        self.despLineEdit = QLineEdit(self)
        self.cleanPushButton = QPushButton(self)
        self.partList = QTableWidget(self)
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
        self.despLineEdit.textChanged.connect(self.__do_search)
        hbox.addWidget(self.despLineEdit)
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
        tt = self.despLineEdit.text().strip()
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

    def set_list_data(self, parts):
        columns_flags = self.__columns[0]
        columns_name = self.__columns[1]
        self.partList.setColumnCount(len(columns_name))
        self.partList.setHorizontalHeaderLabels(list(columns_name))
        self.partList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.partList.setSelectionBehavior(QAbstractItemView.SelectRows)
        r_number = len(parts) if parts is not None else 0
        self.partList.setRowCount(r_number)
        if r_number < 1:
            return
        index = 0
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
            for j in range(5, 10):
                if columns_flags[j] == 1:
                    ss = p.get_specified_tag(self.__database, columns_name[column_index])
                    t_item = QTableWidgetItem(ss)
                    self.partList.setItem(index, column_index, t_item)
                    column_index += 1

            if columns_flags[10] == 1:
                comment_item = QTableWidgetItem(p.comment)
                self.partList.setItem( index, column_index, comment_item )
            index += 1
        QTableWidget.resizeColumnsToContents(self.partList)
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
        self.despLineEdit.setText(None)


class PartStructurePanel(QFrame):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.__database = database
        self.__parent = parent
        self.__structureTree = QTreeWidget(self)
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
