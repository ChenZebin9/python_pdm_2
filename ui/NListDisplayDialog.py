# coding=gbk

from PyQt5.QtWidgets import (QDialog, QListWidgetItem)

from ui.ListDisplayDialog import Ui_listDisplayDialog


class NListDisplayDialog( QDialog, Ui_listDisplayDialog ):

    def __init__(self, parent=None, data=None):
        super( NListDisplayDialog, self ).__init__( parent )
        self.setup_ui()
        if data is not None:
            self.set_data( data )

    def setup_ui(self):
        super( NListDisplayDialog, self ).setupUi( self )
        self.setModal( True )
        self.setLayout( self.h_layout )
        self.theListWidget.setWrapping( True )

    def set_data(self, data):
        for d in data:
            item = QListWidgetItem( d, self.theListWidget )
            self.theListWidget.addItem( item )
