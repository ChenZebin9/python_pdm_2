# coding=gbk
import sys
from PyQt5.QtWidgets import (QDialog, QApplication)
from ui.EntranceDialog import *


class NEntranceDialog( QDialog, Ui_Dialog ):
    """
    各个功能的选择入口：
    Button_1 - 产品数据管理 - NPartMainWindow
    Button_2 - 产品管理 - NProductMainWindow
    Button_3 - 库存管理 - 将要做
    Button_4 - 生成领料单 - NCreatePickBillDialog
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
