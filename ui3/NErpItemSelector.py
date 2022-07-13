# coding=gbk
from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QHeaderView, QMessageBox

from ui3.ErpItemSelector import Ui_Dialog


class NErpItemSelector( QDialog, Ui_Dialog ):

    def __init__(self, database, parent=None):
        self.__parent = parent
        self.__database = database
        self.__search_mode = -1  # 1 -> 通过物料编码，2 -> 通过物料描述
        self.is_zd_erp = True
        self.__model = QStandardItemModel()
        super( NErpItemSelector, self ).__init__( parent )
        self.setup_ui()

    def setup_ui(self):
        super( NErpItemSelector, self ).setupUi( self )
        self.setLayout( self.mv_layout )
        self.desRadioButton.setChecked( True )
        self.__search_mode = 2
        self.idRadioButton.toggled.connect( self.search_mode_changed )
        self.desRadioButton.toggled.connect( self.search_mode_changed )
        self.searchLineEdit.textChanged.connect( self.do_research )
        self.__model.setColumnCount( 3 )
        self.__model.setHorizontalHeaderLabels( ['物料编码', '单位', '物料描述'] )
        self.itemsTableView.setModel( self.__model )
        self.itemsTableView.horizontalHeader().setStretchLastSection( True )
        self.itemsTableView.setColumnWidth( 0, 160 )
        self.itemsTableView.setColumnWidth( 1, 60 )
        self.itemsTableView.horizontalHeader().setSectionResizeMode( 0, QHeaderView.Fixed )
        self.itemsTableView.horizontalHeader().setSectionResizeMode( 1, QHeaderView.Fixed )
        self.itemsTableView.horizontalHeader().setSectionResizeMode( 2, QHeaderView.Interactive )
        self.setWindowTitle( '从中德仓库选择' )

    def search_mode_changed(self, is_checked):
        if not is_checked:
            return
        self.__search_mode = 1 if self.sender() is self.idRadioButton else 2

    def do_research(self, txt: str):
        refresh = False
        if self.__search_mode == 1:
            # 通过物料编码搜索
            s_tr = txt.strip()
            c = len( s_tr )
            s_b = (3, 6, 9, 13)
            if c in s_b:
                r_s = self.__database.search_thr_erp_id( s_tr, is_zd=self.is_zd_erp )
                r_c = len( r_s )
                self.__model.setRowCount( 0 )
                for r in r_s:
                    self.__model.appendRow( [QStandardItem( r[0] ), QStandardItem( r[2] ), QStandardItem( r[1] )] )
                refresh = r_c > 0
        else:
            # 通过物料描述搜索
            s_tr = txt.strip()
            if len( s_tr ) >= 1:
                r_s = self.__database.search_thr_erp_description( s_tr, is_zd=self.is_zd_erp )
                r_c = len( r_s )
                self.__model.setRowCount( 0 )
                for r in r_s:
                    self.__model.appendRow( [QStandardItem( r[0] ), QStandardItem( r[2] ), QStandardItem( r[1] )] )
                refresh = r_c > 0
        if refresh:
            self.itemsTableView.horizontalHeader().resizeSection( 2, QHeaderView.ResizeToContents )

    def accept(self) -> None:
        selection_model: QItemSelectionModel = self.itemsTableView.selectionModel()
        indexes = selection_model.selectedIndexes()
        c = len( indexes )
        if c > 0:
            pass
            QMessageBox.information( self, '', '有所选择' )
            super( NErpItemSelector, self ).accept()
        else:
            QMessageBox.warning( self, '', '没有选择！' )

        # c = int( len( indexes ) / 3 )
        # for i in range( c ):
        #     first_index: QModelIndex = indexes[i * 5]
        #     self.__dest_data.removeRow( first_index.row() )
