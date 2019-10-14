import xlwt
from PyQt5.QtWidgets import (QMainWindow, QInputDialog)

from DataImporter import *
from Part import Part
from UiFrame import (PartInfoPanelInMainWindow, TagViewPanel, PartTablePanel,
                     ChildrenTablePanel, PartStructurePanel, CostInfoPanel)
from ui.DocOutputDialog import *
from ui.NPartColumnSettingDialog import *
from ui.NSetDefaultTagDialog import *
from ui.PartMainWindow import *


class NPartMainWindow( QMainWindow, Ui_MainWindow ):

    def __init__(self, parent=None, database=None, username=None, work_folder=None, pdm_vault=None, mode=None):
        super( NPartMainWindow, self ).__init__( parent )
        self.__database = database
        self.__username = username
        self.__work_folder = work_folder
        self.__pdm_vault = pdm_vault
        self.__mode = mode
        # Solidworks 程序
        self.__sw_app = None
        # 一个存储了设置参数的数据库，原ini文件变成为只读设置
        self.__config_file = None
        # 在 Part 添加 Tag 时，默认加入的组，-1 时为没有选中
        self.__default_tag_group = -1
        # 当前被选中的 Part，-1 时为没有选中
        self.__current_selected_part = -1
        self.tagTreePanel = TagViewPanel( self, database=database )
        self.partInfoPanel = PartInfoPanelInMainWindow( self, work_folder=self.__work_folder, database=self.__database )
        self.partInfoPanel.set_vault( pdm_vault )
        # 一个用于设置显示列的对话框，包含一些功能函数
        self.__columns_setting_dialog = None
        self.partListPanel = PartTablePanel( self, database=database )
        self.childrenTablePanel = ChildrenTablePanel( self, database=database )
        self.parentsTablePanel = ChildrenTablePanel( self, database=database, mode=1 )
        self.partStructurePanel = PartStructurePanel( self, database=database )
        self.partCostPanel = CostInfoPanel(self, database=database)
        self.__doc_output_dialog = None
        self.setup_ui()
        self.__all_dockWidget = [self.tagDockWidget, self.partInfoDockWidget,
                                 self.partChildrenDockWidget, self.partParentDockWidget,
                                 self.purchaseDockWidget, self.partStructureDockWidget]

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
        self.partParentDockWidget.setWidget( self.parentsTablePanel )
        self.purchaseDockWidget.setWidget(self.partCostPanel)
        self.setDockNestingEnabled( True )

        # 这种方式关闭时出现异常，暂时屏蔽
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
        self.doTaggedMenuItem.triggered.connect( self.__tag_parts )
        self.tagEditModeMenuItem.triggered.connect( self.__on_change_tag_mode )
        self.selectDefaultTagMenuItem.triggered.connect(self.__set_default_tag_set)
        self.addTag2PartMenuItem.triggered.connect(self.__add_tag_2_part)

        # 关于统计功能
        self.allStatisticsAction.triggered.connect( self.__set_statistics_setting_as_combo )
        self.purchaseStatisticsAction.triggered.connect( self.__set_statistics_setting_as_combo )
        self.assemblyStatisticsAction.triggered.connect( self.__set_statistics_setting_as_combo )

        # 关于一些权限的设定
        if self.__username == "陈泽斌":
            self.showPriceAction.setVisible(True)

    def __set_statistics_setting_as_combo(self):
        i = 2
        if self.sender() is self.allStatisticsAction:
            i = 1
        elif self.sender() is self.purchaseStatisticsAction:
            i = 2
        elif self.sender() is self.assemblyStatisticsAction:
            i = 3
        self.__set_statistics_easy( i )

    def __tag_parts(self):
        # 给所选的 Part 打标签
        parts = self.partListPanel.get_current_selected_parts()
        if len(parts) < 1:
            QMessageBox.warning(self, '', '没有选择部件。')
            return
        the_tag: Tag = self.tagTreePanel.get_current_selected_tag()
        if the_tag is None:
            QMessageBox.warning(self, '', '没有选择标签。')
            return
        resp = QMessageBox.question(self, '', '将这些部件，打上 \'{0}\' 的标签？'.format(the_tag),
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp == QMessageBox.No:
            return
        for p in parts:
            self.__database.set_tag_2_part(the_tag.tag_id, p)
        QMessageBox.information(self, '', 'Done!')

    def __set_statistics_easy(self, index):
        self.allStatisticsAction.setChecked( index == 1 )
        self.purchaseStatisticsAction.setChecked( index == 2 )
        self.assemblyStatisticsAction.setChecked( index == 3 )

    def __set_default_tag_set(self):
        dialog = NSetDefaultDialog(self, self.__database, self.__config_file)
        dialog.show()

    def get_statistics_setting(self):
        """ 获取统计的设置 """
        return (self.statisticsInTimeAction.isChecked(), self.allStatisticsAction.isChecked(),
                self.purchaseStatisticsAction.isChecked(), self.assemblyStatisticsAction.isChecked(),
                self.showPriceAction.isChecked())

    def __init_data(self):
        parts = Part.get_parts( self.__database )
        self.partListPanel.set_list_data( parts )
        tags = Tag.get_tags( self.__database )
        self.tagTreePanel.fill_data( tags )
        self.__reset_dock()
        if self.__mode == 1:
            mode_string = '(离线模式)'
        else:
            mode_string = '(在线模式)'
        self.setWindowTitle( '产品数据管理 __用户：{0} {1}'.format(self.__username, mode_string) )

    def __on_change_tag_mode(self, check_status):
        self.doTaggedMenuItem.setVisible( check_status )
        self.tagTreePanel.set_mode( check_status )

    def do_when_part_list_select(self, part_id):
        parts = Part.get_parts( self.__database, part_id=part_id )
        p = parts[0]
        self.__current_selected_part = p
        p.get_tags( self.__database )
        self.partInfoPanel.set_part_info( p, self.__database )
        self.childrenTablePanel.set_part_children( p, self.__database )
        self.parentsTablePanel.set_part_children(p, self.__database)
        self.partCostPanel.set_part_cost_info(p)

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
                if item is None:
                    continue
                table.write( j + 1, i, item.text() )
        DataImporter.export_data_2_excel(self, file)

    def set_display_columns(self, columns_data):
        self.partListPanel.set_display_columns( columns_data )

    def __set_part_view_column(self):
        if self.__columns_setting_dialog is None:
            tt = self.__database.get_tags(parent_id=None)
            column_lists = []
            for t in tt:
                column_lists.append((t[0], t[1]))
            self.__columns_setting_dialog = NPartColumnSettingDialog(self, column_lists, self.__config_file)
        self.__columns_setting_dialog.show()

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

        # 主动关闭后台线程
        self.partListPanel.stop_background_thread()
        thread_1 = self.partListPanel.fill_part_info_thread
        thread_1.quit()
        thread_1.wait()
        del thread_1
        self.partStructurePanel.stop_background_thread()
        thread_2 = self.partStructurePanel.statistics_thread
        thread_2.quit()
        thread_2.wait()
        del thread_2

        # 关闭数据库
        if self.__database is not None:
            self.__database.close()

        event.accept()

    def set_default_tag_group_2_add(self, tag_id):
        self.__default_tag_group = tag_id

    def __add_tag_2_part(self):
        if self.__current_selected_part is None:
            QMessageBox.information(self, '', '没有选择一个项目。', QMessageBox.Ok)
            return
        part_id = self.__current_selected_part.get_part_id()
        p = Part.get_parts(self.__database, part_id=part_id)[0]
        to_tag = None
        if self.__default_tag_group > 0:
            to_tag = Tag.get_tags(self.__database, tag_id=self.__default_tag_group)[0]
        msg_1 = '{0}_{1}'.format(p.part_id, p.name)
        msg_2 = '新标签'
        if to_tag is not None:
            msg_2 = to_tag.name
        text, ok_pressed = QInputDialog.getText(self, msg_1, msg_2, QLineEdit.Normal, '')
        if ok_pressed and text != '':
            result = Tag.add_one_tag_2_part(self.__database, text, part_id, parent_tag_id=to_tag.tag_id)
            the_tag_id = result[0]
            if result[1] == 1:
                self.set_status_bar_text('{0}_{1} 使用了原有的标签。'.format(p.part_id, p.name))
            elif result[1] == 0:
                self.set_status_bar_text('新建了一个标签，编号：{0}，刷新标签清单后显示。'.format(the_tag_id))
            elif result[1] == 2:
                self.set_status_bar_text('该便签已经存在了。')
        self.do_when_part_list_select(p.get_part_id())

    def add_config_and_init(self, sw_app, config_file):
        self.__sw_app = sw_app
        self.__config_file = config_file

        # 设定显示列
        tt = self.__database.get_tags( parent_id=None )
        column_lists = []
        for t in tt:
            column_lists.append( (t[0], t[1]) )
        self.__columns_setting_dialog = NPartColumnSettingDialog(self, column_lists, config_file)
        columns = self.__columns_setting_dialog.get_columns_setting()
        self.partListPanel.set_columns(columns)

        # 获取默认的 Tag
        conn = sqlite3.connect( self.__config_file )
        c = conn.cursor()
        c.execute( 'SELECT config_value FROM display_config WHERE name=\'default_tag_group\'' )
        self.__default_tag_group = int(c.fetchone()[0])
        conn.close()

        self.__init_data()

    def set_ready_for_statistics_display(self):
        """ 设置好统计显示清单，数量添加在最后。 """
        is_price_shown = self.showPriceAction.isChecked()
        self.partListPanel.set_list_header_4_statistics(is_price_shown)

    def add_one_item_to_statistics_list(self, part_id, qty, price):
        """ 增加一个项目去统计显示清单 """
        if not self.showPriceAction.isChecked():
            price = None
        self.partListPanel.add_one_part_4_statistics(part_id, qty, price)

    def show_statistics_finish_flag(self, finish_type, sum_price):
        """ 发出一个统计显示清单完成的信号 """
        if not finish_type:
            if not self.showPriceAction.isChecked():
                self.set_status_bar_text('完成统计。')
            else:
                self.set_status_bar_text('完成统计，总金额：{:.2f}'.format(sum_price))
            QTableWidget.resizeColumnsToContents(self.partListPanel.partList)
            QTableWidget.resizeRowsToContents(self.partListPanel.partList)
        else:
            self.set_status_bar_text('统计被中断。')
