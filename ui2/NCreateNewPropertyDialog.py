# coding=gbk
from PyQt5.QtWidgets import QDialog, QComboBox, QLineEdit, QMessageBox

from db import ProductDatasHandler
from ui2.CreateNewPropertyDialog import *


class NCreateNewPropertyDialog( QDialog, Ui_Dialog ):

    def __init__(self, parent=None, database=None, product_id=None, index=-1):
        self.__parent = parent
        self.__database: ProductDatasHandler = database
        self.__product_id = product_id
        self.__insert_index = index
        super( NCreateNewPropertyDialog, self ).__init__( parent )

        self.nameComboBox = QComboBox()
        self.valueLineEdit = QLineEdit()

        self.setup_ui()

    def setup_ui(self):
        super( NCreateNewPropertyDialog, self ).setupUi( self )
        names = self.__database.get_product_other_info_name()
        self.nameComboBox.setEditable( True )
        self.nameComboBox.addItems( names )
        self.nameComboBox.setCurrentIndex( -1 )
        self.formLayout.addRow( '名称：', self.nameComboBox )
        self.formLayout.addRow( '值：', self.valueLineEdit )

    def accept(self) -> None:
        name = self.nameComboBox.currentText().strip()
        value = self.valueLineEdit.text().strip()
        if len( name ) < 1:
            QMessageBox.warning( self, '异常', '没有输入属性名称。' )
            return
        if len( value ) < 1:
            QMessageBox.warning( self, '异常', '没有输入属性值。' )
            return
        self.__database.insert_product_other_info( self.__product_id, name, value, self.__insert_index )
        self.close()
