# coding=gbk

from PyQt5.QtCore import (Qt, QItemSelectionModel, QDate, QModelIndex)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QDialog, QMessageBox, QAbstractItemView, QItemDelegate, QSplitter,
                             QFrame, QVBoxLayout, QInputDialog)

from Part import Part
from db.DatabaseHandler import DatabaseHandler
from ui3.HandleRequirementDialog import *


class NHandleRequirementDialog( QDialog, Ui_Dialog ):

    def __init__(self, parent=None, database=None, config_dict=None):
        self.__parent = parent
        self.__database: DatabaseHandler = database
        # 操作人员
        self.__operator = config_dict['Operator']
        if self.__operator is None:
            self.__operator = '（离线）'
        # 可以操作的数据
        self.__data_s = config_dict['Data']
        # 当前的阶段
        self.__current_process = config_dict['Process']
        self.__source_data = QStandardItemModel()
        self.__dest_data = QStandardItemModel()
        # 入库阶段的特别变量
        self.__default_storage = None
        # 表格排序的数据
        self.__sort_flags = {}
        # 用于上下两个表格的对应关系
        self.__row_map = {}
        # 有进行检索的标记
        self.__after_search = False
        # 源表格的列数
        self.__source_table_column_count = 8
        super( NHandleRequirementDialog, self ).__init__( parent )
        self.setModal( True )
        self.setup_ui()
        self.init_data()

    def setup_ui(self):
        super( NHandleRequirementDialog, self ).setupUi( self )
        main_layout = QVBoxLayout( self )
        self.setLayout( main_layout )

        splitter = QSplitter( Qt.Vertical )
        top_frame = QFrame()
        top_frame.setLayout( self.h2_layout )
        mid_frame = QFrame()
        mid_frame.setLayout( self.h2_2_layout )
        splitter.addWidget( self.sourceRequirementTableView )
        splitter.addWidget( mid_frame )
        splitter.addWidget( self.destRequirementTableView )
        mid_frame.setFixedHeight( 30 )
        bottom_frame = QFrame()
        bottom_frame.setLayout( self.button_h_layout )

        main_layout.addWidget( top_frame )
        main_layout.addWidget( splitter )
        main_layout.addWidget( bottom_frame )

        self.searchItemComboBox.addItems( ['描述', '备注'] )
        self.searchItemComboBox.setCurrentIndex( 0 )

        self.sourceRequirementTableView.setModel( self.__source_data )
        self.sourceRequirementTableView.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.sourceRequirementTableView.setSelectionMode( QAbstractItemView.ExtendedSelection )
        self.sourceRequirementTableView.setEditTriggers( QAbstractItemView.NoEditTriggers )
        self.destRequirementTableView.setModel( self.__dest_data )
        self.destRequirementTableView.horizontalHeader().setStretchLastSection( True )
        self.destRequirementTableView.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.destRequirementTableView.setSelectionMode( QAbstractItemView.ExtendedSelection )
        source_headers = ['单号', '零件号', '描述', '中德物料编码', '数量', '已下传数', '日期', '备注']
        if self.__current_process == 4:
            source_headers.extend( ['仓位', '去税单价'] )
        self.__source_data.setHorizontalHeaderLabels( source_headers )
        self.__source_table_column_count = len( source_headers )
        dest_headers = ['零件号', '描述', '中德物料编码', '数量', '备注']
        if self.__current_process == 3 or self.__current_process == 4:
            dest_headers.extend( ['仓位', '去税单价'] )
        self.__dest_data.setHorizontalHeaderLabels( dest_headers )
        readonly_delegate = ReadOnlyDelegate()
        for i in range( 3 ):
            self.destRequirementTableView.setItemDelegateForColumn( i, readonly_delegate )

        # 一些响应函数
        self.sourceRequirementTableView.horizontalHeader().sectionClicked.connect( self.__sort_by_column )
        self.pushForwardButton.clicked.connect( lambda: self.__how_to_handle_the_source( 1 ) )
        self.rollBackButton.clicked.connect( lambda: self.__how_to_handle_the_source( 2 ) )
        self.cancelRequirementButton.clicked.connect( lambda: self.__how_to_handle_the_source( 3 ) )
        self.destRequirementTableView.selectionModel().selectionChanged.connect( self.__dest_selected_changed )
        self.removeButton.clicked.connect( lambda: self.__how_to_handle_the_dest( 1 ) )
        self.doSearchButton.clicked.connect( self.do_search )
        self.cleanSearchButton.clicked.connect( self.clean_search )
        self.filterlineEdit.returnPressed.connect( self.do_search )
        self.okButton.clicked.connect( self.do_ok )
        self.closeButton.clicked.connect( self.do_close )

        # 一些初始化的显示数据
        current_title = self.windowTitle()
        if self.__current_process == 1:
            post_fix = '投料'
        elif self.__current_process == 2:
            post_fix = '派工'
        elif self.__current_process == 3:
            post_fix = '入库'
        else:
            post_fix = '退库'
        self.setWindowTitle( f'{current_title} - {post_fix}' )

        # 根据不同的模式某些功能要加以抑制
        if self.__current_process == 1 or self.__current_process == 2:
            # 投料和派工，不能“回退”，只能“前进”或“作废”
            self.rollBackButton.setEnabled( False )
        if self.__current_process == 4:
            # 退库时，不能“回退”和“取消”
            self.rollBackButton.setEnabled( False )
            self.cancelRequirementButton.setEnabled( False )

    def do_search(self):
        """
        进行检索
        :return:
        """
        t = self.filterlineEdit.text()
        filter_text = t.strip()
        if len( filter_text ) < 1:
            return
        row_count = self.__source_data.rowCount()
        search_type = self.searchItemComboBox.currentText()
        hide_row_count = 0
        for i in range( row_count ):
            col = 2 if search_type == '描述' else 7
            item_text = self.__source_data.item( i, col ).text()
            u = filter_text.upper()
            if len( item_text ) > 0 and item_text.upper().find( u ) > 0:
                self.sourceRequirementTableView.showRow( i )
            else:
                self.sourceRequirementTableView.hideRow( i )
                hide_row_count += 1
        if hide_row_count > 0:
            self.__after_search = True

    def clean_search(self):
        """
        清除检索
        :return:
        """
        self.filterlineEdit.setText( '' )
        if not self.__after_search:
            return
        row_count = self.__source_data.rowCount()
        for i in range( row_count ):
            self.sourceRequirementTableView.showRow( i )

    def do_close(self):
        resp = QMessageBox.question( self, '', '确定要关闭？', defaultButton=QMessageBox.No )
        if resp == QMessageBox.Yes:
            self.close()

    def do_ok(self):
        when_do = QDate.currentDate().toString( 'yyMMdd' )
        try:
            # 增加已退库（15）的状态，以免再次被检测到
            next_process = 13
            bill_type = '入库单'
            operation_data = []
            if self.__current_process == 1 or self.__current_process == 2:
                if self.__current_process == 1:
                    next_process = 11
                    bill_type = '投料单'
                else:
                    next_process = 12
                    bill_type = '派工单'
                operation_data = []
                record_count = self.__dest_data.rowCount()
                for i in range( record_count ):
                    # TODO 要添加数量的验证
                    first_item_in_row: QStandardItem = self.__dest_data.item( i, 0 )
                    link_item_nr = first_item_in_row.data( Qt.UserRole + 2 )
                    qty_item: QStandardItem = self.__dest_data.item( i, 3 )
                    the_qty = qty_item.data( Qt.EditRole )
                    comment_item: QStandardItem = self.__dest_data.item( i, 4 )
                    the_comment = comment_item.text()
                    operation_data.append( [link_item_nr, the_qty, the_comment] )
            elif self.__current_process == 3:
                record_count = self.__dest_data.rowCount()
                for i in range( record_count ):
                    first_item_in_row: QStandardItem = self.__dest_data.item( i, 0 )
                    link_item_nr = first_item_in_row.data( Qt.UserRole + 2 )
                    last_process_link = first_item_in_row.data( Qt.UserRole + 3 )
                    qty_item: QStandardItem = self.__dest_data.item( i, 3 )
                    the_qty = qty_item.data( Qt.EditRole )
                    comment_item: QStandardItem = self.__dest_data.item( i, 4 )
                    the_comment = comment_item.text()
                    storage_id = self.__dest_data.item( i, 5 ).text()
                    # 入库单要有仓位，否则发出警告
                    if storage_id is None or len( storage_id ) < 1 or storage_id.isspace():
                        raise Exception( '入库的时候没有设置仓位。' )
                    the_unit_price_temp = self.__dest_data.item( i, 6 ).data( Qt.EditRole )
                    the_unit_price = None
                    if the_unit_price_temp is not None:
                        the_unit_price_str = the_unit_price_temp.strip()
                        if len( the_unit_price_str ) > 0:
                            the_unit_price = float( the_unit_price_str )
                            if the_unit_price < 0.0001:
                                the_unit_price = None
                    operation_data.append(
                        [link_item_nr, the_qty, the_comment, last_process_link, storage_id, the_unit_price] )
            elif self.__current_process == 4:
                next_process = 15  # 增加已退库的标记
                operation_data = []
                record_count = self.__dest_data.rowCount()
                # 预先修改数量
                for i in range( record_count ):
                    qty_item: QStandardItem = self.__dest_data.item( i, 3 )
                    the_qty = qty_item.data( Qt.EditRole )
                    if the_qty > 0:
                        qty_item.setData( -the_qty, Qt.EditRole )
                resp = QMessageBox.question( self, '确认', '真的确定要退库吗？', defaultButton=QMessageBox.No )
                if resp == QMessageBox.No:
                    return
                for i in range( record_count ):
                    first_item_in_row: QStandardItem = self.__dest_data.item( i, 0 )
                    link_item_nr = first_item_in_row.data( Qt.UserRole + 2 )
                    last_process_link = first_item_in_row.data( Qt.UserRole + 3 )
                    qty_item: QStandardItem = self.__dest_data.item( i, 3 )
                    storage_item: QStandardItem = self.__dest_data.item( i, 5 )
                    storage_id = storage_item.text()
                    the_unit_price_item: QStandardItem = self.__dest_data.item( i, 6 )
                    the_unit_price = the_unit_price_item.text()
                    if len( the_unit_price ) < 1:
                        the_unit_price = None
                    else:
                        the_unit_price = float( the_unit_price )
                    the_qty = qty_item.data( Qt.EditRole )
                    # 价格按之前入库的价格
                    comment_item: QStandardItem = self.__dest_data.item( i, 4 )
                    the_comment = comment_item.text()
                    operation_data.append(
                        [link_item_nr, the_qty, the_comment, last_process_link, storage_id, the_unit_price] )
            if len( operation_data ) < 1:
                QMessageBox.warning( self, '警告', '没有需要操作的数据！' )
                return
            data = {'BillName': when_do, 'Operator': self.__operator,
                    'DoingDate': QDate.currentDate().toString( 'yyyy-MM-dd' ), 'BillType': bill_type,
                    'NextProcess': next_process, 'Items': operation_data}
            neu_bill_name = self.__database.create_supply_operation( data )
            if self.__current_process == 1:
                message = f'生成了新的投料单号：{neu_bill_name}'
            elif self.__current_process == 2:
                message = f'生成了新的派工单号：{neu_bill_name}'
            elif self.__current_process == 3:
                message = f'生成了新的入库单号：{neu_bill_name}'
            else:
                message = f'生成了退库单号：{neu_bill_name}'
            QMessageBox.information( self, '完成', message, QMessageBox.Ok, QMessageBox.Ok )
            self.close()
        except Exception as ex:
            QMessageBox.critical( self, '出错', ex.__str__(), QMessageBox.Ok, QMessageBox.Ok )

    def __how_to_handle_the_dest(self, mode):
        """
        根据不同的mode，处理已推进的需求
        :param mode:
        :return:
        """
        selection_model: QItemSelectionModel = self.destRequirementTableView.selectionModel()
        indexes = selection_model.selectedIndexes()

        # 删除已选定的物料
        c = int( len( indexes ) / 5 )
        for i in range( c ):
            first_index: QModelIndex = indexes[i * 5]
            self.__dest_data.removeRow( first_index.row() )

    def __how_to_handle_the_source(self, mode):
        """
        根据不同的mode，处理已经选定的需求
        :param mode: 1=处理, 2=回退, 3=作废
        :return:
        """
        selection_model: QItemSelectionModel = self.sourceRequirementTableView.selectionModel()
        indexes = selection_model.selectedIndexes()

        if mode == 1:
            if self.__default_storage is None and self.__current_process == 3:
                # 输入默认的仓位
                text, ok = QInputDialog.getText( self, '输入', '默认仓位：' )
                if ok:
                    self.__default_storage = text

            cc = int( len( indexes ) / self.__source_table_column_count )
            for i in range( cc ):
                # 获取原来的数据
                first_item: QStandardItem = self.__source_data.itemFromIndex(
                    indexes[i * self.__source_table_column_count] )
                row_index = first_item.data( Qt.UserRole + 1 )
                require_item = first_item.data( Qt.UserRole + 2 )
                process_id = first_item.data( Qt.UserRole + 3 )
                the_row = self.__row_map[row_index]
                part_id = the_row[1].text()
                description = the_row[2].text()
                zd_erp = the_row[3].text()
                qty = the_row[4].data( Qt.DisplayRole )
                done_qty = the_row[5].data( Qt.DisplayRole )
                default_qty = qty - done_qty
                # TODO 检验不要重复添加
                # 生成未来的数据
                first_dest_item = QStandardItem( part_id )
                first_dest_item.setData( row_index, Qt.UserRole + 1 )
                first_dest_item.setData( require_item, Qt.UserRole + 2 )
                if self.__current_process == 3 or self.__current_process == 4:
                    first_dest_item.setData( process_id, Qt.UserRole + 3 )
                new_dest_row = [first_dest_item, QStandardItem( description ), QStandardItem( zd_erp )]
                qty_item = QStandardItem()
                qty_item.setData( default_qty, Qt.DisplayRole )
                qty_item.setTextAlignment( Qt.AlignCenter )
                new_dest_row.extend( [qty_item, QStandardItem()] )
                if self.__current_process == 3:
                    # 入库时候的一些特殊工作
                    storage_item = QStandardItem()
                    storage_item.setTextAlignment( Qt.AlignCenter )
                    if self.__default_storage is not None:
                        storage_item.setText( self.__default_storage )
                    unit_price_item = QStandardItem()
                    unit_price_item.setTextAlignment( Qt.AlignCenter )
                    new_dest_row.extend( [storage_item, unit_price_item] )
                elif self.__current_process == 4:
                    storage_item = QStandardItem( the_row[8] )
                    storage_item.setTextAlignment( Qt.AlignCenter )
                    unit_price_item = QStandardItem( the_row[9] )
                    unit_price_item.setTextAlignment( Qt.AlignCenter )
                    new_dest_row.extend( [storage_item, unit_price_item] )
                self.__dest_data.appendRow( new_dest_row )
        elif mode == 2 or mode == 3:
            a_word = '回退' if mode == 2 else '作废'
            rsp = QMessageBox.question( self, '', f'确定要进行{a_word}处理？', QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No )
            if rsp == QMessageBox.No:
                return

            cc = int( len( indexes ) / 8 )
            for i in range( cc ):
                first_item: QStandardItem = self.__source_data.itemFromIndex( indexes[i * 8] )
                row_index = first_item.data( Qt.UserRole + 1 )
                require_item = first_item.data( Qt.UserRole + 2 )
                the_row = self.__row_map[row_index]
                qty = the_row[4].data( Qt.DisplayRole )
                done_qty = the_row[5].data( Qt.DisplayRole )
                default_qty = qty - done_qty
                if mode == 2:
                    # TODO 进行“回退”处理
                    QMessageBox.warning( self, '', '回退的功能还未完成。敬请期待。' )
                    return
                else:
                    if self.__current_process == 1 or self.__current_process == 2:
                        self.__database.cancel_material_requirement( require_item, default_qty )
                    elif self.__current_process == 3:
                        item_process_id = first_item.data( Qt.UserRole + 3 )
                        self.__database.cancel_supply_operation( item_process_id, default_qty )
            # 删除原来的记录
            for i in range( cc ):
                first_index: QModelIndex = indexes[i * 8]
                self.__source_data.removeRow( first_index.row() )

    def __dest_selected_changed(self, item_1, item_2):
        """
        目标的项目选择更换时的响应函数
        :return:
        """
        select_mode: QItemSelectionModel = self.destRequirementTableView.selectionModel()
        the_first_index = select_mode.selectedIndexes()
        if len( the_first_index ) < 1:
            return
        first_item = self.__dest_data.itemFromIndex( the_first_index[0] )
        i = first_item.data( Qt.UserRole + 1 )
        original_row = self.__row_map[i]
        original_index = self.__source_data.indexFromItem( original_row[0] )
        original_selection: QItemSelectionModel = self.sourceRequirementTableView.selectionModel()
        original_selection.clearSelection()
        original_selection.select( original_index, QItemSelectionModel.Select | QItemSelectionModel.Rows )

    def __sort_by_column(self, column_index):
        """
        点击表头时，对表内容进行排列
        :param column_index:
        :return:
        """
        sort_flags = False
        if column_index in self.__sort_flags:
            sort_flags = self.__sort_flags[column_index]
        if sort_flags:
            self.sourceRequirementTableView.sortByColumn( column_index, Qt.AscendingOrder )
            sort_flags = False
        else:
            self.sourceRequirementTableView.sortByColumn( column_index, Qt.DescendingOrder )
            sort_flags = True
        self.__sort_flags[column_index] = sort_flags

    def init_data(self):
        """
        初始化数据
        :return:
        """
        i = 0
        for d in self.__data_s[1]:
            part_id = d[2]
            parts = Part.get_parts( self.__database, part_id=part_id )
            if parts is not None and len( parts ) > 0:
                the_part = parts[0]
                part_id = the_part.part_id
                description = the_part.name
                if the_part.description is not None:
                    description += ' {0}'.format( the_part.description )
            elif d[3] is not None:
                temp_description = self.__database.get_erp_info( d[3] )
                if temp_description is None:
                    description = "（无数据）"
                else:
                    description = self.__database.get_erp_info( d[3] )[1]
            else:
                QMessageBox.warning( self, '', '其中数据有误', QMessageBox.Ok, QMessageBox.Ok )
                continue
            first_item = QStandardItem( d[0] )
            # 给每行的首个单元，打上记号
            first_item.setData( i, Qt.UserRole + 1 )
            first_item.setData( d[1], Qt.UserRole + 2 )
            # 承接之前的 Supply Operation 的 Id
            if self.__current_process == 3 or self.__current_process == 4:
                first_item.setData( d[9], Qt.UserRole + 3 )
            one_row = [first_item]
            one_row.extend( [QStandardItem( part_id ), QStandardItem( description ), QStandardItem( d[3] )] )
            qty_item = QStandardItem( d[5] )
            # 直接 QStandardItem.setData( Decimal, Qt.DisplayRole ) 无法显示？
            qty_item.setData( float( d[5] ), Qt.DisplayRole )
            qty_item.setTextAlignment( Qt.AlignCenter )
            one_row.append( qty_item )
            u_doing_qty = d[6] + d[7]
            u_qty_item = QStandardItem( u_doing_qty )
            u_qty_item.setData( float( u_doing_qty ), Qt.DisplayRole )
            u_qty_item.setTextAlignment( Qt.AlignCenter )
            one_row.append( u_qty_item )
            date_str = d[4][:10] if type( d[4] ) == str else d[4].strftime( '%Y-%m-%d' )
            one_row.append( QStandardItem( date_str ) )
            one_row.append( QStandardItem( d[8] ) )
            if self.__current_process == 4:
                p_item = QStandardItem( d[10] )
                p_item.setTextAlignment( Qt.AlignCenter )
                one_row.append( p_item )
                u_item = QStandardItem( d[11] )
                u_item.setTextAlignment( Qt.AlignCenter )
                one_row.append( u_item )
            self.__row_map[i] = one_row
            self.__source_data.appendRow( one_row )
            i += 1
        self.sourceRequirementTableView.resizeColumnsToContents()
        self.sourceRequirementTableView.horizontalHeader().setStretchLastSection( True )
        self.sourceRequirementTableView.horizontalHeader().setSectionsClickable( True )
        self.sourceRequirementTableView.horizontalHeader().setSortIndicatorShown( True )


class ReadOnlyDelegate( QItemDelegate ):

    def createEditor(self, parent, option, index):
        return None

    def __init__(self, parent=None):
        super().__init__( parent )
