# coding=gbk

from PyQt5.QtWidgets import (QDialog, QListWidgetItem, QLineEdit, QDateEdit, QComboBox, QPlainTextEdit)

from ui2.ProductSoldDialog import Ui_Dialog
import datetime


class NProductSoldDialog( QDialog, Ui_Dialog ):

    def __init__(self, parent=None, database=None, contract_nr=None):
        super( NProductSoldDialog, self ).__init__( parent )
        self.__parent = parent
        self.__database = database
        all_customers = self.__get_customer_list()
        self.__contract_nr = contract_nr
        self.__contract_nr_lineEdit = QLineEdit()
        self.__date_selector = QDateEdit()
        self.__customer_selector = QComboBox()
        self.__terminal_customer_selector = QComboBox()
        self.__customer_selector.addItems( all_customers )
        self.__terminal_customer_selector.addItems( all_customers )
        self.__comment_textEdit = QPlainTextEdit()
        self.setup_ui()

    def setup_ui(self):
        super( NProductSoldDialog, self ).setupUi( self )
        self.setLayout( self.v1_layout )
        self.__date_selector.setCalendarPopup( True )

        self.f3_layout.addRow( '合同号', self.__contract_nr_lineEdit )
        self.f3_layout.addRow( '日期', self.__date_selector )
        self.f3_layout.addRow( '客户', self.__customer_selector )
        self.f3_layout.addRow( '终端客户', self.__terminal_customer_selector )
        self.f3_layout.addRow( '备注', self.__comment_textEdit )

        self.__customer_selector.setCurrentIndex( -1 )
        self.__terminal_customer_selector.setCurrentIndex( -1 )
        self.__date_selector.setDate( datetime.date.today() )

    def __get_customer_list(self):
        """
        获取用户清单
        :return:
        """
        all_customers = []
        ts = self.__database.get_customers()
        for t in ts:
            all_customers.append( t[1] )
        return all_customers

    def closeEvent(self, event):
        self.__parent.show_add_product_action( False )
        event.accept()

    def accept(self):
        contract_nr = self.__contract_nr_lineEdit.text()
        contract_date = self.__date_selector.text()
        customer = self.__customer_selector.currentText()
        terminal_customer = self.__terminal_customer_selector.currentText()
        comment = self.__comment_textEdit.toPlainText()
        products = []
        for i in range( self.listWidget.count() ):
            item: QListWidgetItem = self.listWidget.item( i )
            products.append( item.text() )
        data_dict = {'No': contract_nr, 'Date': contract_date, 'Customer': customer,
                     'Terminal Customer': terminal_customer, 'Comment': comment, 'Products': products}
        self.__database.insert_sale_contract( data_dict )
        self.close()

    def reject(self):
        self.close()

    def add_2_product_list(self, product_id):
        """
        将一个产品加入销售的产品清单中
        :param product_id:
        :return:
        """
        item = QListWidgetItem( product_id, self.listWidget )
        self.listWidget.addItem( item )
