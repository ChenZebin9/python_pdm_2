# coding=gbk
import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication)
from ui2.ProduceMainWindow import *


class NProduceMainWindow( QMainWindow, Ui_MainWindow ):

    def __init__(self, parent=None, database=None, username=None, pdm_vault=None):
        super( NProduceMainWindow, self ).__init__( parent )
        self.setup_ui()
        self.__all_dockWidget = [self.WorkgroupDockWidget, self.CtDockWidgetContents]

    def setup_ui(self):
        super( NProduceMainWindow, self ).setupUi( self )
        self.WkDockWidgetContents.setLayout( self.v_layout_3 )
        self.CtDockWidgetContents.setLayout( self.v_layout_2 )
        self.RequirementCentralWidget.setLayout(self.v_layout_1)


if __name__ == '__main__':
    app = QApplication( sys.argv )
    test_dialog = NProduceMainWindow( parent=None, database=None, username='陈泽斌', pdm_vault=None )
    test_dialog.show()
    sys.exit( app.exec_() )
