# coding=gbk

from PyQt5.Qt import Qt
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QSplitter,
                             QFrame, QPushButton, QVBoxLayout, QLabel, QTableView,
                             QTreeWidget, QTreeWidgetItem, QListWidget, QMenu,
                             QInputDialog, QAbstractItemView, QTabWidget)

from Part import Tag
from Product import Product
from UiFrame import TagViewPanel
from ui.NListDisplayDialog import *
from ui2.NCreateNewPropertyDialog import *
from ui2.NProductInfoDialog import *
from ui2.NProductSoldDialog import *
from ui2.ProductMainWindow import *
from ui2.ProductServiceRecordDialog import Ui_Dialog as ServiceRecordDialog


class NProductMainWindow( QMainWindow, Ui_MainWindow ):

    def __init__(self, parent=None, database=None, offline=0):
        super( NProductMainWindow, self ).__init__( parent )
        self.__database = database
        self.__is_online = False if offline else True
        self.__productTab = ProductPanel( self, database=database )
        self.__contract_dialog = None  # 处理销售合同的对话框
        self.setup_ui()
        self.__init_data()

    def setup_ui(self):
        super( NProductMainWindow, self ).setupUi( self )

        self.setCentralWidget( self.__productTab )

        self.exitAction.triggered.connect( self.__close )
        self.addProductAction.triggered.connect( self.__add_product )
        self.addServiceRecordAction.triggered.connect( self.__add_service_record )
        self.addCustomerAction.triggered.connect( lambda: self.__handle_customer( mode=1 ) )
        self.editCustomerAction.triggered.connect( lambda: self.__handle_customer( mode=2 ) )
        self.addSaleContractAction.triggered.connect( lambda: self.__handle_sale_contract( mode=1 ) )
        self.editSaleContractAction.triggered.connect( lambda: self.__handle_sale_contract( mode=2 ) )
        self.getAvailableSerNrAction.triggered.connect( self.__get_available_ser_nr )
        self.addSaleContractAction.triggered.connect( lambda: self.__handle_sale_contract( mode=1 ) )
        self.editSaleContractAction.triggered.connect( lambda: self.__handle_sale_contract( mode=2 ) )

        self.actionAdd2Contract.triggered.connect( self.__add_product_2_contract )

        if not self.__is_online:
            self.__change_platte()

    def __init_data(self):
        self.__productTab.init_data()

    def __close(self):
        self.close()

    def __handle_customer(self, mode=1):
        """
        新建或编辑客户的对话框
        :param mode: 对话框类型，1=新建，2=编辑
        :return:
        """
        pass

    def __add_product_2_contract(self):
        """
        添加产品列表的产品到合同对话框中
        :return:
        """
        selected_product: Product = self.__productTab.current_product
        if selected_product is None:
            return
        if self.__contract_dialog is not None and self.__contract_dialog.isVisible:
            self.__contract_dialog.add_2_product_list( selected_product.product_id )

    def __get_available_ser_nr(self):
        """
        用于获取下一个可用的出厂编号的小工具
        :return:
        """
        all_ser_nr = self.__database.get_available_ser_nr()
        dialog = NListDisplayDialog( parent=self, data=all_ser_nr )
        dialog.show()

    def __handle_sale_contract(self, mode=1):
        """
        新建或编辑销售合同的对话框
        :param mode: 对话框类型，1=新建，2=编辑
        :return:
        """
        if self.__contract_dialog is not None and self.__contract_dialog.isVisible():
            return
        if mode == 1:
            self.__contract_dialog = NProductSoldDialog( parent=self, database=self.__database )
            self.__contract_dialog.setWindowTitle( '新建销售合同' )
            self.__contract_dialog.show()
            self.show_add_product_action( True )
        elif mode == 2:
            # TODO: 选择现有的销售合同
            pass

    def show_add_product_action(self, is_shown):
        self.actionAdd2Contract.setVisible( is_shown )

    def __add_product(self):
        dialog = NProductInfoDialog( self, database=self.__database )
        dialog.exec_()

    def __add_service_record(self):
        dialog = NProductServiceRecordDialog( self, database=self.__database )
        dialog.exec_()

    def closeEvent(self, event):
        if self.__database is not None:
            self.__database.close()
        event.accept()

    def __change_platte(self):
        """
        改变离线时，窗口的主题
        :return:
        """
        palette = QtGui.QPalette()
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 170, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Button, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 213, 127 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Light, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 191, 63 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush )
        brush = QtGui.QBrush( QtGui.QColor( 127, 85, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Dark, brush )
        brush = QtGui.QBrush( QtGui.QColor( 170, 113, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Mid, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Text, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 255, 255 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 255, 255 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Base, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 170, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Window, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 212, 127 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 255, 220 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0, 128 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 170, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 213, 127 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 191, 63 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush )
        brush = QtGui.QBrush( QtGui.QColor( 127, 85, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush )
        brush = QtGui.QBrush( QtGui.QColor( 170, 113, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 255, 255 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 255, 255 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 170, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 212, 127 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 255, 220 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0, 128 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 127, 85, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 170, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 213, 127 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 191, 63 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush )
        brush = QtGui.QBrush( QtGui.QColor( 127, 85, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush )
        brush = QtGui.QBrush( QtGui.QColor( 170, 113, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush )
        brush = QtGui.QBrush( QtGui.QColor( 127, 85, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 255, 255 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 127, 85, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 170, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 170, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 170, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush )
        brush = QtGui.QBrush( QtGui.QColor( 255, 255, 220 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush )
        brush = QtGui.QBrush( QtGui.QColor( 0, 0, 0, 128 ) )
        brush.setStyle( QtCore.Qt.SolidPattern )
        palette.setBrush( QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush )
        self.setPalette( palette )


class NProductServiceRecordDialog( QDialog, ServiceRecordDialog ):

    def __init__(self, parent=None, database=None, product_id=None):
        self.__parent = parent
        self.__database = database
        self.__product_id = product_id
        super( NProductServiceRecordDialog, self ).__init__( parent )
        self.recordIdEdit = QLineEdit( self )
        self.productIdCombo = QComboBox( self )
        self.dateEdit = QDateEdit( self )
        self.operatorCombo = QComboBox( self )
        self.descriptionEdit = QLineEdit( self )
        self.__persons = {}
        self.setup_ui()

    def setup_ui(self):
        super( NProductServiceRecordDialog, self ).setupUi( self )
        self.setWindowModality( Qt.ApplicationModal )
        self.dateEdit.setCalendarPopup( True )
        self.h_layout.setContentsMargins( 5, 5, 5, 5 )

        self.f_layout.addRow( '服务单号', self.recordIdEdit )
        self.f_layout.addRow( '产品编号', self.productIdCombo )
        self.f_layout.addRow( '日期', self.dateEdit )
        self.f_layout.addRow( '主要人员', self.operatorCombo )
        self.f_layout.addRow( '服务描述', self.descriptionEdit )

        self.setLayout( self.h_layout )

        # 初始化数据
        self.dateEdit.setDate( QDate.currentDate() )
        self.dateEdit.dateChanged.connect( self.__on_date_changed )
        temp = self.__database.get_products()
        for t in temp:
            self.productIdCombo.addItem( t[0] )
        if self.__product_id is not None:
            self.productIdCombo.setEnabled( False )
            self.productIdCombo.setCurrentText( self.__product_id )
        temp = self.__database.get_usable_operators()
        for t in temp:
            self.__persons[t[0]] = t[1]
        self.operatorCombo.addItems( self.__persons.keys() )
        self.operatorCombo.setCurrentIndex( -1 )
        self.productIdCombo.setCurrentIndex( -1 )

    def __on_date_changed(self, the_date: QDate):
        format_date = the_date.toString( 'yyMMdd' )
        record_id = self.__database.pre_get_service_record_id( format_date )
        self.recordIdEdit.setText( record_id )

    def accept(self):
        is_reject = False
        record_id = self.recordIdEdit.text()
        description = self.descriptionEdit.text()
        if record_id is None or len( record_id ) < 1 or record_id.isspace():
            QMessageBox.warning( self, '数据不完整', '没有服务单号！' )
            is_reject = True
        elif self.productIdCombo.currentIndex() < 0:
            QMessageBox.warning( self, '数据不完整', '没有选择产品！' )
            is_reject = True
        elif self.operatorCombo.currentIndex() < 0:
            QMessageBox.warning( self, '数据不完整', '没有选择售后人员！' )
            is_reject = True
        elif description is None or len( description ) < 1 or description.isspace():
            QMessageBox.warning( self, '数据不完整', '必须填写服务内容！' )
            is_reject = True
        if is_reject:
            self.reject()
            return
        self.__database.insert_service_record( record_id, self.productIdCombo.currentText(), self.dateEdit.text(),
                                               self.__persons[self.operatorCombo.currentText()], description )
        QMessageBox.information( self, '', '创建服务记录成功！' )
        self.close()


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


class ProductPanel( QFrame ):

    def __init__(self, parent=None, database=None):
        super( QFrame, self ).__init__( parent )
        self.__leftTopTabLayout = QTabWidget( parent )
        self.__tagPanel = TagViewInProductTab( parent=self, database=database )
        self.__customerPanel = CustomerView( parent=self, database=database )
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
        self.serviceRecordModel = QStandardItemModel()

        # 右键菜单
        self.__menu_4_product_list = QMenu( parent=self.productView )
        self.__modify_product_info = self.__menu_4_product_list.addAction( '修改' )
        self.__copy_product_info = self.__menu_4_product_list.addAction( '复制' )
        self.__replace_product = self.__menu_4_product_list.addAction( '代替' )
        self.__delete_product = self.__menu_4_product_list.addAction( '删除' )

        self.__menu_4_product_info = QMenu( parent=self.productInfoTable )
        self.__modify_product_one_info = self.__menu_4_product_info.addAction( '修改' )
        self.__insert_product_one_info = self.__menu_4_product_info.addAction( '增加' )
        self.__delete_product_one_info = self.__menu_4_product_info.addAction( '删除' )

        self.__initUI()

    def __initUI(self):
        h_box = QHBoxLayout()
        splitter1 = QSplitter( Qt.Vertical )
        splitter2 = QSplitter( Qt.Horizontal )
        splitter1.setStretchFactor( 0, 1 )
        splitter1.setStretchFactor( 1, 8 )
        splitter2.setStretchFactor( 0, 2 )
        splitter2.setStretchFactor( 1, 1 )

        splitter2.addWidget( self.__leftTopTabLayout )
        self.__leftTopTabLayout.addTab( self.__tagPanel, '标签' )
        self.__leftTopTabLayout.addTab( self.__customerPanel, '客户' )

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

        splitter3_1 = QSplitter( Qt.Horizontal, splitter1 )

        b_1 = QFrame( splitter3_1 )
        bottom_layout_1 = QVBoxLayout()
        bottom_layout_1.addWidget( QLabel( '基本信息' ) )
        bottom_layout_1.addWidget( self.productInfoTable )
        b_1.setLayout( bottom_layout_1 )

        b_2 = QFrame( splitter3_1 )
        bottom_layout_2 = QVBoxLayout()
        bottom_layout_2.addWidget( QLabel( '标签' ) )
        bottom_layout_2.addWidget( self.tagInfoList )
        b_2.setLayout( bottom_layout_2 )

        b_3 = QFrame( splitter3_1 )
        bottom_layout_3 = QVBoxLayout()
        bottom_layout_3.addWidget( QLabel( '状态变化记录' ) )
        bottom_layout_3.addWidget( self.statusInfoTable )
        b_3.setLayout( bottom_layout_3 )

        b_4 = QFrame( splitter3_1 )
        bottom_layout_4 = QVBoxLayout()
        bottom_layout_4.addWidget( QLabel( '售后记录' ) )
        bottom_layout_4.addWidget( self.afterSaleInfoTable )
        b_4.setLayout( bottom_layout_4 )

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

        self.serviceRecordModel.setHorizontalHeaderLabels( ('编号', '描述') )
        self.afterSaleInfoTable.setModel( self.serviceRecordModel )
        self.afterSaleInfoTable.verticalHeader().hide()
        self.afterSaleInfoTable.setEditTriggers( QAbstractItemView.NoEditTriggers )
        self.afterSaleInfoTable.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.afterSaleInfoTable.setSelectionMode( QAbstractItemView.SingleSelection )

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
        self.__insert_product_one_info.triggered.connect( self.__insert_product_one_info_handle )
        self.__delete_product_one_info.triggered.connect( self.__delete_product_one_info_handle )

    def __on_custom_context_menu_requested_2(self, pos):
        item_index = self.productInfoTable.indexAt( pos )
        r_index = item_index.row()
        self.__current_product_info_row = r_index
        self.__modify_product_one_info.setVisible( r_index >= 0 )
        self.__delete_product_one_info.setVisible( r_index >= 0 )
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
        if ok_pressed:
            try:
                self.__database.update_product_other_info( self.current_product.product_id, the_key, text )
            except Exception as ex:
                QMessageBox.warning( self, '', ex.__str__() )

    def __insert_product_one_info_handle(self):
        r_index = self.__current_product_info_row
        dialog = NCreateNewPropertyDialog( self, self.__database, self.current_product.product_id, r_index )
        dialog.exec_()
        self.__update_product_info( self.current_product )

    def __delete_product_one_info_handle(self):
        resp = QMessageBox.question( self, '确认', '确定要删除该属性？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No )
        if resp == QMessageBox.No:
            return
        r_index = self.__current_product_info_row
        r_m_index_1 = self.productInfoModel.index( r_index, 0 )
        r_item_1: QStandardItem = self.productInfoModel.itemFromIndex( r_m_index_1 )
        the_key = r_item_1.data( Qt.DisplayRole )
        self.__database.delete_product_other_info( self.current_product.product_id, the_key )
        self.productInfoModel.takeRow( r_index )

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
                    self.productView.clearSelection()
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
        # 产品相关信息
        self.__update_product_info( product_obj )
        # 产品的售后服务记录
        self.serviceRecordModel.clear()
        self.serviceRecordModel.setHorizontalHeaderLabels( ('编号', '描述') )
        self.afterSaleInfoTable.horizontalHeader().setStretchLastSection( True )
        service_info_s = self.__database.get_service_record( product_id=product_obj.product_id )
        for info in service_info_s:
            one_row = [QStandardItem( info[0] ), QStandardItem( info[1] )]
            self.serviceRecordModel.appendRow( one_row )
        if self.serviceRecordModel.rowCount() > 0:
            self.afterSaleInfoTable.resizeColumnsToContents()

    def __update_product_info(self, product_obj):
        self.productInfoModel.clear()
        self.productInfoModel.setHorizontalHeaderLabels( ('项目', '数值') )
        self.productInfoTable.horizontalHeader().setStretchLastSection( True )
        info_s = self.__database.get_other_product_info( product_id=product_obj.product_id )
        for info in info_s:
            one_row = [QStandardItem( info[0] ), QStandardItem( info[1] )]
            self.productInfoModel.appendRow( one_row )
        # 将销售情况添加入其中
        info_s_2 = self.__database.get_sold_customer( product_id=product_obj.product_id )
        if len( info_s_2 ) > 0:
            self.productInfoModel.appendRow( [QStandardItem( '客户' ), QStandardItem( info_s_2[0][0] )] )
            if info_s_2[0][1] is not None:
                self.productInfoModel.appendRow( [QStandardItem( '终端客户' ), QStandardItem( info_s_2[0][1] )] )
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
        self.__customerPanel.do_search()

    """
    search_parent: 是否要往上追溯
    """

    def fill_products_table(self, products, columns_setting=None, search_parent=False):
        self.productView.clear()
        self.temp_list.clear()
        if columns_setting is None:
            self.productView.setColumnCount( 5 )
            self.productView.setHeaderLabels( ['编号', '状态', '产品备注', '状态备注', '配置'] )
            for pp in products:
                if pp.product_id in self.temp_list.keys():
                    continue
                one_pp_data = [pp.product_id, pp.actual_status, pp.product_comment, pp.status_comment, pp.config]
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
        data_s = [pp.product_id, pp.actual_status, pp.product_comment, pp.status_comment, pp.config]
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
                one_cc_data = [cc.product_id, cc.actual_status, cc.product_comment, cc.status_comment, cc.config]
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


class CustomerView( QFrame ):

    def __init__(self, parent=None, database=None):
        super().__init__( parent )
        self.__parent = parent
        self.__database = database
        self.filterLineEdit = QLineEdit( self )
        self.cleanTextPushButton = QPushButton( self )
        self.customersList = QListWidget( self )
        self.__init_ui()

    def __init_ui(self):
        self.cleanTextPushButton.setText( '清空' )
        v_box = QVBoxLayout( self )

        filter_h_box = QHBoxLayout( self )
        filter_h_box.addWidget( QLabel( '过滤' ) )
        filter_h_box.addWidget( self.filterLineEdit )
        filter_h_box.addWidget( self.cleanTextPushButton )

        v_box.addLayout( filter_h_box )
        v_box.addWidget( self.customersList )

        self.setLayout( v_box )

        self.cleanTextPushButton.clicked.connect( self.__reset_search )
        self.filterLineEdit.returnPressed.connect( lambda: self.do_search( with_filter=True ) )
        self.customersList.currentItemChanged.connect( self.__select_customer_changed )

    def do_search(self, with_filter=False):
        if with_filter:
            tt = self.filterLineEdit.text().strip()
            if tt == '':
                tt = None
            rs = self.__database.get_customers( the_filter=tt )
        else:
            rs = self.__database.get_customers()
        self.customersList.clear()
        for r in rs:
            one_item = QListWidgetItem( r[1] )
            one_item.setData( Qt.UserRole, r[0] )
            self.customersList.addItem( one_item )

    def __reset_search(self):
        self.filterLineEdit.setText( '' )
        self.do_search( with_filter=False )

    def __select_customer_changed(self, item: QListWidgetItem):
        if item is not None:
            data = item.data( Qt.UserRole )
            temp_data = self.__database.get_products_from_customer( data )
            real_products = []
            for t in temp_data:
                real_products.append( Product( *t ) )
            self.__parent.show_products_from_outside( real_products )
