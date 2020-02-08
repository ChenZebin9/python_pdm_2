# coding=gbk
import sys
from PyQt5.QtWidgets import (QDialog, QApplication)
from ui.EntranceDialog import *


class NEntranceDialog( QDialog, Ui_Dialog ):
    """
    �������ܵ�ѡ����ڣ�
    Button_1 - ��Ʒ���ݹ��� - NPartMainWindow
    Button_2 - ��Ʒ���� - NProductMainWindow
    Button_3 - ������ - ��Ҫ��
    Button_4 - �������ϵ� - NCreatePickBillDialog
    """

    def __init__(self, parent=None):
        super( NEntranceDialog, self ).__init__( parent )
        self.__inner_result = 0
        self.__button_list = []
        self.setup_ui()

    def setup_ui(self):
        super( NEntranceDialog, self ).setupUi( self )
        self.__button_list.extend( [self.Button_1, self.Button_2, self.Button_3, self.Button_4] )
        self.setLayout( self.vLayout )
        for b in self.__button_list:
            b.clicked.connect( self.__button_handler )

    def __button_handler(self):
        index = self.__button_list.index( self.sender() )
        self.__inner_result = index + 1
        self.done( self.__inner_result )


if __name__ == '__main__':
    app = QApplication( sys.argv )
    the_dialog = NEntranceDialog( parent=None )
    result = the_dialog.show()
    print(result)
    sys.exit( app.exec_() )
