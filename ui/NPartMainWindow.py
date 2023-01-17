import configparser
import xlwt
from PyQt5.QtWidgets import (QMainWindow, QInputDialog, QListWidget)

import Com
from DataTransport import *
from UiFrame import (PartInfoPanelInMainWindow, TagViewPanel, PartTablePanel,
                     ChildrenTablePanel, PartStructurePanel, CostInfoPanel, IdenticalPartsPanel)
from ui.DocOutputDialog import *
from ui.NPartColumnSettingDialog import *
from ui.NSetDefaultTagDialog import *
from ui.PartMainWindow import *
from ui.NCreatePartDialog import *
from ui3.NCreatePickBillDialog import *
from ui3.NCreateRequirementDialog import *
from ui3.NHandleEntranceDialog import *
from ui3.NHandlePickMaterialDialog import *
from db.jl_erp import JL_ERP_Database
from Com import str2float, Queue
import datetime


class NPartMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None, database=None, username=None, work_folder=None, pdm_vault=None, mode=None,
                 local_folder=None, ):
        super(NPartMainWindow, self).__init__(parent)
        self.__database = database
        self.__username = username
        self.__work_folder = work_folder
        self.__pdm_vault = pdm_vault
        self.__mode = mode
        self.__is_offline = mode == 1
        self.__local_folder = local_folder
        # 第一次初始化的标记
        self.__in_initialation = True
        # Solidworks 程序
        self.__sw_app = None
        # 一个存储了设置参数的数据库，原ini文件变成为只读设置
        self.__config_file = None
        # 在 Part 添加 Tag 时，默认加入的组，-1 时为没有选中
        self.__default_tag_group = -1
        # 当前被选中的 Part，-1 时为没有选中
        self.__current_selected_part = -1
        # 新建Part时，可黏贴的Part
        self.part_2_paste = None
        # 一些Panel组件
        self.tagTreePanel = TagViewPanel(self, database=database)
        self.partInfoPanel = PartInfoPanelInMainWindow(self, work_folder=self.__work_folder,
                                                       database=self.__database, is_offline=self.__is_offline)
        self.partInfoPanel.set_vault(pdm_vault)
        # 能否进行列表编辑的标记
        self.edit_child_mode = False
        # 仓位列表
        self.__storing_pos_list_widget = QListWidget()
        self.__storing_pos_checkbox = []
        # 导入数据的临时存放位置
        self.__import_cache = []
        # 显示需求对话框有没有存在
        self.__requirement_dialog_shown = False
        self.__the_requirement_dialog = None
        # 状态栏显示的信息，最多5个
        self.__status_message = Queue()
        # 一个用于设置显示列的对话框，包含一些功能函数
        self.__columns_setting_dialog = None
        self.partListPanel = PartTablePanel(self, database=database)
        self.childrenTablePanel = ChildrenTablePanel(self, database=database)
        self.parentsTablePanel = ChildrenTablePanel(self, database=database, mode=1)
        self.partStructurePanel = PartStructurePanel(self, database=database)
        self.identicalManagementPanel = IdenticalPartsPanel(self, database=database)
        self.partCostPanel = CostInfoPanel(self, database=database)
        self.__doc_output_dialog = None
        # 是否显示仓储信息
        self.__show_storage_info = False
        self.__pick_material_dialog = None
        self.setup_ui()
        self.__all_dockWidget = [self.tagDockWidget, self.partInfoDockWidget,
                                 self.partChildrenDockWidget, self.partParentDockWidget,
                                 self.purchaseDockWidget, self.partStructureDockWidget,
                                 self.storingPositionDockWidget, self.identicalManagementDockWidget]
        self.__reset_dock()

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
        self.tabifyDockWidget(self.partStructureDockWidget, self.identicalManagementDockWidget)
        self.tabifyDockWidget(self.identicalManagementDockWidget, self.storingPositionDockWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.partInfoDockWidget)
        self.tabifyDockWidget(self.partInfoDockWidget, self.partChildrenDockWidget)
        self.tabifyDockWidget(self.partChildrenDockWidget, self.partParentDockWidget)
        self.tabifyDockWidget(self.partParentDockWidget, self.purchaseDockWidget)
        self.__show_dock()

    def close(self) -> bool:
        super(NPartMainWindow, self).close()
        # other operation
        pass

    def setup_ui(self):
        if self.__mode == 1:
            self.__change_platte()
        config = configparser.ConfigParser()
        config.read('pdm_config.ini', encoding='GBK')

        super(NPartMainWindow, self).setupUi(self)
        self.setCentralWidget(self.partListPanel)
        self.tagDockWidget.setWidget(self.tagTreePanel)
        self.partInfoDockWidget.setWidget(self.partInfoPanel)
        self.partChildrenDockWidget.setWidget(self.childrenTablePanel)
        self.partStructureDockWidget.setWidget(self.partStructurePanel)
        self.partParentDockWidget.setWidget(self.parentsTablePanel)
        self.purchaseDockWidget.setWidget(self.partCostPanel)
        self.identicalManagementDockWidget.setWidget(self.identicalManagementPanel)
        self.setDockNestingEnabled(True)

        # 仓位组件的设置
        all_pos = self.__database.get_all_storing_position()
        for p in all_pos:
            a_item = QListWidgetItem(self.__storing_pos_list_widget)
            a_check_box = QCheckBox()
            defined_text = config.get('PositionDefine', p)
            if defined_text is not None:
                item_text = f'{p} {defined_text}'
            else:
                item_text = p
            a_check_box.setText(item_text)
            self.__storing_pos_list_widget.setItemWidget(a_item, a_check_box)
            a_check_box.stateChanged.connect(self.__when_storing_pos_check)
            self.__storing_pos_checkbox.append(a_check_box)
        v_box = QVBoxLayout(self.dockWidgetContents_5)
        v_box.addWidget(self.__storing_pos_list_widget)
        self.dockWidgetContents_5.setLayout(v_box)

        # 基础性的功能
        self.actionCreatePart.triggered.connect(self.__create_part)

        # 这种方式关闭时出现异常，暂时屏蔽
        self.exitMenuItem.triggered.connect(self.close)
        self.resetDocksMenuItem.triggered.connect(self.__reset_dock)
        self.add2TreeViewMenuItem.triggered.connect(self.__add_2_structure_view)
        self.importPartListMenuItem.triggered.connect(self.__import_part_list)
        self.exportPartListMenuItem.triggered.connect(self.__export_part_list_2)
        self.columnViewMenuItem.triggered.connect(self.__set_part_view_column)
        self.refreshMenuItem.triggered.connect(self.refresh_part_list)
        self.add2OutputListMenuItem.triggered.connect(self.__add_item_2_output_list)
        self.showOutputListMenuItem.triggered.connect(self.__show_output_list_dialog)

        # 实现标签的编辑功能
        self.doTaggedMenuItem.triggered.connect(self.__tag_parts)
        self.tagEditModeMenuItem.triggered.connect(self.__on_change_tag_mode)
        self.selectDefaultTagMenuItem.triggered.connect(self.__set_default_tag_set)
        self.addTag2PartMenuItem.triggered.connect(self.__add_tag_2_part)
        self.importTagsMenuItem.triggered.connect(self.__import_tags_link_2_part)

        # 关于统计功能
        self.allStatisticsAction.triggered.connect(self.__set_statistics_setting_as_combo)
        self.purchaseStatisticsAction.triggered.connect(self.__set_statistics_setting_as_combo)
        self.assemblyStatisticsAction.triggered.connect(self.__set_statistics_setting_as_combo)

        # 关于一些权限的设定
        self.showPriceAction.setVisible(True)

        # 关于同质化描述的设定
        self.identicalGroupEditModeMenuItem.triggered.connect(self.__set_action_about_identical_edit_mode)
        self.createIdenticalDesciptionMenuItem.triggered.connect(self.__create_identical_description_handler)
        self.joinIntoIdenticalGroupMenuItem.triggered.connect(self.__edit_part_in_identical_group_handler)
        self.removeFromIdenticalGroupMenuItem.triggered.connect(self.__edit_part_in_identical_group_handler)

        # 关于仓储（配料）信息的显示
        self.showStorageMenuItem.triggered.connect(self.__set_storage_shown_flag)
        self.pickMaterialsAction.triggered.connect(self.__show_pick_material_dialog)
        self.add2pickDialogAction.triggered.connect(self.__add_items_2_pick_dialog)
        self.startRequirementAction.triggered.connect(self.__create_requirement)
        self.handleReqiurementAction.triggered.connect(self.__handle_the_requirement)
        self.add2RequirementAction.triggered.connect(self.__add_part_2_requirement)
        self.actionGoBack2Storage.triggered.connect(self.__go_back_to_storage)

        # 其它一些产品技术文档的功能
        self.actionLocalPdfFirst.triggered.connect(self.__set_use_local_pdf_flag)

    def __edit_part_in_identical_group_handler(self):
        """
        加入新的同质描述
        :return:
        """
        do_join = self.sender() is self.joinIntoIdenticalGroupMenuItem
        try:
            fun_id = self.identicalManagementPanel.current_fun_id
            if fun_id < 1:
                QMessageBox.warning(self, '', '没有选择同质描述。')
                return
            part_id_s = self.partListPanel.get_current_selected_parts()
            if len(part_id_s) < 1:
                QMessageBox.warning(self, '', '没有选择零件。')
            if do_join:
                # 添加关联
                c = 0
                for part_id in part_id_s:
                    s, _ = QInputDialog.getInt(self, '评分', f'输入{part_id:08d}的评分', value=6, min=1, max=10)
                    if not _:
                        self.set_status_bar_text(f'跳过了{part_id:08d}。')
                        continue
                    c += 1
                    self.__database.edit_part_to_identical_group(fun_id, part_id, grade=s)
                self.set_status_bar_text(f'完成了{c}个零件的关联。')
            else:
                # 移除关联
                for part_id in part_id_s:
                    resp = QMessageBox.question(self, '确定', f'确定要移除{part_id:08d}的同质组关联吗？',
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if resp == QMessageBox.No:
                        continue
                    self.__database.edit_part_to_identical_group(fun_id, part_id, add_action=False)
                    self.set_status_bar_text(f'移除了{part_id:08d}在同质组的关联。')
        except Exception as ex:
            QMessageBox.critical(self, '操作过程有误', str(ex))

    def __set_action_about_identical_edit_mode(self, is_checked):
        self.joinIntoIdenticalGroupMenuItem.setVisible(is_checked)
        self.removeFromIdenticalGroupMenuItem.setVisible(is_checked)
        self.identicalManagementPanel.set_identical_panel_edit_mode(is_checked)

    def __create_identical_description_handler(self):
        """
        创建同质描述
        :return:
        """
        d = Com.MyInputDialog(self, '新的同质描述', '')
        resp = d.exec()
        if resp == QDialog.Accepted:
            t = d.txt
            if len(t) > 0:
                fun_id = self.__database.set_identical_description(t)
                self.set_status_bar_text(f'创建了编号为 {fun_id} 的同质描述。')
            else:
                QMessageBox.warning(self, '', '无效输入。')

    def __go_back_to_storage(self):
        """
        退料
        :return:
        """
        dialog = NHandlePickMaterialDialog(self, self.__database, self.__username)
        dialog.show()

    def __create_part(self):
        """
        创建新单元的对话框
        :return:
        """
        c_p_dialog = NCreatePartDialog(self, self.__database, self.part_2_paste)
        c_p_dialog.setModal(True)
        c_p_dialog.show()
        self.part_2_paste = None

    def __add_part_2_requirement(self):
        """
        将选择的物料添加入需求对话框
        :return:
        """
        if self.__the_requirement_dialog is None:
            return
        parts = self.partListPanel.get_current_selected_parts()
        if parts is not None and len(parts) > 0:
            self.__the_requirement_dialog.add_items(parts)

    def __create_requirement(self):
        """
        启动物料需求
        :return:
        """
        if not self.__requirement_dialog_shown:
            config_dict = {'Operator': self.__username}
            dialog = NCreateRequirementDialog(parent=self, database=self.__database, config_dict=config_dict)
            dialog.show()
            self.__the_requirement_dialog = dialog
            self.__requirement_dialog_shown = True
            self.add2RequirementAction.setVisible(True)

    def flag_when_requirement_dialog_close(self):
        """
        当需求对话框被关闭时，进行标记
        :return:
        """
        self.__requirement_dialog_shown = False
        self.__the_requirement_dialog = None
        self.add2RequirementAction.setVisible(False)

    def __handle_the_requirement(self):
        """
        处理物料需求
        :return:
        """
        config_dict = {'Operator': self.__username}
        dialog = NHandleEntranceDialog(parent=self, database=self.__database, config_dict=config_dict)
        dialog.show()

    def __set_use_local_pdf_flag(self, use_pdf):
        """
        设置使用本地图纸的标记
        :param use_pdf: bool 使用的标签
        :return:
        """
        if use_pdf:
            self.partInfoPanel.set_use_local_pdf_first(self.__local_folder)
        else:
            self.partInfoPanel.set_use_local_pdf_first(None)

    def __add_items_2_pick_dialog(self):
        """
        将所选的零件添加至领料对话框
        :return:
        """
        jl_erp_database = None
        self.__show_pick_material_dialog()
        try:
            all_parts = []
            if self.partListPanel.partList.hasFocus():
                select_parts = self.partListPanel.get_current_selected_parts()
                if len(select_parts) < 1:
                    QMessageBox.warning(self, '无效操作', '没有选择任何物料')
                    return
                for p in select_parts:
                    p = Part.get_parts(self.__database, part_id=p)[0]
                    if self.__pick_material_dialog.is_zd_erp():
                        erp_info = p.get_erp_info(self.__database)
                    else:
                        erp_code = p.get_specified_tag(self.__database, '巨轮智能ERP物料编码')
                        if erp_code is None:
                            erp_info = None
                        else:
                            if jl_erp_database is None:
                                jl_erp_database = JL_ERP_Database()
                            erp_info = jl_erp_database.get_erp_data(erp_code)
                    if erp_info is None:
                        if self.__pick_material_dialog.get_default_storage() != 'A':
                            QMessageBox.warning(self, '忽略', f'{p.name}({p.part_id})没有ERP的信息，被忽略。')
                            continue
                        else:
                            description = [p.name]
                            if p.description is not None and p.description != '':
                                description.append(p.description)
                            t1 = p.get_specified_tag(self.__database, '品牌')
                            t2 = p.get_specified_tag(self.__database, '标准')
                            t3 = p.get_specified_tag(self.__database, '单位')
                            unit_str = t3 if len(t3) > 0 else '件'
                            if len(t1) > 0:
                                description.append(f'({t1})')
                            if len(t2) > 0:
                                description.append(f'({t2})')
                            des_str = ' '.join(description)
                            erp_id = p.part_id
                    else:
                        erp_id = erp_info[0]
                        des_str = erp_info[1]
                        unit_str = erp_info[2]
                    all_parts.append((p.part_id, erp_id, des_str, unit_str))
            else:
                return
            if len(all_parts) >= 1:
                self.__pick_material_dialog.add_items(all_parts)
        finally:
            if jl_erp_database is not None:
                jl_erp_database.close()

    def __create_pick_material_dialog_and_config(self):
        """
        创建一个领料对话框，并进行预先设置领料对话框
        :return:
        """
        self.__pick_material_dialog = NCreatePickBillDialog(self.__database, parent=self)
        the_config_dict = {}
        the_text, ok = QInputDialog.getText(self, '默认合同号', '合同号：')
        if ok:
            try_record = self.__database.get_products_by_id(the_text)
            if len(try_record) > 0:
                the_config_dict['合同号'] = the_text
            else:
                QMessageBox.warning(self, '无效输入', '所输入的产品编号不存在！')
        the_text, ok = QInputDialog.getItem(self, '选择', '库房号：', self.__database.get_all_storing_position())
        if ok:
            the_config_dict['仓库'] = the_text
        if self.__username is not None and len(self.__username) > 0:
            the_config_dict['操作者'] = self.__username
        today_bill = QDate.currentDate().toString('yyMMdd')
        the_config_dict['清单'] = self.__database.get_available_supply_operation_bill(prefix=f'P{today_bill}')
        self.__pick_material_dialog.set_config(the_config_dict)

    def __show_pick_material_dialog(self):
        """
        显示直接从仓库领料的对话框
        :return:
        """
        if self.__pick_material_dialog is None or not self.__pick_material_dialog.isVisible():
            self.__create_pick_material_dialog_and_config()
            self.__pick_material_dialog.show()

    def __set_storage_shown_flag(self, is_check):
        self.partListPanel.set_storage_shown_flags(is_check)
        self.actionViewSupply.setVisible(is_check)

    def __when_storing_pos_check(self):
        selected_pos = []
        for c in self.__storing_pos_checkbox:
            if c.isChecked():
                t_s = c.text()
                pos = t_s.split(' ')[0]
                selected_pos.append(pos)
        if len(selected_pos) < 1:
            self.set_status_bar_text('没有选择仓位！')
            return
        pp = self.__database.get_storing(part_id=None, position=selected_pos)
        p_s = []
        for p in pp:
            p_s.append(p[0])
        p_s = list(set(p_s))
        p_s.sort()
        part_s = []
        for p_id in p_s:
            the_part_s = Part.get_parts(self.__database, part_id=p_id)
            if len(the_part_s) > 0:
                part_s.append(the_part_s[0])
        if not self.showStorageMenuItem.isChecked():
            self.showStorageMenuItem.setChecked(True)
            self.__set_storage_shown_flag(True)
        self.show_parts_from_outside(part_s)

    def __set_statistics_setting_as_combo(self):
        i = 2
        if self.sender() is self.allStatisticsAction:
            i = 1
        elif self.sender() is self.purchaseStatisticsAction:
            i = 2
        elif self.sender() is self.assemblyStatisticsAction:
            i = 3
        self.__set_statistics_easy(i)

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
        self.allStatisticsAction.setChecked(index == 1)
        self.purchaseStatisticsAction.setChecked(index == 2)
        self.assemblyStatisticsAction.setChecked(index == 3)

    def __set_default_tag_set(self):
        dialog = NSetDefaultDialog(self, self.__database, self.__config_file)
        dialog.show()

    def set_children_list_edit_mode(self, is_edit_mode):
        self.edit_child_mode = is_edit_mode

    def get_statistics_setting(self):
        """ 获取统计的设置 """
        return (self.statisticsInTimeAction.isChecked(), self.allStatisticsAction.isChecked(),
                self.purchaseStatisticsAction.isChecked(), self.assemblyStatisticsAction.isChecked(),
                self.showPriceAction.isChecked())

    def __init_data(self):
        # 设定显示列
        tt = self.__database.get_tags(parent_id=None)
        column_lists = []
        for t in tt:
            column_lists.append((t[0], t[1]))
        self.__columns_setting_dialog = NPartColumnSettingDialog(self, column_lists, self.__config_file)
        columns = self.__columns_setting_dialog.get_columns_setting()
        self.partListPanel.set_columns(columns)

        # 获取默认的 Tag
        conn = sqlite3.connect(self.__config_file)
        c = conn.cursor()
        c.execute('SELECT config_value FROM display_config WHERE name=\'default_tag_group\'')
        self.__default_tag_group = int(c.fetchone()[0])
        conn.close()

        parts = Part.get_parts(self.__database)
        self.partListPanel.set_list_data(parts)
        tags = Tag.get_tags(self.__database)
        self.tagTreePanel.fill_data(tags)
        self.__reset_dock()
        if self.__mode == 1:
            mode_string = '(离线模式)'
        else:
            mode_string = '(在线模式)'
        self.setWindowTitle('产品数据管理 __用户：{0} {1}'.format(self.__username, mode_string))
        # 默认使用本地PDF文件
        self.actionLocalPdfFirst.setChecked(True)
        self.__set_use_local_pdf_flag(True)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        if self.__in_initialation:
            self.__init_data()
            self.__in_initialation = False

    def __on_change_tag_mode(self, check_status):
        self.doTaggedMenuItem.setVisible(check_status)
        self.tagTreePanel.set_mode(check_status)

    def do_when_part_list_select(self, part_id, all_id=None):
        if (part_id is not None) and part_id > 0:
            parts = Part.get_parts(self.__database, part_id=part_id)
            p = parts[0]
            p.get_tags(self.__database)
        else:
            p = None
        self.__current_selected_part = p
        self.partInfoPanel.set_part_info(p, self.__database)
        self.partInfoPanel.set_part_operate_button_status(2, True)
        self.partInfoPanel.set_part_operate_button_status(1, False)
        self.childrenTablePanel.set_part_children(p, self.__database, all_id)
        self.parentsTablePanel.set_part_children(p, self.__database)
        self.partCostPanel.set_part_cost_info(p)
        pp = -1 if p is None else p.get_part_id()
        self.identicalManagementPanel.display_current_part_identical_group(part_id=pp)

    def do_when_tag_tree_select(self, tag_id):
        try:
            display_parts = Part.get_parts_from_tag(self.__database, tag_id)
            self.partListPanel.set_display_range(display_parts)
            self.partListPanel.set_list_data(display_parts)
        except Exception as ex:
            print('Error: ' + str(ex))

    def __add_2_structure_view(self):
        current_part = self.partListPanel.get_current_selected_part()
        if current_part is None or current_part <= 0:
            QMessageBox.warning(self, '空', '没有选择某项目！', QMessageBox.Ok)
            return
        part = Part.get_parts(database=self.__database, part_id=current_part)[0]
        children = part.get_children(self.__database)
        if children is None:
            QMessageBox.warning(self, '', '该项目没有子项目！', QMessageBox.Ok)
            return
        self.partStructureDockWidget.raise_()
        self.partStructurePanel.fill_data(part, children)

    def __add_item_2_output_list(self):
        all_parts = []
        if self.partListPanel.partList.hasFocus():
            select_parts = self.partListPanel.get_current_selected_parts()
            for p in select_parts:
                p = Part.get_parts(self.__database, part_id=p)[0]
                files = p.get_related_files(self.__database)
                """ 输出优先级：PDF、SLDDRW、SLDPRT """
                all_parts.append([p.part_id, p.name, files])
        elif self.partInfoPanel.relationFilesList.hasFocus():
            print('file list')
        else:
            print('no list')
        if self.__doc_output_dialog is None:
            self.__doc_output_dialog = DocOutputDialog(self, self.__pdm_vault, self.__sw_app)
        if not self.__doc_output_dialog.isVisible():
            self.__doc_output_dialog.show()
        self.__doc_output_dialog.add_doc_list(all_parts)

    def __show_output_list_dialog(self):
        if self.__doc_output_dialog is None:
            self.__doc_output_dialog = DocOutputDialog(self, self.__pdm_vault, self.__sw_app)
        if self.__doc_output_dialog.isVisible():
            return
        self.__doc_output_dialog.show()

    def show_parts_from_outside(self, parts: [Part]):
        self.partListPanel.set_list_data(parts)

    def __import_part_list(self):
        DataTransport.import_data_4_parts_list(self, title='No name', database=self.__database)

    def fill_import_cache(self, data_s):
        self.__import_cache.clear()
        self.__import_cache.extend(data_s)

    def __import_tags_link_2_part(self):
        """
        通过一个选择对话框，将批量导入标签，并建立与零件的连接
        :return:
        """
        dlg = NImportSettingDialog(self, '批量导入标签数据', self.__database)
        caption = '选择要导入的标签数据文件'
        f, f_type = QFileDialog.getOpenFileName(self, caption, filter='Excel Files (*.xls *.xlsx)')
        if f == '':
            return
        tags = Tag.get_tags(self.__database)
        if f[-1] == 'x' or f[-1] == 'X':
            excel_file = ExcelHandler3(f)
        else:
            excel_file = ExcelHandler2(f)
        columns_name = ['零件号']
        for t in tags:
            the_tag: Tag = t
            columns_name.append(the_tag.name)
        dlg.set_excel_mode(columns_name, excel_file, general_use=True)
        dlg.exec_()
        if len(self.__import_cache) < 0:
            QMessageBox.warning(self, '', '没有数据')
            return
        first_r = self.__import_cache[0]
        if first_r[0] is None or (type(first_r[0]) == str and len(first_r[0]) < 1):
            QMessageBox.warning(self, '', '数据有误')
            return
        tag_2_tag = []
        tag_c = len(tags)
        for i in range(1, tag_c):
            if first_r[i] is not None and len(first_r[i]) > 0:
                tag_2_tag.append((tags[i - 1], i))
        for r in self.__import_cache:
            part_id = int(float(r[0]))
            parts = Part.get_parts(self.__database, part_id=part_id)
            if len(parts) < 1:
                QMessageBox.warning(self, '', f'{part_id}编号，未找到相应的数据。')
                continue
            the_part = parts[0]
            tag_datas = r[1:]
            for data_2_tag in tag_2_tag:
                parent_tag = data_2_tag[0]
                tag_name = r[data_2_tag[1]]
                the_part.get_tags(self.__database)
                part_tag = the_part.get_specified_tag(self.__database, parent_tag.name)
                will_create_tag = False
                if len(part_tag) > 0:
                    existed_tags = part_tag.split(' ')
                    if tag_name in existed_tags:
                        QMessageBox.warning(self, '已存在',
                                            f'编号为\"{the_part.part_id}\"的\"{the_part.name}\"，'
                                            f'\n已存在\"{parent_tag.name}->{tag_name}\"的标签，将被跳过！')
                        continue
                    resp = QMessageBox.question(self, '询问', f'编号为\"{the_part.part_id}\"的\"{the_part.name}\"，，'
                                                              f'\n已存在\"{parent_tag.name}\"类的标签，是否再新建一个？'
                                                              f'\nYes-新建标签，No-修改原有标签，Ignore-忽略。',
                                                QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore)
                    if resp == QMessageBox.Yes:
                        will_create_tag = True
                    elif resp == QMessageBox.No:
                        # 删除原有的
                        for tags_2_part in the_part.tags:
                            t: Tag = tags_2_part
                            if t.parent_name == parent_tag.name:
                                self.__database.del_tag_from_part(t.tag_id, the_part.get_part_id())
                        will_create_tag = True
                    elif resp == QMessageBox.Ignore:
                        continue
                else:
                    will_create_tag = True
                if will_create_tag:
                    # 新建标签
                    result = Tag.add_one_tag_2_part(self.__database, tag_name, the_part.get_part_id(),
                                                    parent_tag_id=parent_tag.tag_id)
                    the_tag_id = result[0]
                    if result[1] == 1:
                        self.set_status_bar_text('{0}_{1} 使用了原有的标签。'.format(the_part.part_id, the_part.name))
                    elif result[1] == 0:
                        self.set_status_bar_text('新建了一个标签，编号：{0}，刷新标签清单后显示。'.format(the_tag_id))
                    elif result[1] == 2:
                        self.set_status_bar_text('该便签已经存在了。')
        QMessageBox.information(self, '', '完成标签的导入。')

    def __export_part_list_2(self):
        data_source = self.partListPanel.partList
        r_c = data_source.rowCount()
        c_c = data_source.columnCount()
        header = []
        data_rows = []
        for i in range(c_c):
            item = data_source.horizontalHeaderItem(i)
            column_name = item.text()
            header.append(column_name)
        get_hyper_link = False
        if self.exportPurchaseLinkMenuItem.isChecked():
            # header.append( '链接' )
            get_hyper_link = True
        for j in range(r_c):
            one_row = []
            part_id = -1
            for i in range(c_c):
                item = data_source.item(j, i)
                if i == 0:
                    v = item.text().lstrip('0')
                    part_id = int(v)
                else:
                    v = item.text().strip()
                one_row.append(v)
            if get_hyper_link:
                the_link = self.__database.get_part_hyper_link(part_id)
                if the_link is not None:
                    one_row.append(the_link)
                else:
                    one_row.append('None')
            data_rows.append(one_row)
        result = DataTransport.export_data_2_excel_2(header, data_rows)
        print(result)

    def __export_part_list(self):
        file = xlwt.Workbook()
        table = file.add_sheet('items list')
        data_source = self.partListPanel.partList
        r_c = data_source.rowCount()
        c_c = data_source.columnCount()
        # 要显示为数量格式的列
        num_column_label = ('序号', '数量', '单价', '总价')
        date_column_label = ('最近修改日期', '')
        num_column_index = []
        date_column_index = []
        if r_c < 1:
            QMessageBox.Warning(self, '', '没有显示项目！', QMessageBox.Ok)
            return
        max_column_index = 0
        for i in range(c_c):
            item = data_source.horizontalHeaderItem(i)
            column_name = item.text()
            if column_name in num_column_label:
                num_column_index.append(i)
            elif column_name in date_column_label:
                date_column_index.append(i)
            table.write(0, i, column_name)
            max_column_index = i
        if self.exportPurchaseLinkMenuItem.isChecked():
            table.write(0, max_column_index + 1, '采购链接')
        id_style = xlwt.XFStyle()
        id_style.num_format_str = '00000000'
        for j in range(r_c):
            id_item = data_source.item(j, 0)
            part_id = int(id_item.text().lstrip('0'))
            table.write(j + 1, 0, part_id, id_style)
            if self.exportPurchaseLinkMenuItem.isChecked():
                the_link = self.__database.get_part_hyper_link(part_id)
                if the_link is not None:
                    table.write(j + 1, max_column_index + 1, xlwt.Formula(f'HYPERLINK("{the_link}";"采购链接")'))
        date_style = xlwt.XFStyle()
        date_style.num_format_str = 'YYYY/M/D'
        for i in range(1, c_c):
            for j in range(r_c):
                item = data_source.item(j, i)
                if item is None:
                    continue
                if i in num_column_index:
                    ss = item.text()
                    if len(ss.strip()) < 1:
                        continue
                    value = str2float(item.text())
                    table.write(j + 1, i, value)
                elif i in date_column_index:
                    value = datetime.datetime.strptime(item.text(), "%Y-%m-%d")
                    table.write(j + 1, i, value, date_style)
                else:
                    table.write(j + 1, i, item.text())
        DataTransport.export_data_2_excel(self, file)

    def set_display_columns(self, columns_data):
        self.partListPanel.set_display_columns(columns_data)

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
        if len(parts_id) < 1:
            return
        parts = []
        for i in parts_id:
            p = Part.get_parts(self.__database, part_id=i)
            parts.extend(p)
        self.partListPanel.set_list_data(parts)
        # self.partListPanel.set_display_range( parts )

    def set_status_bar_text(self, text):
        if self.__status_message.size() > 2:
            self.__status_message.dequeue()
        self.__status_message.enqueue(text)
        m = ' --> '.join(self.__status_message.current_list())
        self.statusbar.showMessage(m)

    def closeEvent(self, event):
        # TODO 值得关注
        if self.__doc_output_dialog is not None:
            if not self.__doc_output_dialog.all_task_done:
                # 后台还有任务在执行
                QMessageBox.warning(self, '', '后台还有任务在执行，暂时无法关闭。', QMessageBox.Ok)
                event.ignore()
                return
            if self.__doc_output_dialog.isVisible():
                self.__doc_output_dialog.close()
        del self.__doc_output_dialog

        if self.tagTreePanel.clipboard_is_not_empty():
            resp = QMessageBox.question(self, '', '剪切板还有标签数据，是否删除退出？', QMessageBox.Yes | QMessageBox.No)
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
        if ok_pressed and len(text.strip()) > 0:
            result = Tag.add_one_tag_2_part(self.__database, text.strip(), part_id, parent_tag_id=to_tag.tag_id)
            the_tag_id = result[0]
            if result[1] == 1:
                self.set_status_bar_text('{0}_{1} 使用了原有的标签。'.format(p.part_id, p.name))
            elif result[1] == 0:
                self.set_status_bar_text('新建了一个标签，编号：{0}，刷新标签清单后显示。'.format(the_tag_id))
            elif result[1] == 2:
                self.set_status_bar_text('该便签已经存在了。')
        self.do_when_part_list_select(p.get_part_id())

    def add_config(self, sw_app, config_file):
        self.__sw_app = sw_app
        self.__config_file = config_file

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

    def __change_platte(self):
        """
        改变离线时，窗口的主题
        :return:
        """
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 213, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 191, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 113, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 212, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 213, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 191, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 113, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 212, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 213, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 191, 63))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 113, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.setPalette(palette)
