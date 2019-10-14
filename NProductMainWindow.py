# coding=gbk
import sys

from PyQt5.Qt import Qt
from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QSplitter,
                             QFrame, QPushButton, QVBoxLayout, QLabel, QTableView,
                             QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem, QMenu,
                             QInputDialog, QAbstractItemView)

from Part import Tag, Product
from UiFrame import TagViewPanel
from ui.NProductInfoDialog import *
from ui.ProductMainWindow import *


class NProductMainWindow( QMainWindow, Ui_MainWindow ):

    def __init__(self, parent=None, database=None):
        super( NProductMainWindow, self ).__init__( parent )
        self.__database = database
        self.__productTab = ProductTab( self, database=database )
        self.setup_ui()
        self.__init_data()

    def setup_ui(self):
        super( NProductMainWindow, self ).setupUi( self )

        product_tab_layout = QHBoxLayout( self.productTab )
        product_tab_layout.addWidget( self.__productTab )
        self.productTab.setLayout( product_tab_layout )
        self.setCentralWidget( self.tabWidget )

        self.tabWidget.setCurrentIndex( 0 )
        self.exitAction.triggered.connect( self.__close )
        self.addProductAction.triggered.connect( self.__add_product )

    def __init_data(self):
        self.__productTab.init_data()

    def __close(self):
        self.close()

    def __add_product(self):
        dialog = NProductInfoDialog( self, database=self.__database )
        dialog.exec_()

    def closeEvent(self, event):
        if self.__database is not None:
            self.__database.close()
        event.accept()


class TagViewInProductTab( TagViewPanel ):

    def __init__(self, parent=None, database=None):
        super( TagViewInProductTab, self ).__init__( parent=parent, database=database )
        self.__my_database = database

    def search_by_tag(self):
        if self.tagFilterListWidget.count() < 1:
            return
        result = set()
        for i in range( 0, self.tagFilterListWidget.count() ):
            item = self.tagFilterListWidget.item( i )
            t: Tag = item.data( Qt.UserRole )
            ps = Product.get_products_from_tag( self.__my_database, t.tag_id )
            ps_s = set( ps )
            if len( result ) < 1:
                result = ps_s
            else:
                result = result.intersection( ps_s )
            if len( ps_s ) < 1:
                return
        r_list = list( result )
        self.parent.show_products_from_outside( r_list )


class ProductTab( QFrame ):

    def __init__(self, parent=None, database=None):
        super( QFrame, self ).__init__( parent )
        self.__tagPanel = TagViewInProductTab( parent=self, database=database )
        self.__database = database
        self.__topRightPanel = QFrame( self )
        self.productIdLineEdit = QLineEdit( self )
        self.commentComboBox = QComboBox( self )
        self.commentLineEdit = QLineEdit( self )
        self.cleanPushButton = QPushButton( self )
        self.productView = QTreeWidget( self )
        self.current_product = None
        self.current_product_item = None
        self.__current_product_info_row = -1
        # 用于计算产品清单用
        self.temp_list = {}

        self.__bottomPanel = QFrame( self )
        self.productInfoTable = QTableView( self )
        self.tagInfoList = QListWidget( self )
        self.statusInfoTable = QTableView( self )
        self.afterSaleInfoTable = QTableView( self )
        self.productInfoModel = QStandardItemModel()

        # 右键菜单
        self.__menu_4_product_list = QMenu( parent=self.productView )
        self.__modify_product_info = self.__menu_4_product_list.addAction( '修改' )
        self.__copy_product_info = self.__menu_4_product_list.addAction( '复制' )
        self.__replace_product = self.__menu_4_product_list.addAction( '代替' )
        self.__delete_product = self.__menu_4_product_list.addAction( '删除' )

        self.__menu_4_product_info = QMenu( parent=self.productInfoTable )
        self.__modify_product_one_info = self.__menu_4_product_info.addAction( '修改' )

        self.__initUI()

    def __initUI(self):
        h_box = QHBoxLayout()
        splitter1 = QSplitter( Qt.Vertical )
        splitter2 = QSplitter( Qt.Horizontal )
        splitter1.setStretchFactor( 0, 1 )
        splitter1.setStretchFactor( 1, 8 )
        splitter2.setStretchFactor( 0, 2 )
        splitter2.setStretchFactor( 1, 1 )

        splitter2.addWidget( self.__tagPanel )

        top_right_layout = QVBoxLayout()
        top_right_layout_top = QHBoxLayout()
        top_right_layout_top.addWidget( QLabel( '产品编号' ) )
        top_right_layout_top.addWidget( self.productIdLineEdit )
        self.commentComboBox.addItems( ['产品备注', '状态备注', '配置'] )
        top_right_layout_top.addWidget( self.commentComboBox )
        top_right_layout_top.addWidget( self.commentLineEdit )
        self.cleanPushButton.setText( '清空' )
        top_right_layout_top.addWidget( self.cleanPushButton )
        top_right_layout.addLayout( top_right_layout_top )
        top_right_layout.addWidget( self.productView )
        self.__topRightPanel.setLayout( top_right_layout )
        splitter2.addWidget( self.__topRightPanel )
        splitter1.addWidget( splitter2 )

        bottom_layout = QHBoxLayout()
        bottom_layout_1 = QVBoxLayout()
        bottom_layout_1.addWidget( QLabel( '基本信息' ) )
        bottom_layout_1.addWidget( self.productInfoTable )
        bottom_layout.addLayout( bottom_layout_1 )
        bottom_layout_2 = QVBoxLayout()
        bottom_layout_2.addWidget( QLabel( '标签' ) )
        bottom_layout_2.addWidget( self.tagInfoList )
        bottom_layout.addLayout( bottom_layout_2 )
        bottom_layout_3 = QVBoxLayout()
        bottom_layout_3.addWidget( QLabel( '状态变化记录' ) )
        bottom_layout_3.addWidget( self.statusInfoTable )
        bottom_layout.addLayout( bottom_layout_3 )
        bottom_layout_4 = QVBoxLayout()
        bottom_layout_4.addWidget( QLabel( '售后记录' ) )
        bottom_layout_4.addWidget( self.afterSaleInfoTable )
        bottom_layout.addLayout( bottom_layout_4 )
        self.__bottomPanel.setLayout( bottom_layout )
        splitter1.addWidget( self.__bottomPanel )
        self.productView.setStyleSheet(
            '''
            QTreeWidget::item
            {
                border-right: 1px solid red;
                border-bottom: 1px solid red;
                padding: 2px;
                margin: 0px;
                margin-left: -2px;
            }
            QTreeWidget::item:hover
            {
                background-color: rgb(0,255,0);
            }
            QTreeWidget::item:selected
            {
                background-color: rgb(192,192,192);
            }
            ''' )
        self.productInfoModel.setHorizontalHeaderLabels( ('项目', '数值') )
        self.productInfoTable.setModel( self.productInfoModel )
        self.productInfoTable.verticalHeader().hide()
        self.productInfoTable.setEditTriggers( QAbstractItemView.NoEditTriggers )
        self.productInfoTable.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.productInfoTable.setSelectionMode( QAbstractItemView.SingleSelection )
        h_box.addWidget( splitter1 )
        self.setLayout( h_box )

        # signal handler
        self.cleanPushButton.clicked.connect( self.__clean_input )
        self.productIdLineEdit.returnPressed.connect( self.__do_search )
        self.commentLineEdit.returnPressed.connect( self.__do_search )
        self.productView.itemSelectionChanged.connect( self.__product_selected )
        self.productView.itemExpanded.connect( self.__when_product_view_expanded )

        # 设置右键菜单
        self.productView.setContextMenuPolicy( Qt.CustomContextMenu )
        self.productView.customContextMenuRequested.connect( self.__on_custom_context_menu_requested )
        self.__modify_product_info.triggered.connect( self.__custom_context_handler )
        self.__copy_product_info.triggered.connect( self.__custom_context_handler )
        self.__replace_product.triggered.connect( self.__custom_context_handler )
        self.__delete_product.triggered.connect( self.__custom_context_handler )

        self.productInfoTable.setContextMenuPolicy( Qt.CustomContextMenu )
        self.productInfoTable.customContextMenuRequested.connect( self.__on_custom_context_menu_requested_2 )
        self.__modify_product_one_info.triggered.connect( self.__modify_product_one_info_handler )

    def __on_custom_context_menu_requested_2(self, pos):
        item_index = self.productInfoTable.indexAt( pos )
        r_index = item_index.row()
        self.__current_product_info_row = r_index
        if r_index < 0:
            return
        self.__menu_4_product_info.exec( QCursor.pos() )

    def __modify_product_one_info_handler(self):
        r_index = self.__current_product_info_row
        r_m_index_1 = self.productInfoModel.index( r_index, 0 )
        r_m_index_2 = self.productInfoModel.index( r_index, 1 )
        r_item_1: QStandardItem = self.productInfoModel.itemFromIndex( r_m_index_1 )
        r_item_2: QStandardItem = self.productInfoModel.itemFromIndex( r_m_index_2 )
        the_key = r_item_1.data( Qt.DisplayRole )
        the_value = r_item_2.data( Qt.DisplayRole )
        text, ok_pressed = QInputDialog.getText( self, '新数值', the_key, QLineEdit.Normal, the_value )
        i_s = the_key.split( '.' )[0]
        if ok_pressed:
            try:
                self.__database.update_product_other_info( self.current_product.product_id, int( i_s ), text )
            except Exception as ex:
                QMessageBox.warning(self, '', ex.__str__())

    def __on_custom_context_menu_requested(self, pos):
        item: QTreeWidgetItem = self.productView.itemAt( pos )
        if item is not None:
            self.current_product_item = item
            self.current_product = item.data( 0, Qt.UserRole )
            self.__menu_4_product_list.exec( QCursor.pos() )

    def __custom_context_handler(self):
        try:
            if self.sender() is self.__modify_product_info or self.sender() is self.__copy_product_info:
                p_id = self.current_product.product_id
                if self.sender() is self.__modify_product_info:
                    m = 2
                else:
                    m = 3
                dialog = NProductInfoDialog( parent=self, database=self.__database, product_id=p_id, mode=m )
                dialog.exec_()
            elif self.sender() is self.__replace_product:
                text, ok_pressed = QInputDialog.getText( self, '要来代替的产品', '产品编号：', QLineEdit.Normal,
                                                         self.current_product.product_id )
                if ok_pressed and text != '':
                    self.__database.replace_product( self.current_product.product_id, text.strip() )
                    QMessageBox.information( self, '', '代替成功！' )
                    rsp = QMessageBox.question( self, '', '被代替的产品是否要删除？', QMessageBox.No | QMessageBox.Yes,
                                                QMessageBox.No )
                    if rsp == QMessageBox.Yes:
                        self.__database.delete_product( self.current_product.product_id )
            elif self.sender() is self.__delete_product:
                rsp = QMessageBox.question( self, '确定', '确定要删除该产品的记录？',
                                            QMessageBox.No | QMessageBox.Yes, QMessageBox.No )
                if rsp == QMessageBox.Yes:
                    self.__database.delete_product( self.current_product.product_id )
                    if self.current_product_item.parent() is None:
                        ii = self.productView.indexOfTopLevelItem( self.current_product_item )
                        self.productView.takeTopLevelItem( ii )
                    else:
                        pp: QTreeWidgetItem = self.current_product_item.parent()
                        pp.removeChild( self.current_product_item )
                    self.current_product_item = None
                    QMessageBox.information( self, '', '删除完毕。' )
        except Exception as ex:
            QMessageBox.warning( self, '异常', ex.__str__() )

    def __clean_input(self):
        self.productIdLineEdit.setText( '' )
        self.commentLineEdit.setText( '' )
        products = Product.get_products( self.__database, top=True )
        self.fill_products_table( products )

    def __when_product_view_expanded(self):
        self.productView.resizeColumnToContents( 0 )

    def __do_search(self):
        if self.sender() is self.productIdLineEdit:
            products = Product.get_products( self.__database, product_id=self.productIdLineEdit.text() )
            self.fill_products_table( products, search_parent=True )
        elif self.sender() is self.commentLineEdit:
            filter_text = self.commentLineEdit.text()
            if self.commentComboBox.currentIndex() == 0:
                products = Product.get_products( self.__database, product_comment=filter_text )
            elif self.commentComboBox.currentIndex() == 1:
                products = Product.get_products( self.__database, status_comment=filter_text )
            elif self.commentComboBox.currentIndex() == 2:
                products = Product.get_products( self.__database, config=filter_text )
            self.fill_products_table( products, search_parent=True )

    def show_products_from_outside(self, products):
        self.fill_products_table( products, search_parent=True )
        self.productView.expandAll()

    def __product_selected(self):
        one_product: QTreeWidgetItem = self.productView.currentItem()
        product_obj: Product = one_product.data( 0, Qt.UserRole )
        self.current_product = product_obj
        # 设置标签
        self.tagInfoList.clear()
        product_obj.get_tags( self.__database )
        for t in product_obj.tags:
            one_item = QListWidgetItem( t.get_whole_name(), parent=self.tagInfoList )
            one_item.setData( Qt.UserRole, t )
            self.tagInfoList.addItem( one_item )
        # 显示其它信息
        self.productInfoModel.clear()
        self.productInfoModel.setHorizontalHeaderLabels( ('项目', '数值') )
        self.productInfoTable.horizontalHeader().setStretchLastSection( True )
        info_s = self.__database.get_other_product_info( product_id=product_obj.product_id )
        the_keys = list( info_s.keys() ).copy()
        the_keys.sort()
        for k in the_keys:
            one_row = [QStandardItem( k ), QStandardItem( info_s[k] )]
            self.productInfoModel.appendRow( one_row )
        if self.productInfoModel.rowCount() > 0:
            self.productInfoTable.resizeColumnsToContents()

    def do_when_tag_tree_select(self, tag_id):
        products = Product.get_products_from_tag( self.__database, tag_id )
        self.fill_products_table( products, search_parent=True )
        self.productView.expandAll()

    def init_data(self):
        tags = Tag.get_tags( self.__database )
        self.__tagPanel.fill_data( tags )
        products = Product.get_products( self.__database, top=True )
        self.fill_products_table( products )

    """
    search_parent: 是否要往上追溯
    """

    def fill_products_table(self, products, columns_setting=None, search_parent=False):
        self.productView.clear()
        self.temp_list.clear()
        if columns_setting is None:
            self.productView.setColumnCount( 4 )
            self.productView.setHeaderLabels( ['编号', '产品备注', '状态备注', '配置'] )
            for pp in products:
                if pp.product_id in self.temp_list.keys():
                    continue
                one_pp_data = [pp.product_id, pp.product_comment, pp.status_comment, pp.config]
                one_row = QTreeWidgetItem()
                i = 0
                for pp_d in one_pp_data:
                    if pp_d is not None:
                        one_row.setText( i, pp_d )
                    i += 1
                one_row.setData( 0, Qt.UserRole, pp )
                self.productView.addTopLevelItem( one_row )
                self.temp_list[pp.product_id] = one_row
                self.__add_product_children( pp, one_row, columns_setting )
                if search_parent:
                    self.__add_product_parent( pp, one_row, columns_setting )
        self.__resize_header()

    def __resize_header(self):
        view_cc = self.productView.columnCount()
        for i in range( view_cc ):
            self.productView.resizeColumnToContents( i )

    def __add_product_parent(self, product: Product, one_row: QTreeWidgetItem, column_setting=None):
        the_parent = product.get_children( self.__database, mode=1 )
        if the_parent is None:
            return
        pp = the_parent[0]
        index = self.productView.indexOfTopLevelItem( one_row )
        self.productView.takeTopLevelItem( index )
        if pp.product_id in self.temp_list.keys():
            to_node = self.temp_list[pp.product_id]
            to_node.addChild( one_row )
            return
        previous_one_row = QTreeWidgetItem()
        data_s = [pp.product_id, pp.product_comment, pp.status_comment, pp.config]
        i = 0
        for d in data_s:
            if d is not None:
                previous_one_row.setText( i, d )
            i += 1
        previous_one_row.setData( 0, Qt.UserRole, pp )
        self.productView.addTopLevelItem( previous_one_row )
        previous_one_row.addChild( one_row )
        previous_one_row.setExpanded( True )
        self.temp_list[pp.product_id] = previous_one_row
        self.__add_product_parent( pp, previous_one_row, column_setting )

    def __add_product_children(self, product: Product, one_row: QTreeWidgetItem, column_setting=None):
        if len( product.children ) < 1:
            return
        if column_setting is None:
            for cc in product.children:
                one_cc_data = [cc.product_id, cc.product_comment, cc.status_comment, cc.config]
                next_one_row = QTreeWidgetItem()
                i = 0
                for cc_d in one_cc_data:
                    if cc_d is not None:
                        next_one_row.setText( i, cc_d )
                    i += 1
                next_one_row.setData( 0, Qt.UserRole, cc )
                one_row.addChild( next_one_row )
                self.temp_list[cc.product_id] = next_one_row
                self.__add_product_children( cc, next_one_row, column_setting )


if __name__ == '__main__':
    app = QApplication( sys.argv )
    database = SqliteHandler( r'db/produce_datas.db' )
    theDialog = NProductMainWindow( parent=None, database=database )
    theDialog.show()
    sys.exit( app.exec_() )
