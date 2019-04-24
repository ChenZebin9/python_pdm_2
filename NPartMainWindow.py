from PyQt5.QtWidgets import QMainWindow
import xlwt
import os
from DataImporter import *
from Part import Part, Tag
from UiFrame import (PartInfoPanelInMainWindow, TagViewPanel, PartTablePanel,
                     ChildrenTablePanel, PartStructurePanel)
from ui.NPartColumnSettingDialog import *
from ui.PartMainWindow import *
from ui.DocOutputDialog import *


class NPartMainWindow( QMainWindow, Ui_MainWindow ):

    def __init__(self, parent=None, database=None, username=None, work_folder=None, pdm_vault=None):
        super( NPartMainWindow, self ).__init__( parent )
        self.__database = database
        self.__username = username
        self.__work_folder = work_folder
        self.__pdm_vault = pdm_vault
        self.__sw_app = None
        self.tagTreePanel = TagViewPanel( self, database=database )
        self.partInfoPanel = PartInfoPanelInMainWindow( self, work_folder=self.__work_folder )
        self.partInfoPanel.set_vault( pdm_vault )
        self.partListPanel = PartTablePanel( self, database=database,
                                             columns=NPartColumnSettingDialog.get_columns_setting() )
        self.childrenTablePanel = ChildrenTablePanel( self, database=database )
        self.partStructurePanel = PartStructurePanel( self, database=database )
        self.__doc_output_dialog = None
        self.setup_ui()
        self.__all_dockWidget = [self.tagDockWidget, self.partInfoDockWidget,
                                 self.partChildrenDockWidget, self.partParentDockWidget,
                                 self.purchaseDockWidget, self.partStructureDockWidget]
        self.__init_data()

    def __remove_all_dock(self):
        for d in self.__all_dockWidget:
            self.removeDockWidget( d )

    def __show_dock(self, docks=None):
        if docks is None or len( docks ) < 1:
            for d in self.__all_dockWidget:
                d.show()
            return
        for i in docks:
            self.__all_dockWidget[i].show()

    def __reset_dock(self):
        self.__remove_all_dock()
        self.addDockWidget( Qt.LeftDockWidgetArea, self.tagDockWidget )
        self.tabifyDockWidget( self.tagDockWidget, self.partStructureDockWidget )
        self.addDockWidget( Qt.BottomDockWidgetArea, self.partInfoDockWidget )
        self.tabifyDockWidget( self.partInfoDockWidget, self.partChildrenDockWidget )
        self.tabifyDockWidget( self.partChildrenDockWidget, self.partParentDockWidget )
        self.tabifyDockWidget( self.partParentDockWidget, self.purchaseDockWidget )
        self.__show_dock()

    def setup_ui(self):
        super( NPartMainWindow, self ).setupUi( self )
        self.setCentralWidget( self.partListPanel )
        self.tagDockWidget.setWidget( self.tagTreePanel )
        self.partInfoDockWidget.setWidget( self.partInfoPanel )
        self.partChildrenDockWidget.setWidget( self.childrenTablePanel )
        self.partStructureDockWidget.setWidget( self.partStructurePanel )
        self.setDockNestingEnabled( True )

        self.exitMenuItem.triggered.connect( self.close )
        self.resetDocksMenuItem.triggered.connect( self.__reset_dock )
        self.add2TreeViewMenuItem.triggered.connect( self.__add_2_structure_view )
        self.importPartListMenuItem.triggered.connect( self.__import_part_list )
        self.exportPartListMenuItem.triggered.connect( self.__export_part_list )
        self.columnViewMenuItem.triggered.connect( self.__set_part_view_column )
        self.refreshMenuItem.triggered.connect( self.refresh_part_list )
        self.add2OutputListMenuItem.triggered.connect( self.__add_item_2_output_list )
        self.showOutputListMenuItem.triggered.connect( self.__show_output_list_dialog )

        # 实现标签的编辑功能
        self.tagEditModeMenuItem.triggered.connect( self.__on_change_tag_mode )

        # 关于统计功能
        self.allStatisticsAction.triggered.connect( self.__set_statistics_setting_as_combo )
        self.purchaseStatisticsAction.triggered.connect( self.__set_statistics_setting_as_combo )
        self.assemblyStatisticsAction.triggered.connect( self.__set_statistics_setting_as_combo )

    def __set_statistics_setting_as_combo(self):
        i = 2
        if self.sender() is self.allStatisticsAction:
            i = 1
        elif self.sender() is self.purchaseStatisticsAction:
            i = 2
        elif self.sender() is self.assemblyStatisticsAction:
            i = 3
        self.__set_statistics_easy( i )

    def __set_statistics_easy(self, index):
        self.allStatisticsAction.setChecked( index == 1 )
        self.purchaseStatisticsAction.setChecked( index == 2 )
        self.assemblyStatisticsAction.setChecked( index == 3 )

    def get_statistics_setting(self):
        """ 获取统计的设置 """
        return (self.statisticsInTimeAction.isChecked(), self.allStatisticsAction.isChecked(),
                self.purchaseStatisticsAction.isChecked(), self.assemblyStatisticsAction.isChecked())

    def __init_data(self):
        parts = Part.get_parts( self.__database )
        self.partListPanel.set_list_data( parts )
        tags = Tag.get_tags( self.__database )
        self.tagTreePanel.fill_data( tags )
        self.__reset_dock()
        self.setWindowTitle( '物料管理 __用户：' + self.__username )

    def __on_change_tag_mode(self, check_status):
        self.doTaggedMenuItem.setVisible( check_status )
        self.tagTreePanel.set_mode( check_status )

    def do_when_part_list_select(self, part_id):
        parts = Part.get_parts( self.__database, part_id=part_id )
        p = parts[0]
        p.get_tags( self.__database )
        self.partInfoPanel.set_part_info( p, self.__database )
        self.childrenTablePanel.set_part_children( p, self.__database )

    def do_when_tag_tree_select(self, tag_id):
        try:
            display_parts = Part.get_parts_from_tag( self.__database, tag_id )
            self.partListPanel.set_display_range( display_parts )
            self.partListPanel.set_list_data( display_parts )
        except Exception as ex:
            print( 'Error: ' + str( ex ) )

    def __add_2_structure_view(self):
        current_part = self.partListPanel.get_current_selected_part()
        if current_part is None or current_part <= 0:
            QMessageBox.warning( self, '空', '没有选择某项目！', QMessageBox.Ok )
            return
        part = Part.get_parts( database=self.__database, part_id=current_part )[0]
        children = part.get_children( self.__database )
        if children is None:
            QMessageBox.warning( self, '', '该项目没有子项目！', QMessageBox.Ok )
            return
        self.partStructureDockWidget.raise_()
        self.partStructurePanel.fill_data( part, children )

    def __add_item_2_output_list(self):
        all_parts = []
        if self.partListPanel.partList.hasFocus():
            select_parts = self.partListPanel.get_current_selected_parts()
            for p in select_parts:
                p = Part.get_parts( self.__database, part_id=p )[0]
                files = p.get_related_files( self.__database )
                """ 输出优先级：PDF、SLDDRW、SLDPRT """
                all_parts.append( [p.part_id, p.name, files] )
        elif self.partInfoPanel.relationFilesList.hasFocus():
            print( 'file list' )
        else:
            print( 'no list' )
        if self.__doc_output_dialog is None:
            self.__doc_output_dialog = DocOutputDialog( self, self.__pdm_vault, self.__sw_app )
        if not self.__doc_output_dialog.isVisible():
            self.__doc_output_dialog.show()
        self.__doc_output_dialog.add_doc_list( all_parts )

    def __show_output_list_dialog(self):
        if self.__doc_output_dialog is None:
            self.__doc_output_dialog = DocOutputDialog( self, self.__pdm_vault, self.__sw_app )
        if self.__doc_output_dialog.isVisible():
            return
        self.__doc_output_dialog.show()

    def show_parts_from_outside(self, parts):
        self.partListPanel.set_list_data( parts )

    def __import_part_list(self):
        DataImporter.import_data_4_parts_list( self, title='No name', database=self.__database )

    def __export_part_list(self):
        file = xlwt.Workbook()
        table = file.add_sheet( 'items list' )
        data_source = self.partListPanel.partList
        r_c = data_source.rowCount()
        c_c = data_source.columnCount()
        if r_c < 1:
            QMessageBox.Warning( self, '', '没有显示项目！', QMessageBox.Ok )
            return
        for i in range( c_c ):
            item = data_source.horizontalHeaderItem( i )
            table.write( 0, i, item.text() )
        for i in range( c_c ):
            for j in range( r_c ):
                item = data_source.item( j, i )
                table.write( j + 1, i, item.text() )
        DataImporter.export_data_2_excel(self, file)

    def set_display_columns(self, columns_data):
        self.partListPanel.set_display_columns( columns_data )

    def __set_part_view_column(self):
        dialog = NPartColumnSettingDialog( self, 'pdm_config.ini' )
        dialog.show()

    def refresh_part_list(self):
        parts_id = self.partListPanel.get_current_parts_id()
        if len( parts_id ) < 1:
            return
        parts = []
        for i in parts_id:
            p = Part.get_parts( self.__database, part_id=i )
            parts.extend( p )
        self.partListPanel.set_list_data( parts )
        self.partListPanel.set_display_range( parts )

    def set_status_bar_text(self, text):
        self.statusbar.showMessage( text )

    def closeEvent(self, event):
        if self.__doc_output_dialog is not None:
            if not self.__doc_output_dialog.all_task_done:
                # 后台还有任务在执行
                QMessageBox.warning( self, '', '后台还有任务在执行，暂时无法关闭。', QMessageBox.Ok )
                event.ignore()
                return
            if self.__doc_output_dialog.isVisible():
                self.__doc_output_dialog.close()
        del self.__doc_output_dialog

        if self.tagTreePanel.clipboard_is_not_empty():
            resp = QMessageBox.question( self, '', '剪切板还有标签数据，是否删除退出？', QMessageBox.Yes | QMessageBox.No )
            if resp == QMessageBox.No:
                event.ignore()
                return

        event.accept()

    def add_config(self, sw_app):
        self.__sw_app = sw_app

    def set_ready_for_statistics_display(self):
        """ 设置好统计显示清单 """
        pass

    def add_one_item_to_statistics_list(self, part_id, qty, unit):
        """ 增加一个项目去统计显示清单 """
        pass

    def show_statistics_finish_flag(self):
        """ 发出一个统计显示清单完成的信号 """
        pass
