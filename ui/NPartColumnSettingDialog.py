from ui.PartColumnSettingDialog import Ui_Dialog
from PyQt5.QtWidgets import (QDialog, QListWidgetItem)
from PyQt5.QtCore import Qt
import configparser


class NPartColumnSettingDialog(QDialog, Ui_Dialog):

    Columns = ('序号', '名称', '英文名称', '描述', '状态', '类别', '标准', '品牌', '巨轮智能ERP物料编码', '外部编码', '备注')

    def __init__(self, parent, ini_file):
        self.__parent = parent
        self.__ini_file = ini_file
        super(NPartColumnSettingDialog, self).__init__(parent)
        self.__setup_ui()

    def __setup_ui(self):
        super( NPartColumnSettingDialog, self ).setupUi( self )
        self.setFixedSize(380, 300)

        config = configparser.ConfigParser()
        config.read( 'pdm_config.ini', encoding='GBK' )
        columns_set = config.get( 'PartView', 'columns' )
        columns_set_flags = columns_set.split(',')
        index = 0
        for columns in NPartColumnSettingDialog.Columns:
            item = QListWidgetItem(columns)
            is_checked = Qt.Checked
            ii = int(columns_set_flags[index])
            if ii == 0:
                is_checked = Qt.Unchecked
            item.setCheckState(is_checked)
            self.columnListWidget.addItem(item)
            index += 1

    def accept(self):
        setting = []
        columns_count = self.columnListWidget.count()
        for i in range(0, columns_count):
            item: QListWidgetItem = self.columnListWidget.item(i)
            if item.checkState() == Qt.Checked:
                setting.append('1')
            else:
                setting.append('0')
        setting_str = ','.join(setting)
        config = configparser.ConfigParser()
        config.read(self.__ini_file, encoding='GBK')
        config.set('PartView', 'columns', setting_str)
        config.write(open(self.__ini_file, 'r+', encoding='GBK'))
        self.__parent.set_display_columns(NPartColumnSettingDialog.get_columns_setting())
        self.__parent.refresh_part_list()
        self.close()

    @staticmethod
    def get_columns_setting():
        config = configparser.ConfigParser()
        config.read( 'pdm_config.ini', encoding='GBK' )
        columns_set = config.get( 'PartView', 'columns' )
        columns_set_flags = columns_set.split( ',' )
        result = []
        result_str = []
        index = 0
        for c in columns_set_flags:
            ii = int(c)
            result.append(ii)
            if ii == 1:
                result_str.append(NPartColumnSettingDialog.Columns[index])
            index += 1
        return result, result_str
