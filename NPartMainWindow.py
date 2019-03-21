from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from Part import Part, Tag
from UiFrame import (PartInfoPanelInMainWindow, TagViewPanel, PartTablePanel,
                     ChildrenTablePanel, PartStructurePanel)
from ui.PartMainWindow import *


class NPartMainWindow( QMainWindow, Ui_MainWindow ):

    def __init__(self, parent=None, database=None, username=None, work_folder=None, pdm_vault=None):
        super( NPartMainWindow, self ).__init__( parent )
        self.__database = database
        self.__username = username
        self.__work_folder = work_folder
        self.__pdm_vault = pdm_vault
        self.tagTreePanel = TagViewPanel( self , database=database)
        self.partInfoPanel = PartInfoPanelInMainWindow( self, work_folder=self.__work_folder )
        self.partListPanel = PartTablePanel( self , database=database)
        self.childrenTablePanel = ChildrenTablePanel(self, database=database)
        self.partStructurePanel = PartStructurePanel(self, database=database)
        self.setup_ui()
        self.__all_dockWidget = [self.tagDockWidget, self.partInfoDockWidget,
                                 self.partChildrenDockWidget, self.partParentDockWidget,
                                 self.purchaseDockWidget, self.partStructureDockWidget]
        self.__init_data()

    def __remove_all_dock(self):
        for d in self.__all_dockWidget:
            self.removeDockWidget(d)

    def __show_dock(self, docks=None):
        if docks is None or len(docks) < 1:
            for d in self.__all_dockWidget:
                d.show()
            return
        for i in docks:
            self.__all_dockWidget[i].show()

    def __reset_dock(self):
        self.__remove_all_dock()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tagDockWidget)
        self.tabifyDockWidget(self.tagDockWidget, self.partStructureDockWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.partInfoDockWidget)
        self.tabifyDockWidget(self.partInfoDockWidget, self.partChildrenDockWidget)
        self.tabifyDockWidget(self.partChildrenDockWidget, self.partParentDockWidget)
        self.tabifyDockWidget(self.partParentDockWidget, self.purchaseDockWidget)
        self.__show_dock()

    def setup_ui(self):
        super( NPartMainWindow, self ).setupUi( self )
        self.setCentralWidget(self.partListPanel)
        self.tagDockWidget.setWidget(self.tagTreePanel)
        self.partInfoDockWidget.setWidget(self.partInfoPanel)
        self.partChildrenDockWidget.setWidget(self.childrenTablePanel)
        self.partStructureDockWidget.setWidget(self.partStructurePanel)
        self.setDockNestingEnabled(True)
        self.exitMenuItem.triggered.connect(self.close)
        self.resetDocksMenuItem.triggered.connect(self.__reset_dock)
        self.add2TreeViewMenuItem.triggered.connect(self.__add_2_structure_view)

    def __init_data(self):
        parts = Part.get_parts(self.__database)
        self.partListPanel.set_list_data(parts)
        tags = Tag.get_tags(self.__database)
        self.tagTreePanel.fill_data(tags)
        self.__reset_dock()
        self.setWindowTitle('物料管理 __用户：' + self.__username)

    def do_when_part_list_select(self, part_id):
        parts = Part.get_parts( self.__database, part_id=part_id )
        p = parts[0]
        p.get_tags(self.__database)
        self.partInfoPanel.set_part_info(p, self.__database)
        self.childrenTablePanel.set_part_children(p, self.__database)

    def do_when_tag_tree_select(self, tag_id):
        try:
            display_parts = Part.get_parts_from_tag(self.__database, tag_id)
            self.partListPanel.set_display_range(display_parts)
            self.partListPanel.set_list_data(display_parts)
        except Exception as ex:
            print('Error: ' + str(ex))

    def __add_2_structure_view(self):
        current_part = self.partListPanel.get_current_selected_part()
        if current_part <= 0:
            QMessageBox.warning(self, '空', '没有选择某项目！', QMessageBox.Ok)
            return
        part = Part.get_parts(database=self.__database, part_id=current_part)[0]
        children = part.get_children(self.__database)
        if children is None:
            QMessageBox.warning(self, '', '该项目没有子项目！', QMessageBox.Ok)
            return
        self.partStructureDockWidget.raise_()
        self.partStructurePanel.fill_data(part, children)

    def show_parts_from_outside(self, parts):
        self.partListPanel.set_list_data(parts)
