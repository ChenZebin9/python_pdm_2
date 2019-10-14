# coding=gbk
from PyQt5.QtWidgets import (QDialog, QComboBox, QLineEdit,
                             QTextEdit, QCheckBox, QMessageBox)

from db.ProductDatasHandler import SqliteHandler
from ui.ProductInfoDialog import *


class NProductInfoDialog( QDialog, Ui_Dialog ):

    def __init__(self, parent=None, database=None, product_id=None, mode=1):
        self.__parent = parent
        self.__database: SqliteHandler = database
        super( NProductInfoDialog, self ).__init__( parent )
        self.productIdEdit = QLineEdit( self )
        self.productCommentEdit = QTextEdit( self )
        self.statusCommentEdit = QTextEdit( self )
        self.configEdit = QLineEdit( self )
        self.typeCombo = QComboBox( self )
        self.initStatusCombo = QComboBox( self )
        self.costTypeCombo = QComboBox( self )
        self.isChildCheck = QCheckBox( self )
        self.parentCombo = QComboBox( self )
        self.setup_ui()
        self.__product_types_list = None
        self.__status_list = None
        self.__cost_types_list = None
        self.__products_list = None
        # mode
        # 1 - create
        # 2 - modify
        # 3 - copy, create
        self.__dialog_mode = mode
        self.__init_data( product_id )

    def setup_ui(self):
        super( NProductInfoDialog, self ).setupUi( self )
        self.main_h_box.setContentsMargins( 5, 5, 5, 5 )

        self.form_box.addRow( '序号', self.productIdEdit )
        self.form_box.addRow( '产品备注', self.productCommentEdit )
        self.form_box.addRow( '状态备注', self.statusCommentEdit )
        self.form_box.addRow( '配置', self.configEdit )
        self.form_box.addRow( '类型', self.typeCombo )
        self.form_box.addRow( '状态', self.initStatusCombo )
        self.form_box.addRow( '物料分配', self.costTypeCombo )

        self.isChildCheck.setText( '包括于' )
        self.inner_h_box.addWidget( self.isChildCheck )
        self.inner_h_box.addWidget( self.parentCombo )
        self.parentCombo.setEnabled( False )

        self.setLayout( self.main_h_box )

        self.isChildCheck.clicked.connect( self.__check_box_changed )

    def __init_data(self, product_id):
        self.__product_types_list = self.__database.get_types()
        self.__cost_types_list = self.__database.get_cost_types()
        self.typeCombo.addItems( self.__product_types_list )
        self.costTypeCombo.addItems( self.__cost_types_list )
        pps = self.__database.get_products()
        ps = []
        for p in pps:
            ps.append( p[0] )
        ps.sort()
        self.__products_list = ps
        self.parentCombo.addItems( ps )
        self.__status_list = self.__database.get_status()
        self.initStatusCombo.addItems( self.__status_list )
        if product_id is not None:
            ps = self.__database.get_products_by_id( product_id )
            p = None
            if len( ps ) > 0:
                p = ps[0]
            self.productIdEdit.setText( p[0] )
            self.productCommentEdit.setText( p[7] )
            self.statusCommentEdit.setText( p[8] )
            self.configEdit.setText( p[9] )
            self.typeCombo.setCurrentIndex( self.__product_types_list.index( p[1] ) )
            self.costTypeCombo.setCurrentIndex( self.__cost_types_list.index( p[6] ) )
            self.initStatusCombo.setCurrentIndex( self.__status_list.index( p[2] ) )
            if p[-1] is not None:
                self.isChildCheck.setChecked( True )
                self.parentCombo.setEnabled( True )
                self.parentCombo.setCurrentIndex( self.__products_list.index( p[-1] ) )
            if self.__dialog_mode == 3:
                self.productIdEdit.setText( '' )
            if self.__dialog_mode == 2:
                self.productIdEdit.setEnabled( False )

    def __check_box_changed(self, check_status):
        self.parentCombo.setEnabled( check_status )

    def accept(self):
        product_id = NProductInfoDialog.__add_quotes( self.productIdEdit.text() )
        product_type = NProductInfoDialog.__add_quotes( self.typeCombo.currentText() )
        status = NProductInfoDialog.__add_quotes( self.initStatusCombo.currentText() )
        cost_type = NProductInfoDialog.__add_quotes( self.costTypeCombo.currentText() )
        p_comment = self.productCommentEdit.toPlainText()
        p_comment = NProductInfoDialog.__strip_handle( p_comment )
        s_comment = self.statusCommentEdit.toPlainText()
        s_comment = NProductInfoDialog.__strip_handle( s_comment )
        config = self.configEdit.text()
        config = NProductInfoDialog.__strip_handle( config )
        is_child = self.isChildCheck.isChecked()
        if is_child:
            parent_product = '\'{0}\''.format( self.parentCombo.currentText() )
        else:
            parent_product = 'NULL'
        if self.__dialog_mode == 1 or self.__dialog_mode == 3:
            data_s = [product_id, product_type, status, cost_type, p_comment, s_comment, config, parent_product]
            tag_s = {'类型': self.typeCombo.currentText(),
                     '状态': self.initStatusCombo.currentText(),
                     '物料归类': self.costTypeCombo.currentText()}
            try:
                self.__database.insert_product_record( data=data_s, tag=tag_s )
                QMessageBox.information( self, '', '完成产品{0}的插入。'.format( product_id ),
                                         QMessageBox.Yes, QMessageBox.Yes )
            except Exception as e:
                QMessageBox.warning( self, '插入出错', e, QMessageBox.Yes, QMessageBox.Yes )
        elif self.__dialog_mode == 2:
            data_s = [product_id, product_type, status, cost_type, p_comment, s_comment, config, parent_product]
            try:
                self.__database.update_prduct( data_s )
                QMessageBox.information( self, '', '完成产品{0}的更新。'.format( product_id ) )
            except Exception as e:
                QMessageBox.warning( self, '更新出错', e, QMessageBox.Yes, QMessageBox.Yes )
        self.close()

    @staticmethod
    def __strip_handle(the_str):
        if the_str is None:
            return 'NULL'
        tt = the_str.strip()
        if len( tt ) > 0:
            return '\'{0}\''.format( tt )
        else:
            return 'NULL'

    @staticmethod
    def __add_quotes(the_str):
        return '\'{0}\''.format( the_str )
