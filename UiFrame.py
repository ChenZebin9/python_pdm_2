import _thread
import os
import subprocess
import time
from decimal import Decimal

from PyQt5.QtCore import (QThread, pyqtSignal)
from PyQt5.QtGui import (QIntValidator, QPixmap, QCursor, QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QFrame, QLabel, QTextEdit,
                             QListWidget, QHBoxLayout, QFormLayout, QVBoxLayout,
                             QPushButton, QComboBox, QTableWidget,
                             QTableWidgetItem, QListWidgetItem, QTableView,
                             QMenu, QSplitter, QFileDialog, QCheckBox)

from Part import Part, DoStatistics
from db.DatabaseHandler import DatabaseHandler
from ui.MyTreeWidget import *
from utils.CaptureImage import WScreenShot, ConfirmImage


class PartInfoPanel( QFrame ):

    def __init__(self, parent=None, mode=0):
        """
        单元的信息Widget
        :param parent:
        :param mode: 0=在主窗口中，1=在新建单元的对话框中
        """
        super().__init__( parent )
        self.__mode = mode
        self.part_id = None
        self.idLineEdit = QLineEdit( self )
        self.nameLineEdit = QLineEdit( self )
        self.englishNameLineEdit = QLineEdit( self )
        self.descriptionLineEdit = QLineEdit( self )
        self.commentTextEdit = QTextEdit( self )
        self.tagListWidget = QListWidget( self )
        # 在新建模式下，显示
        self.tagTableWidget = QTableWidget( self )
        self.__init_ui()

    def init_data(self, part_id, tag_data):
        """
        数据的初始化，仅在新建单元时被调用
        :param tag_data: {}, Tag 表格的数据
        :param part_id: int, 可用的 Part Id
        :return:
        """
        self.part_id = part_id
        self.idLineEdit.setText( '{:08d}'.format( part_id ) )
        self.idLineEdit.setEnabled( False )
        self.tagTableWidget.setRowCount( len( tag_data ) )
        self.tagTableWidget.setColumnCount( 2 )
        self.tagTableWidget.setHorizontalHeaderLabels( ['标签名', '值'] )
        i = 0
        for k in tag_data:
            item = QTableWidgetItem( k )
            self.tagTableWidget.setItem( i, 0, item )
            value_items = tag_data[k]
            if value_items is not None:
                a_combo_box = QComboBox()
                for v in value_items:
                    a_combo_box.addItem( v )
                a_combo_box.setEditable( True )
                a_combo_box.setCurrentIndex( -1 )
                self.tagTableWidget.setCellWidget( i, 1, a_combo_box )
            else:
                a_edit_line = QLineEdit()
                self.tagTableWidget.setCellWidget( i, 1, a_edit_line )
            i += 1
        self.tagTableWidget.horizontalHeader().setStretchLastSection( True )
        self.tagTableWidget.resizeColumnsToContents()

    def __init_ui(self):
        self.commentTextEdit.setTabChangesFocus( True )

        h_box = QHBoxLayout( self )

        form_layout = QFormLayout( self )
        form_layout.setLabelAlignment( Qt.AlignRight )
        form_layout.addRow( '序号', self.idLineEdit )
        form_layout.addRow( '名称', self.nameLineEdit )
        form_layout.addRow( '英文名称', self.englishNameLineEdit )
        form_layout.addRow( '描述', self.descriptionLineEdit )
        form_layout.addRow( '备注', self.commentTextEdit )

        self.idLineEdit.setAlignment( Qt.AlignHCenter )

        self.nameLineEdit.setContextMenuPolicy( Qt.NoContextMenu )
        self.englishNameLineEdit.setContextMenuPolicy( Qt.NoContextMenu )
        self.descriptionLineEdit.setContextMenuPolicy( Qt.NoContextMenu )
        self.commentTextEdit.setContextMenuPolicy( Qt.NoContextMenu )

        tagLayout = QVBoxLayout( self )
        tagLabel = QLabel( '标签' )
        tagLabel.setAlignment( Qt.AlignCenter )
        tagLayout.addWidget( tagLabel )
        if self.__mode == 0:
            tagLayout.addWidget( self.tagListWidget )
            self.tagTableWidget.hide()
        else:
            tagLayout.addWidget( self.tagTableWidget )
            self.tagListWidget.hide()

        h_box.addLayout( form_layout )
        h_box.addLayout( tagLayout )

        self.setLayout( h_box )
        if self.__mode == 0:
            self.setFixedHeight( 200 )

    def set_part_info(self, part):
        self.idLineEdit.setText( '' )
        self.nameLineEdit.setText( '' )
        self.englishNameLineEdit.setText( '' )
        self.descriptionLineEdit.setText( '' )
        self.commentTextEdit.setText( '' )
        self.tagListWidget.clear()
        if part is not None:
            self.part_id = part.get_part_id()
            self.idLineEdit.setText( part.part_id )
            self.idLineEdit.setEnabled( False )
            self.nameLineEdit.setText( part.name )
            self.englishNameLineEdit.setText( part.english_name )
            self.descriptionLineEdit.setText( part.description )
            self.commentTextEdit.setText( part.comment )
            for t in part.tags:
                one_item = QListWidgetItem( t.get_whole_name(), parent=self.tagListWidget )
                one_item.setData( Qt.UserRole, t )
                self.tagListWidget.addItem( one_item )

    def get_part_info(self):
        """
        获取单元的信息
        :return: 零件号，名称，英文名称，描述，备注，标签{标签名、标签值}
        """
        tag_dict = {}
        row_count = self.tagTableWidget.rowCount()
        for i in range( row_count ):
            value_cell = self.tagTableWidget.cellWidget( i, 1 )
            if type( value_cell ) is QLineEdit:
                value_text = value_cell.text().strip()
            else:
                value_text = value_cell.currentText().strip()
            if len( value_text ) < 1:
                continue
            key_item = self.tagTableWidget.item( i, 0 )
            the_key = key_item.text()
            tag_dict[the_key] = value_text
        return self.part_id, self.nameLineEdit.text().strip(), self.englishNameLineEdit.text().strip(), \
               self.descriptionLineEdit.text().strip(), self.commentTextEdit.toPlainText().strip(), tag_dict


class PartInfoPanelInMainWindow( QFrame ):

    def __init__(self, parent=None, work_folder=None, database=None, is_offline=False):
        # 当前被选定的 part
        self.__current_part: Part = None
        self.__work_folder = work_folder
        self.__parent = parent
        self.__database: DatabaseHandler = database
        self.__vault = None
        self.__is_offline = is_offline
        self.__current_select_tag = None
        # 本地文件的存放路径，当为 None 时，表示不访问本地图纸。
        self.__local_path = None
        super().__init__( parent )
        self.partInfo = PartInfoPanel( parent )
        self.imageLabel = QLabel( self )
        self.__part_image_set = False  # 相应的图片被设置好了
        self.relationFilesList = QListWidget( self )

        """ 操作单元信息的按钮 """
        self.__save_to_part_button = QPushButton( '保存' )
        self.__copy_part_button = QPushButton( '复制' )
        self.__hyper_link_button = QPushButton( '采购链接' )
        self.__the_hyper_link_label = QLabel()

        """ 标签清单的右键菜单 """
        self.__menu_4_tag_list = QMenu( parent=self.partInfo.tagListWidget )
        self.__del_tag_from_list = self.__menu_4_tag_list.addAction( '删除' )
        self.__modify_tag_name_in_list = self.__menu_4_tag_list.addAction( '修改' )
        self.__copy_tag_name_from_list = self.__menu_4_tag_list.addAction( '复制标签文本' )
        self.__del_tag_from_list.triggered.connect( self.__remove_tag_from_part )
        self.__modify_tag_name_in_list.triggered.connect( self.__modify_tag_in_part )
        self.__copy_tag_name_from_list.triggered.connect( self.__copy_tag_name )

        """ 一些按钮的响应语句 """
        self.__save_to_part_button.clicked.connect( self.__save_to_part_handler )
        self.__copy_part_button.clicked.connect( self.__copy_part_handler )
        self.__hyper_link_button.clicked.connect( self.__hyper_link_handler )

        """ 一些文本框的响应语句 """
        self.partInfo.nameLineEdit.textEdited.connect( lambda: self.__save_to_part_button.setEnabled( True ) )
        self.partInfo.englishNameLineEdit.textEdited.connect( lambda: self.__save_to_part_button.setEnabled( True ) )
        self.partInfo.descriptionLineEdit.textEdited.connect( lambda: self.__save_to_part_button.setEnabled( True ) )
        self.partInfo.commentTextEdit.textChanged.connect( lambda: self.__save_to_part_button.setEnabled( True ) )

        """ 图形显示的右键菜单 """
        self.__menu_4_image_label = QMenu( parent=self.imageLabel )
        self.__capture_image = self.__menu_4_image_label.addAction( '截图' )
        self.__clean_image = self.__menu_4_image_label.addAction( '清除' )
        self.__export_image = self.__menu_4_image_label.addAction( '导出' )
        self.imageLabel.setContextMenuPolicy( Qt.CustomContextMenu )
        self.imageLabel.customContextMenuRequested.connect( self.__on_custom_context_menu_requested )
        self.__capture_image.triggered.connect( self.__do_image_capture )
        self.__clean_image.triggered.connect( self.__do_image_clean )
        self.__export_image.triggered.connect( self.__do_image_export )

        """ 链接文件的右键菜单 """
        self.__current_file_item = None
        self.__menu_4_files_list = QMenu( parent=self.relationFilesList )
        self.__open_file_menu = self.__menu_4_files_list.addAction( '打开文件' )
        self.__open_file_location = self.__menu_4_files_list.addAction( '进入文件所在目录' )
        self.relationFilesList.setContextMenuPolicy( Qt.CustomContextMenu )
        self.relationFilesList.customContextMenuRequested.connect( self.__on_custom_context_menu_requested )
        self.__open_file_menu.triggered.connect( self.__open_file_by_menu )
        self.__open_file_location.triggered.connect( self.__do_open_file_location )

        self.__setup_ui()

        """ 额外的参数传递变量 """
        self.__output_filename = ''
        # 当前所选中的链接文件的版本
        self.__current_file_version = {}

    def __setup_ui(self):
        h_box = QHBoxLayout( self )
        splitter = QSplitter( Qt.Horizontal, self )
        splitter.addWidget( self.partInfo )

        v_splitter = QSplitter( Qt.Vertical, self )
        self.__save_to_part_button.setFixedSize( 80, 30 )
        self.__copy_part_button.setFixedSize( 80, 30 )
        self.__hyper_link_button.setFixedSize( 80, 30 )
        self.__the_hyper_link_label.setFixedHeight( 30 )
        self.__save_to_part_button.setEnabled( False )
        self.__copy_part_button.setEnabled( False )
        v_splitter.addWidget( self.__save_to_part_button )
        v_splitter.addWidget( self.__copy_part_button )
        v_splitter.addWidget( self.__hyper_link_button )
        v_splitter.addWidget( self.__the_hyper_link_label )
        splitter.addWidget( v_splitter )

        self.imageLabel.setFixedSize( 200, 200 )
        self.imageLabel.setAlignment( Qt.AlignCenter )
        splitter.addWidget( self.imageLabel )
        splitter.addWidget( self.relationFilesList )
        self.relationFilesList.itemDoubleClicked.connect( self.__open_file )
        self.relationFilesList.itemSelectionChanged.connect( self.__linked_file_changed )
        h_box.addWidget( splitter )
        self.setLayout( h_box )

        self.partInfo.tagListWidget.setContextMenuPolicy( Qt.CustomContextMenu )
        self.partInfo.tagListWidget.customContextMenuRequested.connect( self.__on_custom_context_menu_requested )

    def __do_image_capture(self):
        """ 进行屏幕的框选截图 """
        # 将主窗口最小化
        self.__parent.hide()
        time.sleep( 0.5 )
        img_data = None
        try:
            win = WScreenShot()
            win.exec_()
            if win.image_file is not None:
                confirm_dialog = ConfirmImage( win.image_file )
                confirm_dialog.exec_()
                # 更新数据
                img_data = confirm_dialog.get_img_data()
                if img_data is not None:
                    self.__database.set_part_thumbnail( self.__current_part.get_part_id(), img_data )
                os.unlink( win.image_file )
                img_data = self.__database.get_thumbnail_2_part( self.__current_part.get_part_id() )
                if img_data is not None:
                    img = QPixmap()
                    img.loadFromData( img_data )
                    n_img = img.scaled( 200, 200, aspectRatioMode=Qt.KeepAspectRatio )
                    self.imageLabel.setPixmap( n_img )
                    self.__part_image_set = True
        finally:
            self.__parent.show()

    def __do_image_clean(self):
        resp = QMessageBox.question( self.__parent, '警告', '确定要清除缩略图？', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No )
        if resp == QMessageBox.No:
            return
        self.__database.clean_part_thumbnail( self.__current_part.get_part_id() )
        self.imageLabel.clear()

    def __do_image_export(self):
        if not self.__part_image_set:
            QMessageBox.warning( self.__parent, '', '没有图片可以导出。', QMessageBox.Yes )
            return
        the_image = self.imageLabel.pixmap()
        image_2_export = the_image.scaled( 300, 300, Qt.KeepAspectRatio, Qt.FastTransformation )
        t = QFileDialog.getSaveFileName( self.__parent, '保存图片', '', 'BMP(*.bmp)' )
        filename = t[0]
        if filename is not None and len( filename ) > 0:
            image_2_export.save( filename, format='BMP' )
            QMessageBox.information( self.__parent, '', '导出完毕。' )
            return
        QMessageBox.warning( self.__parent, '', '取消导出。' )

    def __save_to_part_handler(self):
        """ 点击保存时的响应语句 """
        the_name = self.partInfo.nameLineEdit.text().strip()
        the_english_name = self.partInfo.englishNameLineEdit.text().strip()
        the_description = self.partInfo.descriptionLineEdit.text().strip()
        the_comment = self.partInfo.commentTextEdit.toPlainText().strip()
        if the_name == self.__current_part.name and the_english_name == self.__current_part.english_name \
                and the_description == self.__current_part.description and the_comment == self.__current_part.comment:
            self.__save_to_part_button.setEnabled( False )
            return
        # 进行实质上的修改
        self.__database.update_part_info( self.__current_part.get_part_id(), the_name, the_english_name,
                                          the_description, the_comment )
        if self.__vault is not None:
            # 更新PDM的数据
            try:
                ifs = self.__database.get_part_info_quick( self.__current_part.get_part_id() )
                if ifs is None:
                    raise Exception( '居然没找到响应的Part！' )
                ifs.insert( 3, the_english_name )
                linked_file = self.__current_part.get_related_files( self.__database )
                if len( linked_file ) > 0:
                    file_s = []
                    for k in linked_file.keys():
                        file_s.extend( linked_file[k] )
                    _thread.start_new_thread( self.__vault.UpdateFileInPdm, (file_s, ifs) )
            except Exception as ex:
                QMessageBox.critical( self.__parent, '更新PDM数据时失败', str( ex ), QMessageBox.Yes )
        self.__save_to_part_button.setEnabled( False )

    def __hyper_link_handler(self):
        """
        处理项目的采购链接
        :return:
        """
        if self.__current_part is None:
            self.__parent.set_status_bar_text( '没有选择项目！' )
            return
        part_id = self.__current_part.get_part_id()
        the_link = self.__database.get_part_hyper_link( part_id )
        original_text = ''
        if the_link is not None:
            original_text = the_link
        text, ok = QInputDialog.getText( self.__parent, '输入或更改', '采购链接', echo=QLineEdit.Normal,
                                         text=original_text )
        if ok:
            self.__database.set_part_hyper_link( part_id, text )
            self.__database.save_change()

    def __copy_part_handler(self):
        """ 点击复制时的响应语句 """
        pass

    def set_part_operate_button_status(self, which_button, status):
        """
        从外部设置PART信息操作按钮的状态
        :param which_button: 哪一个按钮？save - 1; copy - 2。
        :param status: enable的状态。
        :return:
        """
        if which_button == 1:
            button = self.__save_to_part_button
        elif which_button == 2:
            button = self.__copy_part_button
        else:
            button = None

        if button is not None:
            button.setEnabled( status )

    def __on_custom_context_menu_requested(self, pos):
        if self.sender() == self.partInfo.tagListWidget:
            if self.partInfo.tagListWidget.count() < 1:
                return
            item = self.partInfo.tagListWidget.itemAt( pos )
            self.__current_select_tag = item
            if item is not None:
                self.__menu_4_tag_list.exec( QCursor.pos() )
        elif self.sender() == self.relationFilesList:
            if self.relationFilesList.count() < 1:
                return
            self.__current_file_item = self.relationFilesList.itemAt( pos )
            if self.__current_file_item is not None:
                self.__menu_4_files_list.exec( QCursor.pos() )
        elif self.sender() == self.imageLabel:
            if self.__current_part is not None:
                self.__menu_4_image_label.exec( QCursor.pos() )

    def set_use_local_pdf_first(self, local_path=None):
        """
        设置双击图纸时，是否优先使用本地的PDF文件
        :param local_path: 本地图纸的存放路径
        :return:
        """
        self.__local_path = local_path

    def __copy_tag_name(self):
        the_tag: Tag = self.__current_select_tag.data( Qt.UserRole )
        clipboard = QApplication.clipboard()
        clipboard.setText( the_tag.name )

    def __remove_tag_from_part(self):
        rsp = QMessageBox.question( self.__parent, '', '确定要移除该标签？',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No )
        if rsp == QMessageBox.No:
            return
        index = self.partInfo.tagListWidget.currentRow()
        self.partInfo.tagListWidget.takeItem( index )
        the_tag: Tag = self.__current_select_tag.data( Qt.UserRole )
        tag_id = the_tag.tag_id
        self.__database.del_tag_from_part( tag_id, self.partInfo.part_id )

    def __modify_tag_in_part(self):
        # TODO 修改Part里面某个标签名
        pass

    def set_part_info(self, part, database):
        self.relationFilesList.setCurrentItem( None )
        self.relationFilesList.clear()
        self.imageLabel.clear()
        self.__part_image_set = False
        self.__the_hyper_link_label.setText( '' )
        self.__the_hyper_link_label.setOpenExternalLinks( False )
        self.__current_part = part
        self.partInfo.set_part_info( part )

        if self.__current_part is None:
            return

        files_list = database.get_files_2_part( part.get_part_id() )
        self.relationFilesList.addItems( files_list )
        img_data = database.get_thumbnail_2_part( part.get_part_id() )
        if img_data is not None:
            img = QPixmap()
            img.loadFromData( img_data )
            n_img = img.scaled( 200, 200, aspectRatioMode=Qt.KeepAspectRatio )
            self.imageLabel.setPixmap( n_img )
            self.__part_image_set = True

        # 显示项目的采购链接
        hyper_link = self.__database.get_part_hyper_link( part.get_part_id() )
        if hyper_link is not None:
            self.__the_hyper_link_label.setText( f'<a href=\"{hyper_link}\">采购链接' )
            self.__the_hyper_link_label.setOpenExternalLinks( True )

        self.__current_select_tag = None
        self.__current_file_item = None

    def __do_open_file_location(self):
        if self.__current_file_item is not None:
            file_name = self.__current_file_item.text()
            # 为隐藏执行命令时的cmd窗口，载自网络
            DETACHED_PROCESS = 0x00000008
            subprocess.call( f'explorer.exe /e,/select,{self.__work_folder}\\{file_name}',
                             creationflags=DETACHED_PROCESS )

    def __open_file_by_menu(self):
        if self.__current_file_item is not None:
            self.__open_file( self.__current_file_item )

    def __open_file(self, item: QListWidgetItem):
        try:
            file_name = item.text()
            file_version = None
            if file_name in self.__current_file_version:
                file_version = f"{self.__current_part.part_id}.{self.__current_file_version[file_name]}" \
                               f"-{self.__current_part.name}"
            suffix = os.path.splitext( file_name )[1]
            if suffix.upper() == '.SLDDRW':
                if self.__local_path is not None and os.path.exists( self.__local_path ):
                    # 进行本地PDF文件的查找
                    part_num = self.__current_part.part_id
                    the_file = []
                    dirs = os.listdir( self.__local_path )
                    version_alarm = file_version is None
                    for f in dirs:
                        if f.startswith( part_num ) and os.path.splitext( f )[1].upper() == '.PDF':
                            the_file.append( f )
                            one_file_name = os.path.splitext( f )[0]
                            if file_version is not None:
                                if one_file_name > file_version:
                                    version_alarm = False
                    open_pdf = True
                    check_last_version = version_alarm and len( the_file ) > 0
                    if (not self.__is_offline) and check_last_version:
                        resp = QMessageBox.question( self.__parent, '', '本地PDF的图纸版本是旧版的，是否要打开原有文件？',
                                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No )
                        if resp == QMessageBox.No:
                            open_pdf = False
                    if open_pdf or not check_last_version:
                        if len( the_file ) > 0:
                            the_file.sort( reverse=True )
                            item, ok = QInputDialog.getItem( self, '选择图纸', '文件名：', the_file, 0, False )
                            if ok and item:
                                os.startfile( f'{self.__local_path}\\{item}' )
                            return
            full_path = '{0}\\{1}'.format( self.__work_folder, file_name )
            if os.path.exists( full_path ):
                os.startfile( full_path )
            else:
                QMessageBox.information( self.__parent, '无法打开', '{0}文件不存在'.format( full_path ), QMessageBox.Ok )
        except Exception as e:
            QMessageBox.critical( self.__parent, '打开时出错', str( e ), QMessageBox.Ok )

    def set_vault(self, vault):
        self.__vault = vault

    def __linked_file_changed(self):
        try:
            item = self.relationFilesList.currentItem()
            self.__current_file_item = item
            if self.__vault is None or item is None:
                return
            file_name = item.text()
            datas_ = self.__vault.GetFileStatus( file_name )
            datas = list( datas_ )
            self.__current_file_version[file_name] = PartInfoPanelInMainWindow.create_version( datas )
            self.__parent.set_status_bar_text( file_name + ' ' + datas[0] )
        except Exception as e:
            self.__parent.set_status_bar_text( 'Error: {0}'.format( e ) )

    @staticmethod
    def create_version(the_str):
        status_flag = 'P'
        if the_str[1] == '已审批' or the_str[1] == '已批准':
            status_flag = ''
        lock_status = 'E'
        if the_str[2] == '否':
            lock_status = ''
        return '{0}{1}{2}'.format( the_str[3], status_flag, lock_status )


class ChildrenTablePanel( QFrame ):
    """
    mode = 0: 子清单
    mode = 1: 父清单
    """

    Columns_header = ['序号', '零件号', '名称', '描述', '统计数量', '实际数量', '状态', '备注']

    def __init__(self, parent=None, database=None, mode=0):
        super().__init__( parent )
        self.__parent = parent
        self.__database = database
        self.__mode = mode
        # 当前所编辑的父项目, Part
        self.__part_list_belong_2: Part = None
        # 当前所选择的父项目, Part
        self.__parent_part: Part = None
        # 当前所选择的子项目的零件号, int
        self.__select_part_id = None
        # 当前所选择的子项目的序号
        self.__select_part_index = -1
        # 当前所选择的子项目所在的行号
        self.__select_row = -1
        # 所有当前被选择的Id
        self.__all_selected_id = None
        # 当数据进行后台更新时
        self.__update_data_silence = False
        self.childrenTableWidget = QTableWidget( self )
        self.addItemButton = QPushButton( self )
        self.deleteItemButton = QPushButton( self )
        self.sortItemButton = QPushButton( self )
        self.saveAllItemsButton = QPushButton( self )
        self.go2ItemButton = QPushButton( self )
        self.editModeCheckBox = QCheckBox( self )
        self.__init_ui()
        # 编辑模式下添加及删除的行
        self.__2_add_row = []
        self.__2_remove_row = []
        self.__counter = 0

    def __init_ui(self):
        self.addItemButton.setText( '添加' )
        self.deleteItemButton.setText( '删除' )
        self.sortItemButton.setText( '排序' )
        self.saveAllItemsButton.setText( '保存' )
        self.addItemButton.setEnabled( False )
        self.deleteItemButton.setEnabled( False )
        self.sortItemButton.setEnabled( False )
        self.saveAllItemsButton.setEnabled( False )
        self.go2ItemButton.setText( '跳转...' )
        self.editModeCheckBox.setText( '编辑模式' )
        h_box = QHBoxLayout( self )
        v_box = QVBoxLayout( self )
        v_box.setAlignment( Qt.AlignTop )
        if self.__mode == 0:  # 表示是子项目清单
            v_box.addWidget( self.addItemButton )
            v_box.addWidget( self.deleteItemButton )
            v_box.addWidget( self.sortItemButton )
            v_box.addWidget( self.saveAllItemsButton )
            v_box.addWidget( self.editModeCheckBox )
        else:
            self.addItemButton.setVisible( False )
            self.deleteItemButton.setVisible( False )
            self.sortItemButton.setVisible( False )
            self.saveAllItemsButton.setVisible( False )
            self.editModeCheckBox.setVisible( False )
        v_box.addWidget( self.go2ItemButton )
        h_box.addLayout( v_box )
        h_box.addWidget( self.childrenTableWidget )
        self.setLayout( h_box )
        # 表格的选择
        self.childrenTableWidget.itemSelectionChanged.connect( self.__table_select_changed )
        # 按键的动作响应
        self.go2ItemButton.clicked.connect( self.__go_2_part )
        self.addItemButton.clicked.connect( self.__add_2_part_list )
        self.deleteItemButton.clicked.connect( self.__remove_from_part_list )
        self.sortItemButton.clicked.connect( self.__sort_part_list )
        self.saveAllItemsButton.clicked.connect( self.__save_part_list )
        self.editModeCheckBox.toggled.connect( lambda: self.__set_list_edit_mode( self.editModeCheckBox.isChecked() ) )
        # 编辑某个单元格的响应函数
        self.childrenTableWidget.cellChanged.connect( self.__item_change )

    def __item_change(self, r, c):
        if self.__update_data_silence:
            return
        # itemChanged 的响应函数
        if c == 4:
            item = self.childrenTableWidget.item( r, c )
            data = item.data( Qt.DisplayRole )
            other_item = self.childrenTableWidget.item( r, c + 1 )
            other_item.setData( Qt.DisplayRole, data )

    def __add_2_part_list(self):
        self.__update_data_silence = True
        # 将项目添加到清单中
        if self.__parent_part is None:
            self.__parent.set_status_bar_text( '没有选择可添加的项目。' )
            return
        if self.__parent_part == self.__part_list_belong_2:
            self.__parent.set_status_bar_text( '无法将自身添加为子项目。' )
            return
        if self.__select_row < 0:
            target_row = self.childrenTableWidget.rowCount()
            if target_row > 0:
                jj: QTableWidgetItem = self.childrenTableWidget.item( target_row - 1, 0 )
                jj_text = jj.text()
                next_index = int( jj_text ) + 1
            else:
                next_index = 10
        else:
            target_row = self.__select_row + 1
            next_index = self.__select_part_index + 1
        if self.__all_selected_id is not None and len( self.__all_selected_id ) > 0:
            for the_id in self.__all_selected_id:
                p = Part.get_parts( self.__database, part_id=the_id )[0]
                p.get_tags( self.__database )
                self.childrenTableWidget.insertRow( target_row )
                # 填入一行的数据
                index_item = QTableWidgetItem()
                index_item.setData( Qt.DisplayRole, next_index )
                id_item = QTableWidgetItem( p.part_id )
                id_item.setFlags( id_item.flags() & ~Qt.ItemIsEditable )
                name_item = QTableWidgetItem( p.name )
                name_item.setFlags( name_item.flags() & ~Qt.ItemIsEditable )
                status_item = QTableWidgetItem( p.status )
                status_item.setFlags( status_item.flags() & ~Qt.ItemIsEditable )
                description_item = QTableWidgetItem( p.description )
                description_item.setFlags( description_item.flags() & ~Qt.ItemIsEditable )
                comment_item = QTableWidgetItem()
                qty_1_item = QTableWidgetItem()
                qty_1_item.setData( Qt.DisplayRole, 1.0 )
                qty_1_item.setTextAlignment( Qt.AlignHCenter )
                qty_2_item = QTableWidgetItem()
                qty_2_item.setData( Qt.DisplayRole, 1.0 )
                qty_2_item.setTextAlignment( Qt.AlignHCenter )
                self.childrenTableWidget.setItem( target_row, 0, index_item )
                self.childrenTableWidget.setItem( target_row, 1, id_item )
                self.childrenTableWidget.setItem( target_row, 2, name_item )
                self.childrenTableWidget.setItem( target_row, 3, description_item )
                self.childrenTableWidget.setItem( target_row, 4, qty_1_item )
                self.childrenTableWidget.setItem( target_row, 5, qty_2_item )
                self.childrenTableWidget.setItem( target_row, 6, status_item )
                self.childrenTableWidget.setItem( target_row, 7, comment_item )
                target_row += 1
                next_index += 1
        QTableWidget.resizeColumnsToContents( self.childrenTableWidget )
        QTableWidget.resizeRowsToContents( self.childrenTableWidget )
        self.__parent.set_status_bar_text( f'添加了{next_index}子项目。' )
        self.__update_data_silence = False

    def __remove_from_part_list(self):
        self.__update_data_silence = True
        # 从清单中移除
        if self.__select_row >= 0:
            part_id_item: QTableWidgetItem = self.childrenTableWidget.item( self.__select_row, 1 )
            data = part_id_item.data( Qt.UserRole )
            if data is not None:
                self.__2_remove_row.append( data )
            self.childrenTableWidget.removeRow( self.__select_row )
        else:
            self.__parent.set_status_bar_text( '没有选择要移除的子项目。' )
        self.__update_data_silence = False

    def __sort_part_list(self):
        self.__update_data_silence = True
        # 根据index对清单进行排序
        r_c = self.childrenTableWidget.rowCount()
        if r_c < 2:
            return
        c_c = 8
        temp_dict = {}
        for i in range( r_c ):
            f_cell = self.childrenTableWidget.takeItem( i, 0 )
            k = f_cell.data( Qt.DisplayRole )
            one_row = [f_cell]
            for j in range( 1, c_c ):
                one_row.append( self.childrenTableWidget.takeItem( i, j ) )
            temp_dict[k] = one_row
        sorted_list = list( temp_dict.keys() )
        sorted_list.sort()
        j = 0
        for k in sorted_list:
            one_row = temp_dict[k]
            index_item = QTableWidgetItem()
            index_item.setData( Qt.DisplayRole, 10 * (j + 1) )
            self.childrenTableWidget.setItem( j, 0, index_item )
            for c in range( 1, c_c ):
                self.childrenTableWidget.setItem( j, c, one_row[c] )
            j += 1
        QTableWidget.resizeColumnsToContents( self.childrenTableWidget )
        QTableWidget.resizeRowsToContents( self.childrenTableWidget )
        self.__parent.set_status_bar_text( '排序完成。' )
        self.__update_data_silence = False

    def __save_part_list(self):
        # 保存清单数据
        row_cc = self.childrenTableWidget.rowCount()
        for i in range( row_cc ):
            index = (self.childrenTableWidget.item( i, 0 )).data( Qt.DisplayRole )
            part_id_item = self.childrenTableWidget.item( i, 1 )
            part_id = int( part_id_item.text().lstrip( '0' ) )
            relation_id = part_id_item.data( Qt.UserRole )
            sum_qty = (self.childrenTableWidget.item( i, 4 )).data( Qt.DisplayRole )
            actual_qty = (self.childrenTableWidget.item( i, 5 )).data( Qt.DisplayRole )
            relation_comment = (self.childrenTableWidget.item( i, 7 )).text()
            self.__database.update_part_relation( relation_id, index, self.__part_list_belong_2.get_part_id(),
                                                  part_id, sum_qty, actual_qty, relation_comment )
        for r in self.__2_remove_row:
            self.__database.remove_part_relation( r )
        self.__database.save_change()
        self.__2_remove_row.clear()
        self.set_part_children( self.__part_list_belong_2, self.__database )
        self.__parent.set_status_bar_text( '完成子清单的更新。' )

    def __set_list_edit_mode(self, is_edit_mode):
        self.__update_data_silence = True
        # 编辑模式的相应函数
        self.__parent.set_children_list_edit_mode( is_edit_mode )
        self.addItemButton.setEnabled( is_edit_mode )
        self.deleteItemButton.setEnabled( is_edit_mode )
        self.sortItemButton.setEnabled( is_edit_mode )
        self.saveAllItemsButton.setEnabled( is_edit_mode )
        if is_edit_mode:
            self.__part_list_belong_2 = self.__parent_part
        else:
            self.__part_list_belong_2 = None
            self.__2_add_row.clear()
            self.__2_remove_row.clear()
        r_c = self.childrenTableWidget.rowCount()
        c = (0, 4, 5, 7)
        for i in range( r_c ):
            for j in c:
                item = self.childrenTableWidget.item( i, j )
                if is_edit_mode:
                    item.setFlags( item.flags() | Qt.ItemIsEditable )
                else:
                    item.setFlags( item.flags() & (~Qt.ItemIsEditable) )
        self.__update_data_silence = False

    def __table_select_changed(self):
        cc = len( self.childrenTableWidget.selectedItems() )
        if cc < 1:
            self.__select_part_id = None
            self.__select_row = -1
            self.__select_part_index = -1
            return
        item = self.childrenTableWidget.currentItem()
        self.__select_row = item.row()
        ii: QTableWidgetItem = self.childrenTableWidget.item( self.__select_row, 1 )
        if ii is not None:
            ii_text = ii.text().lstrip( '0' )
            self.__select_part_id = int( ii_text )
        else:
            self.__select_part_id = None
        jj: QTableWidgetItem = self.childrenTableWidget.item( self.__select_row, 0 )
        if jj is not None:
            jj_text = jj.text()
            self.__select_part_index = int( jj_text )
        else:
            self.__select_part_index = -1

    def __go_2_part(self):
        self.__parent.do_when_part_list_select( self.__select_part_id )

    def set_part_children(self, part: Part, database, all_selected_id=None):
        self.__update_data_silence = True
        self.__parent_part = part
        self.__all_selected_id = all_selected_id
        self.__select_part_id = None
        if self.editModeCheckBox.isChecked():
            return
        self.childrenTableWidget.setColumnCount( 8 )
        self.childrenTableWidget.setHorizontalHeaderLabels( ChildrenTablePanel.Columns_header )
        if part is None:
            r_number = 0
        else:
            if self.__mode == 0:
                result = part.get_children( database )
            else:
                result = part.get_children( database, mode=1 )
            r_number = len( result ) if result is not None else 0
        self.childrenTableWidget.setRowCount( r_number )
        if r_number < 1:
            return
        index = 0
        for r in result:
            index_item = QTableWidgetItem()
            index_item.setData( Qt.DisplayRole, r[0] )
            p = r[1]
            id_item = QTableWidgetItem( p.part_id )
            # 保存 PartRelationID
            id_item.setData( Qt.UserRole, r[4] )
            name_item = QTableWidgetItem( p.name )
            status_item = QTableWidgetItem( p.status )
            description_item = QTableWidgetItem( p.description )
            comment_item = QTableWidgetItem( p.comment )
            qty_1_item = QTableWidgetItem()
            qty_1_item.setData( Qt.DisplayRole, r[2] )
            qty_1_item.setTextAlignment( Qt.AlignHCenter )
            qty_2_item = QTableWidgetItem()
            qty_2_item.setData( Qt.DisplayRole, r[3] )
            qty_2_item.setData( Qt.UserRole, r[4] )
            qty_2_item.setTextAlignment( Qt.AlignHCenter )
            self.childrenTableWidget.setItem( index, 0, index_item )
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
        for i in range( r_number ):
            for j in range( 8 ):
                item = self.childrenTableWidget.item( i, j )
                item.setFlags( item.flags() & (~Qt.ItemIsEditable) )
        self.__update_data_silence = False


class TagViewPanel( QFrame ):

    def __init__(self, parent=None, database=None):
        super().__init__( parent )
        self.parent = parent
        self.__database = database
        self.filterLineEdit = QLineEdit( self )
        self.cleanTextPushButton = QPushButton( self )
        self.tagTreeWidget = MyTreeWidget2( self, database )
        self.tagFilterListWidget = QListWidget( self )
        """ 进行标签查看的右键菜单 """
        self.__menu_4_tag_tree = QMenu( parent=self.tagTreeWidget )
        self.__add_tag_2_filter = self.__menu_4_tag_tree.addAction( '添加至过滤' )
        self.__add_tag_2_filter.triggered.connect( self.__on_add_2_filter )
        self.__current_selected_tag = None
        """ 进行标签编辑时的右键菜单 """
        self.__selected_tag_in_edit_mode = None
        self.__menu_4_tag_tree_edit = QMenu( parent=self.tagTreeWidget )
        self.__create_new_tag = self.__menu_4_tag_tree_edit.addAction( '插入' )
        self.__del_tag = self.__menu_4_tag_tree_edit.addAction( '删除' )
        self.__rename_tag = self.__menu_4_tag_tree_edit.addAction( '重命名' )
        self.__sort_tag = self.__menu_4_tag_tree_edit.addAction( '排序' )
        self.__cut_tag = self.__menu_4_tag_tree_edit.addAction( '剪切' )
        self.__paste_tag_into = self.__menu_4_tag_tree_edit.addAction( '粘帖' )
        # 用于右键菜单的 item
        self.__item_this_time = None
        self.__create_new_tag.triggered.connect( self.tagTreeWidget.create_new_tag )
        self.__del_tag.triggered.connect( self.tagTreeWidget.del_tag )
        self.__rename_tag.triggered.connect( self.tagTreeWidget.rename_tag )
        self.__sort_tag.triggered.connect( self.tagTreeWidget.sort_tag )
        self.__cut_tag.triggered.connect( self.tagTreeWidget.cut_tag )
        self.__paste_tag_into.triggered.connect( lambda: self.tagTreeWidget.paste_tag_into( self.__item_this_time ) )
        """ 标签过来清单的右键菜单 """
        self.__menu_4_tag_list = QMenu( parent=self.tagFilterListWidget )
        self.__del_tag_from_filter = self.__menu_4_tag_list.addAction( '删除' )
        self.__clean_tag_from_filter = self.__menu_4_tag_list.addAction( '清空' )
        self.__del_tag_from_filter.triggered.connect( self.__on_del_from_filter )
        self.__clean_tag_from_filter.triggered.connect( self.__on_clean_filter )

        self.__edit_mode = False

        self.__init_ui()

    def set_status_message(self, text):
        self.parent.set_status_bar_text( text )

    def set_mode(self, edit_mode):
        self.__edit_mode = edit_mode
        self.tagTreeWidget.set_edit_mode( edit_mode )

    def __init_ui(self):
        self.cleanTextPushButton.setText( '清空' )
        self.cleanTextPushButton.clicked.connect( self.__reset_search )
        self.tagFilterListWidget.setFixedHeight( 100 )
        v_box = QVBoxLayout( self )

        filter_h_box = QHBoxLayout( self )
        filter_h_box.addWidget( QLabel( '过滤' ) )
        filter_h_box.addWidget( self.filterLineEdit )
        filter_h_box.addWidget( self.cleanTextPushButton )

        v_box.addLayout( filter_h_box )
        v_box.addWidget( self.tagTreeWidget )
        v_box.addWidget( self.tagFilterListWidget )

        self.setLayout( v_box )

        self.tagTreeWidget.setHeaderLabels( ['标签'] )
        self.tagTreeWidget.itemSelectionChanged.connect( self.__select_tag )
        self.tagTreeWidget.itemExpanded.connect( self.__when_item_expand )
        self.filterLineEdit.returnPressed.connect( self.__do_search )
        self.tagTreeWidget.setContextMenuPolicy( Qt.CustomContextMenu )
        self.tagTreeWidget.customContextMenuRequested.connect( self.__on_custom_context_menu_requested )

        self.tagFilterListWidget.setContextMenuPolicy( Qt.CustomContextMenu )
        self.tagFilterListWidget.customContextMenuRequested.connect( self.__on_custom_context_menu_requested )

    def __on_custom_context_menu_requested(self, pos):
        if self.sender() is self.tagTreeWidget:
            self.__item_this_time = self.tagTreeWidget.itemAt( pos )
            if not self.__edit_mode:
                if self.__item_this_time is None:
                    self.__current_selected_tag = None
                    return
                t = self.__item_this_time.data( 0, Qt.UserRole )
                self.__current_selected_tag = t
                self.__menu_4_tag_tree.exec( QCursor.pos() )
            else:
                self.tagTreeWidget.item_when_right_click( self.__item_this_time )
                shown = self.__item_this_time is not None
                self.__rename_tag.setVisible( shown )
                self.__sort_tag.setVisible( shown )
                tag_in_clipper = self.tagTreeWidget.clipper_not_empty( self.__database )
                self.__cut_tag.setVisible( shown and not tag_in_clipper )
                self.__del_tag.setVisible( shown )
                self.__paste_tag_into.setVisible( tag_in_clipper )
                self.__menu_4_tag_tree_edit.exec( QCursor.pos() )
        elif self.sender() is self.tagFilterListWidget:
            if self.tagFilterListWidget.count() < 1:
                return
            item = self.tagFilterListWidget.itemAt( pos )
            if item is None:
                self.__del_tag_from_filter.setVisible( False )
            else:
                self.__del_tag_from_filter.setVisible( True )
            self.__menu_4_tag_list.exec( QCursor.pos() )

    def __on_add_2_filter(self):
        if self.__current_selected_tag is None:
            return
        item = QListWidgetItem( self.__current_selected_tag.get_whole_name(), parent=self.tagFilterListWidget )
        item.setData( Qt.UserRole, self.__current_selected_tag )
        self.tagFilterListWidget.addItem( item )
        self.search_by_tag()

    def __on_del_from_filter(self):
        c_r = self.tagFilterListWidget.currentRow()
        item = self.tagFilterListWidget.takeItem( c_r )
        del item
        self.search_by_tag()

    def __on_clean_filter(self):
        self.tagFilterListWidget.clear()

    def search_by_tag(self):
        if self.tagFilterListWidget.count() < 1:
            return
        result = set()
        for i in range( 0, self.tagFilterListWidget.count() ):
            item = self.tagFilterListWidget.item( i )
            t: Tag = item.data( Qt.UserRole )
            ps = Part.get_parts_from_tag( self.__database, t.tag_id )
            ps_s = set( ps )
            if len( result ) < 1:
                result = ps_s
            else:
                result = result.intersection( ps_s )
            if len( ps_s ) < 1:
                return
        r_list = list( result )
        self.parent.show_parts_from_outside( r_list )

    def fill_data(self, tags):
        self.tagTreeWidget.clear()
        for t in tags:
            t.search_children( self.__database )
            node = QTreeWidgetItem( self.tagTreeWidget )
            node.setText( 0, t.name )
            node.setData( 0, Qt.UserRole, t )
            self.tagTreeWidget.addTopLevelItem( node )
            for c in t.children:
                n_node = QTreeWidgetItem( node )
                n_node.setText( 0, c.name )
                n_node.setData( 0, Qt.UserRole, c )
                node.addChild( n_node )

    def __select_tag(self):
        if self.__edit_mode:
            node = self.tagTreeWidget.currentItem()
            if node is None:
                self.__selected_tag_in_edit_mode = None
            else:
                self.__selected_tag_in_edit_mode = node
            return
        node = self.tagTreeWidget.currentItem()
        t = node.data( 0, Qt.UserRole )
        self.parent.do_when_tag_tree_select( t.tag_id )

    def __when_item_expand(self, item: QTreeWidgetItem):
        data = item.data( 0, Qt.UserRole )
        for cc in data.children:
            cc.search_children( self.__database )
            if len( cc.children ) < 1:
                continue
            for c in cc.children:
                node = QTreeWidgetItem( self.tagTreeWidget )
                node.setText( 0, c.name )
                node.setData( 0, Qt.UserRole, c )

    def __reset_search(self):
        self.filterLineEdit.setText( '' )
        tags = Tag.get_tags( self.__database, name=None )
        self.fill_data( tags )

    def __do_search(self):
        filter_text = self.filterLineEdit.text().strip()
        if filter_text == '':
            filter_text = None
        tags = Tag.get_tags( self.__database, name=filter_text )
        self.fill_data( tags )

    def clipboard_is_not_empty(self):
        return self.tagTreeWidget.clipper_not_empty( self.__database )

    def get_current_selected_tag(self):
        # 当前所选的 Tag
        node = self.__selected_tag_in_edit_mode
        if node is None:
            return None
        the_tag = node.data( 0, Qt.UserRole )
        return the_tag


class PartTablePanel( QFrame ):
    # 要改为 static 变量才能实现 connect？
    __stop_above_thread_signal = pyqtSignal()

    def __init__(self, parent=None, database=None):
        super().__init__( parent )
        self.__database: DatabaseHandler = database
        self.__parent = parent
        self.__columns = None
        self.__display_range = []
        self.__show_storage = False  # 显示仓储信息
        self.idLineEdit = QLineEdit( self )
        self.nameComboBox = QComboBox( self )
        self.nameLineEdit = QLineEdit( self )
        self.desLineEdit = QLineEdit( self )
        self.cleanPushButton = QPushButton( self )
        self.all_part_id_selected = []  # 当前所选择的所有Part的ID

        self.partList = QTableWidget( self )
        self.partList.setEditTriggers( QAbstractItemView.NoEditTriggers )
        self.partList.setSelectionBehavior( QAbstractItemView.SelectRows )

        # 一个填写单元格信息的线程
        self.fill_part_info_thread = FillPartInfo( database.copy() )
        self.__stop_above_thread_signal.connect( self.fill_part_info_thread.stop )
        self.fill_part_info_thread.one_cell_2_fill_signal.connect( self.__fill_one_cell )
        self.fill_part_info_thread.all_cells_done_signal.connect( self.__all_cells_filled )

        self.__init_ui()
        self.__current_selected_part = None

    def stop_background_thread(self):
        """ 停止后台线程 """
        self.__stop_above_thread_signal.emit()

    def set_columns(self, columns):
        self.__columns = columns

    def __init_ui(self):
        vbox = QVBoxLayout( self )
        hbox = QHBoxLayout( self )

        hbox.addWidget( QLabel( '序号' ) )
        self.idLineEdit.setValidator( QIntValidator() )
        self.idLineEdit.setMaxLength( 4 )
        self.idLineEdit.setAlignment( Qt.AlignRight )
        hbox.addWidget( self.idLineEdit )
        self.nameComboBox.addItems( ['中文名称', '英文名称'] )
        self.nameComboBox.setCurrentIndex( 0 )
        hbox.addWidget( self.nameComboBox )
        hbox.addWidget( self.nameLineEdit )
        hbox.addWidget( QLabel( '描述' ) )
        hbox.addWidget( self.desLineEdit )
        self.cleanPushButton.setText( '清空' )
        self.cleanPushButton.clicked.connect( self.__clean_input )
        hbox.addWidget( self.cleanPushButton )

        self.idLineEdit.returnPressed.connect( self.do_search )
        self.nameLineEdit.returnPressed.connect( self.do_search )
        self.desLineEdit.returnPressed.connect( self.do_search )

        vbox.addLayout( hbox )
        vbox.addWidget( self.partList )
        self.setLayout( vbox )
        if self.__parent is not None:
            self.partList.itemSelectionChanged.connect( self.__selected_part )

        # 设置点击表头可以排序
        header_goods = self.partList.horizontalHeader()
        header_goods.sectionClicked.connect( self.__sort_by_column )
        #
        self.__sort_flags = {}

    def __selected_part(self):
        ii = self.partList.selectedItems()
        cc = len( ii )
        self.__current_selected_part = 0
        self.all_part_id_selected.clear()
        if cc > 0:
            for i in range( cc ):
                if i % self.partList.columnCount() == 0:
                    item = ii[i]
                    t = item.text()
                    part_num = int( t.lstrip( '0' ) )
                    self.all_part_id_selected.append( part_num )
            # 确定第一个选择的ID
            selected_row = self.partList.currentRow()
            item = self.partList.item( selected_row, 0 )
            if item is not None:
                t = item.text()
                part_num = int( t.lstrip( '0' ) )
                self.__current_selected_part = part_num
                self.__parent.do_when_part_list_select( part_num, self.all_part_id_selected )
        else:
            self.__parent.do_when_part_list_select( 0 )

    def set_display_columns(self, columns):
        self.__columns = columns

    def set_storage_shown_flags(self, is_shown):
        self.__show_storage = is_shown

    def get_current_selected_parts(self):
        """ 获取所有选择了的part的ID """
        items = self.partList.selectedItems()
        result = []
        rr = []
        for item in items:
            r = item.row()
            if r in rr:
                continue
            rr.append( r )
            i = self.partList.item( r, 0 )
            id_ = i.data( Qt.UserRole )
            result.append( id_ )
        return result

    def get_current_selected_part(self):
        return self.__current_selected_part

    def do_search(self):
        part_id = None if self.idLineEdit.text() == '' else int( self.idLineEdit.text() )
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
                parts.extend( self.__display_range )
            else:
                if part_id is not None:
                    for p in self.__display_range:
                        if p.get_part_id() == part_id:
                            tt.append( p )
                else:
                    tt.extend( self.__display_range )
                if name is not None:
                    for p in tt:
                        p_name = p.name.upper()
                        if p_name.find( name.upper() ) > -1:
                            parts.append( p )
                else:
                    parts.extend( tt )
                tt.clear()
                if english_name is not None:
                    for p in parts:
                        p_name = p.english_name.upper()
                        if p_name.find( english_name.upper() ) > -1:
                            tt.append( p )
                else:
                    tt.extend( parts )
                parts.clear()
                if description is not None:
                    for p in tt:
                        if p.description is not None and p.description.find( description ) > -1:
                            parts.append( p )
                else:
                    parts.extend( tt )
        else:
            parts = Part.get_parts( self.__database, part_id=part_id,
                                    name=name, english_name=english_name, description=description )
        self.set_list_data( parts )

    def set_list_header_4_statistics(self, show_price=False):
        # 为统计进行一些准备
        fact_columns = list( self.__columns[1] )
        fact_columns.append( '数量' )
        if show_price:
            fact_columns.extend( ['单价', '总价'] )
        self.partList.setColumnCount( len( fact_columns ) )
        self.partList.setHorizontalHeaderLabels( list( fact_columns ) )
        self.partList.setRowCount( 0 )

    def add_one_part_4_statistics(self, part_id, qty, price=None):
        p: Part = Part.get_parts( self.__database, part_id=part_id )[0]
        r_c = self.partList.rowCount()
        self.partList.insertRow( r_c )
        columns_flags = self.__columns[0]
        columns_name = self.__columns[1]
        column_index = 0
        if columns_flags[0] == 1:
            id_item = QTableWidgetItem( p.part_id )
            id_item.setData( Qt.UserRole, p.get_part_id() )
            self.partList.setItem( r_c, column_index, id_item )
            column_index += 1
        if columns_flags[1] == 1:
            name_item = QTableWidgetItem( p.name )
            self.partList.setItem( r_c, column_index, name_item )
            column_index += 1
        if columns_flags[2] == 1:
            english_item = QTableWidgetItem( p.english_name )
            self.partList.setItem( r_c, column_index, english_item )
            column_index += 1
        if columns_flags[3] == 1:
            description_item = QTableWidgetItem( p.description )
            self.partList.setItem( r_c, column_index, description_item )
            column_index += 1
        if columns_flags[4] == 1:
            status_item = QTableWidgetItem( p.status )
            self.partList.setItem( r_c, column_index, status_item )
            column_index += 1

        # 其它信息，可配置的
        column_start_index = column_index
        column_end_index = len( columns_flags ) - 6
        for j in range( 0, column_end_index ):
            jj = j + column_start_index
            sss = p.get_specified_tag( self.__database, columns_name[jj] )
            ss = QTableWidgetItem( sss )
            self.partList.setItem( r_c, column_index, ss )
            column_index += 1

        if columns_flags[-1] == 1:
            comment_item = QTableWidgetItem( p.comment )
            self.partList.setItem( r_c, column_index, comment_item )
            column_index += 1

        qty_item = QTableWidgetItem()
        qty_item.setData( Qt.DisplayRole, qty )
        self.partList.setItem( r_c, column_index, qty_item )
        del qty_item
        column_index += 1

        if price is not None:
            unit_price_item = QTableWidgetItem()
            unit_price_item.setData( Qt.DisplayRole, price )
            self.partList.setItem( r_c, column_index, unit_price_item )
            sum_price_item = QTableWidgetItem()
            column_index += 1
            sum_price_item.setData( Qt.DisplayRole, price * qty )
            self.partList.setItem( r_c, column_index, sum_price_item )
            del unit_price_item
            del sum_price_item

    def set_list_data_2(self, part_table_data):
        """
        使用 get_parts_2 函数的新一代 list_data
        :param part_table_data:  相对于 set_list_data 包含更多的数据，是一个纯粹的二维数组
        :return:
        """
        a_parts = []  # 接下来要计算的新Parts List
        addition_storage_data = []  # 用于存储额外的仓储数据，与 a_part 对应
        if self.__show_storage:
            has_calculated = []
            for p in part_table_data:
                if p[0] in has_calculated:
                    continue
                n_p = self.__database.get_storing( part_id=p[0] )
                if n_p is not None:
                    for pp in n_p:
                        if pp[2] > 0:
                            has_calculated.append( p[0] )
                            a_parts.append( p )
                            addition_storage_data.append( pp[1:] )
        else:
            a_parts.extend( part_table_data )
        self.partList.setCurrentItem( None )
        columns_name = self.__columns[1]
        column_index = len( columns_name )
        if self.__show_storage:
            columns_name_with_storage_info = columns_name[:]
            columns_name_with_storage_info.extend( ['仓位', '数量', '最近修改日期', '单价'] )
            self.partList.setColumnCount( len( columns_name_with_storage_info ) )
            self.partList.setHorizontalHeaderLabels( list( columns_name_with_storage_info ) )
        else:
            self.partList.setColumnCount( len( columns_name ) )
            self.partList.setHorizontalHeaderLabels( list( columns_name ) )
        r_number = len( a_parts ) if a_parts is not None else 0
        self.partList.setRowCount( r_number )
        self.__sort_flags.clear()
        if r_number < 1:
            return

        index = 0
        for p in a_parts:
            id_item = QTableWidgetItem( '{:08d}'.format( p[0] ) )
            id_item.setData( Qt.UserRole, p[0] )
            self.partList.setItem( index, 0, id_item )
            del id_item

            for i in range( 1, column_index ):
                item = QTableWidgetItem( p[i] )
                self.partList.setItem( index, i, item )
                del item
            # 显示仓储的数据
            if self.__show_storage:
                position = addition_storage_data[index][0]
                if position is not None and len( position ) > 0:
                    position_item = QTableWidgetItem( position )
                    self.partList.setItem( index, column_index, position_item )
                    del position_item
                    qty_item = QTableWidgetItem()
                    qty_item.setData( Qt.DisplayRole, addition_storage_data[index][1] )
                    self.partList.setItem( index, column_index + 1, qty_item )
                    del qty_item
                    record_date_item = QTableWidgetItem()
                    record_date_item.setData( Qt.DisplayRole, addition_storage_data[index][2].strftime( "%Y/%m/%d" ) )
                    self.partList.setItem( index, column_index + 2, record_date_item )
                    del record_date_item
                    unit_price_item = QTableWidgetItem()
                    the_price = None
                    unit_price = addition_storage_data[index][3]
                    if unit_price is not None:
                        the_price = float( unit_price )
                    unit_price_item.setData( Qt.DisplayRole, the_price )
                    self.partList.setItem( index, column_index + 3, unit_price_item )
                    del unit_price_item
            index += 1
        QTableWidget.resizeColumnsToContents( self.partList )
        QTableWidget.resizeRowsToContents( self.partList )
        self.partList.clearSelection()
        self.partList.horizontalHeader().setSectionsClickable( True )
        self.partList.horizontalHeader().setSortIndicatorShown( True )

    def set_list_data(self, parts):
        a_parts = []  # 接下来要计算的新Parts List
        if self.__show_storage:
            has_calculated = []
            for p in parts:
                if p.part_id in has_calculated:
                    continue
                n_p = p.get_storing_data( self.__database )
                if n_p is not None:
                    for pp in n_p:
                        if pp.qty > 0:
                            has_calculated.append( pp.part_id )
                            a_parts.append( pp )
        else:
            a_parts.extend( parts )
        self.partList.setCurrentItem( None )
        columns_flags = self.__columns[0]
        columns_name = self.__columns[1]
        if self.__show_storage:
            columns_name_with_storage_info = columns_name[:]
            columns_name_with_storage_info.extend( ['仓位', '数量', '最近修改日期', '单价'] )
            self.partList.setColumnCount( len( columns_name_with_storage_info ) )
            self.partList.setHorizontalHeaderLabels( list( columns_name_with_storage_info ) )
        else:
            self.partList.setColumnCount( len( columns_name ) )
            self.partList.setHorizontalHeaderLabels( list( columns_name ) )
        r_number = len( a_parts ) if a_parts is not None else 0
        self.partList.setRowCount( r_number )
        self.__sort_flags.clear()
        if r_number < 1:
            return
        index = 0
        the_begin_column_index = 0
        other_column_count = len( columns_flags[5:-1] )
        for p in a_parts:
            column_index = 0
            if columns_flags[0] == 1:
                id_item = QTableWidgetItem( p.part_id )
                id_item.setData( Qt.UserRole, p.get_part_id() )
                self.partList.setItem( index, column_index, id_item )
                del id_item
                column_index += 1
            if columns_flags[1] == 1:
                name_item = QTableWidgetItem( p.name )
                self.partList.setItem( index, column_index, name_item )
                del name_item
                column_index += 1
            if columns_flags[2] == 1:
                english_item = QTableWidgetItem( p.english_name )
                self.partList.setItem( index, column_index, english_item )
                del english_item
                column_index += 1
            if columns_flags[3] == 1:
                description_item = QTableWidgetItem( p.description )
                self.partList.setItem( index, column_index, description_item )
                del description_item
                column_index += 1
            if columns_flags[4] == 1:
                status_item = QTableWidgetItem( p.status )
                self.partList.setItem( index, column_index, status_item )
                del status_item
                column_index += 1

            # 其它信息，可配置的
            the_begin_column_index = column_index
            column_index += other_column_count

            if columns_flags[-1] == 1:
                comment_item = QTableWidgetItem( p.comment )
                self.partList.setItem( index, column_index, comment_item )
                del comment_item
                column_index += 1

            # 显示仓储的数据
            if self.__show_storage:
                if p.position is not None and len( p.position ) > 0:
                    position_item = QTableWidgetItem( p.position )
                    self.partList.setItem( index, column_index, position_item )
                    del position_item
                    qty_item = QTableWidgetItem()
                    qty_item.setData( Qt.DisplayRole, p.qty )
                    self.partList.setItem( index, column_index + 1, qty_item )
                    del qty_item
                    record_date_item = QTableWidgetItem()
                    date_info = p.last_storing_date[:10] if type(
                        p.last_storing_date ) == str else p.last_storing_date.strftime( "%Y/%m/%d" )
                    record_date_item.setData( Qt.DisplayRole, date_info )
                    self.partList.setItem( index, column_index + 2, record_date_item )
                    del record_date_item
                    unit_price_item = QTableWidgetItem()
                    the_price = None
                    if p.unit_price is not None:
                        the_price = float( p.unit_price )
                    unit_price_item.setData( Qt.DisplayRole, the_price )
                    self.partList.setItem( index, column_index + 3, unit_price_item )
                    del unit_price_item
                    column_index += 4
            index += 1
        QTableWidget.resizeColumnsToContents( self.partList )
        QTableWidget.resizeRowsToContents( self.partList )
        self.partList.clearSelection()
        if other_column_count >= 1:
            if self.fill_part_info_thread.isRunning():
                self.__stop_above_thread_signal.emit()
            while self.fill_part_info_thread.isRunning():
                time.sleep( 0.1 )
            self.__parent.set_status_bar_text( '开始填充。' )
            self.fill_part_info_thread.set_data( columns_flags, the_begin_column_index, a_parts )
            self.fill_part_info_thread.start()
        self.partList.horizontalHeader().setSectionsClickable( False )
        self.partList.horizontalHeader().setSortIndicatorShown( False )

    def __sort_by_column(self, column_index):
        # 列排列的相应函数
        sort_flags = False
        if column_index in self.__sort_flags:
            sort_flags = self.__sort_flags[column_index]
        if sort_flags:
            self.partList.sortByColumn( column_index, Qt.AscendingOrder )
            sort_flags = False
        else:
            self.partList.sortByColumn( column_index, Qt.DescendingOrder )
            sort_flags = True
        self.__sort_flags[column_index] = sort_flags

    def __fill_one_cell(self, row_index, column_index, data):
        # TODO 改成list的模式
        cc = column_index
        for d in data:
            item = QTableWidgetItem( d )
            self.partList.setItem( row_index, cc, item )
            del item
            cc += 1

    def __all_cells_filled(self, is_paused):
        if is_paused:
            self.__parent.set_status_bar_text( '填充中断。' )
            return
        self.__parent.set_status_bar_text( '填充完毕。' )
        QTableWidget.resizeColumnsToContents( self.partList )
        QTableWidget.resizeRowsToContents( self.partList )
        self.partList.clearSelection()
        self.partList.horizontalHeader().setSectionsClickable( True )
        self.partList.horizontalHeader().setSortIndicatorShown( True )

    def get_current_parts_id(self):
        result = []
        cc = self.partList.rowCount()
        for i in range( cc ):
            item = self.partList.item( i, 0 )
            id_ = item.data( Qt.UserRole )
            result.append( id_ )
        return tuple( result )

    def set_display_range(self, parts):
        self.__display_range = parts

    def __clean_input(self):
        self.idLineEdit.setText( None )
        self.nameLineEdit.setText( None )
        self.desLineEdit.setText( None )
        self.do_search()


class FillPartInfo( QThread ):
    """
    执行Part信息的填入
    all_cells_done_signal 所有信息都填写完毕
    one_cell_2_fill_signal 填写一个单元
        int - 行号
        int - 列号
        str - 数值
    fill_one_storing_signal 填写一行的仓储信息
        int - 行号
        int - 起始列号（接下来要填充四列）
        str - 仓位
        float - 数量
        datetime - 最近修改日期
        Decimal - 单价
    """
    all_cells_done_signal = pyqtSignal( bool )
    one_cell_2_fill_signal = pyqtSignal( int, int, list )

    Prop_dict = {1: 6, 15: 7, 16: 8, 266: 9, 1288: 10, 2064: 11, 2111: 12, 2112: 13, 2406: 14}

    def __init__(self, database):
        super().__init__()
        self.__c_f = None
        self.__c_n = None
        self.__c_i = None
        self.__parts = None
        self.__stop_flag = False
        self.__db_type = database[0]
        self.__database = database[1]
        self.__do_get_storing = None

    def set_data(self, columns_id, column_index, parts, get_storing=False):
        self.__c_n = columns_id
        self.__c_i = column_index
        self.__parts = parts
        self.__stop_flag = False
        self.__do_get_storing = get_storing

    def stop(self):
        self.__stop_flag = True

    # sqlite3 对象不能在不同的线程中使用，在run中才算另一个线程，仅在__init__赋值时，视为同一线程。
    def run(self):
        try:
            index = 0
            for p in self.__parts:
                if self.__stop_flag:
                    break
                cc = self.__c_i
                part_id = p.get_part_id()
                t_data = self.__database.get_parts_by_config( part_id=part_id, column_config=self.__c_n )
                data = t_data[part_id]
                ss = data[sum( self.__c_n[:5] ):]
                self.one_cell_2_fill_signal.emit( index, cc, ss )
                index += 1
        except Exception as e:
            print( 'FillPartInfo Error: ' + str( e ) )
        finally:
            self.all_cells_done_signal.emit( self.__stop_flag )


class PartStructurePanel( QFrame ):
    # 用户暂停统计线程
    __stop_above_thread_signal = pyqtSignal()

    def __init__(self, parent=None, database=None):
        super().__init__( parent )
        self.__database = database
        self.__parent = parent
        self.__structureTree = QTreeWidget( self )

        # 一个进行物料统计的线程
        self.statistics_thread = DoStatistics( database.copy() )
        # 统计线程的设置
        self.statistics_thread.clean_part_list_signal.connect( self.__parent.set_ready_for_statistics_display )
        self.statistics_thread.add_2_part_list_signal.connect( self.__parent.add_one_item_to_statistics_list )
        self.statistics_thread.finish_statistics_signal.connect( self.__parent.show_statistics_finish_flag )
        self.__stop_above_thread_signal.connect( self.statistics_thread.stop )

        self.__init_ui()

    def stop_background_thread(self):
        """ 停止后台线程 """
        self.__stop_above_thread_signal.emit()

    def __init_ui(self):
        v_box = QVBoxLayout( self )
        v_box.addWidget( self.__structureTree )
        self.setLayout( v_box )
        self.__structureTree.itemExpanded.connect( self.__when_item_expand )
        self.__structureTree.itemSelectionChanged.connect( self.__select_part )

    def fill_data(self, part, children):
        self.__structureTree.setColumnCount( 2 )
        self.__structureTree.setHeaderLabels( ['项目', '数量'] )
        self.__structureTree.clear()
        root = QTreeWidgetItem( self.__structureTree )
        root.setText( 0, '{0} {1}'.format( part.part_id, part.name ) )
        root.setText( 1, '1.0' )
        root.setData( 0, Qt.UserRole, part )
        self.__structureTree.addTopLevelItem( root )
        for c in children:
            node = QTreeWidgetItem()
            p = c[1]
            qty = c[2]
            node.setText( 0, '{0} {1}'.format( p.part_id, p.name ) )
            node.setText( 1, '{0}'.format( qty ) )
            node.setData( 0, Qt.UserRole, p )
            root.addChild( node )
        self.__structureTree.resizeColumnToContents( 0 )

    def __when_item_expand(self, item: QTreeWidgetItem):
        c_count = item.childCount()
        for i in range( 0, c_count ):
            cc = item.child( i )
            pp = cc.data( 0, Qt.UserRole )
            children = pp.get_children( self.__database )
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
                nodes.append( node )
            cc.takeChildren()
            cc.addChildren( nodes )
        self.__structureTree.resizeColumnToContents( 0 )

    def __select_part(self):
        item = self.__structureTree.currentItem()
        if item is None:
            return
        p = item.data( 0, Qt.UserRole )
        if self.__parent is not None:
            self.__parent.do_when_part_list_select( p.get_part_id() )
            stat_setting = self.__parent.get_statistics_setting()
            if stat_setting[0]:
                # 启动一次统计
                if self.statistics_thread.isRunning():
                    self.__stop_above_thread_signal.emit()
                while self.statistics_thread.isRunning():
                    time.sleep( 0.1 )
                self.__parent.set_status_bar_text( '开始统计。' )
                self.statistics_thread.set_data( p.get_part_id(), stat_setting[1:] )
                self.statistics_thread.start()


class CostInfoPanel( QFrame ):
    """
    显示 Part 的采购（领料）成本的表格
    """

    Column_name = ('单号', '单价', '供应商（来源）', '日期')

    def __init__(self, parent=None, database=None):
        super().__init__( parent )
        self.__parent = parent
        self.__database: DatabaseHandler = database
        self.__costTableView = QTableView( self )
        self.__table_modal = QStandardItemModel()
        self.__init_ui()

    def __init_ui(self):
        v_box = QVBoxLayout( self )
        v_box.addWidget( self.__costTableView )
        self.setLayout( v_box )

        self.__costTableView.setModel( self.__table_modal )

    def set_part_cost_info(self, the_part: Part):
        self.__table_modal.clear()
        self.__table_modal.setHorizontalHeaderLabels( CostInfoPanel.Column_name )
        if the_part is None:
            return
        # 获取 ERP 领料信息的数据
        erp_id = the_part.get_specified_tag( self.__database, '巨轮智能ERP物料编码' )
        if erp_id is not '':
            pick_records = self.__database.get_pick_record_throw_erp( erp_id )
            if pick_records is not None:
                for one_record in pick_records:
                    unit_price = one_record[2] / one_record[1]
                    one_row_in_table = [QStandardItem( one_record[0].strip() )]
                    price_item = QStandardItem( '{:.2f}'.format( unit_price ) )
                    price_item.setData( Qt.DisplayRole, unit_price )
                    one_row_in_table.append( price_item )
                    one_row_in_table.append( QStandardItem( '最近领料' ) )
                    if type( one_record[3] ) != str:
                        date_item = QStandardItem( one_record[3].strftime( "%Y-%m-%d" ) )
                    else:
                        t = one_record[3]
                        date_item = QStandardItem( t[:10] )
                    one_row_in_table.append( date_item )
                    self.__table_modal.appendRow( one_row_in_table )
        pdm_records = self.__database.get_price_from_self_record( the_part.get_part_id() )
        if pdm_records is not None:
            for one_record in pdm_records:
                tt = one_record[:]
                t1 = Decimal.from_float( one_record[1] ) if type( one_record[1] ) == float else one_record[1]
                t2 = Decimal.from_float( one_record[2] ) if type( one_record[2] ) == float else one_record[2]
                t3 = Decimal.from_float( one_record[3] ) if type( one_record[3] ) == float else one_record[3]
                t4 = Decimal.from_float( one_record[4] ) if type( one_record[4] ) == float else one_record[4]
                unit_price = (t1 + t2) / (Decimal.from_float( 1.0 ) + t3) / t4
                bill_nr = '{:06d}'.format( one_record[0] )
                one_row_in_table = [QStandardItem( bill_nr )]
                price_item = QStandardItem( '{:.2f}'.format( unit_price ) )
                supplier_item = QStandardItem( one_record[6] )
                if type( one_record[5] ) == str:
                    t = one_record[5]
                    date_item = QStandardItem( t[:10] )
                else:
                    date_item = QStandardItem( one_record[5].strftime( "%Y-%m-%d" ) )
                one_row_in_table.extend( [price_item, supplier_item, date_item] )
                self.__table_modal.appendRow( one_row_in_table )
        if self.__table_modal.rowCount() > 0:
            self.__costTableView.resizeColumnsToContents()
