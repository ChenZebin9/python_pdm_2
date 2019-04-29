import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QListWidgetItem)

from ui.PartColumnSettingDialog import Ui_Dialog


class NPartColumnSettingDialog(QDialog, Ui_Dialog):

    Columns = ('序号', '名称', '英文名称', '描述', '状态', '类别', '标准', '品牌', '巨轮智能ERP物料编码',
               '巨轮中德ERP物料编码', '外部编码', '备注')

    def __init__(self, parent, ini_file):
        self.__parent = parent
        self.__ini_file = ini_file
        super(NPartColumnSettingDialog, self).__init__(parent)
        self.__setup_ui()

    def __setup_ui(self):
        super( NPartColumnSettingDialog, self ).setupUi( self )
        self.setFixedSize(380, 300)
        columns_set = NPartColumnSettingDialog.__get_config_value()
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
        NPartColumnSettingDialog.__set_config_value(setting_str)
        self.__parent.set_display_columns(NPartColumnSettingDialog.get_columns_setting())
        self.__parent.refresh_part_list()
        self.close()

    @staticmethod
    def __get_config_value():
        conn = sqlite3.connect( 'rt_config.db' )
        c = conn.cursor()
        c.execute( 'SELECT config_value FROM display_config WHERE name=\'columns\'' )
        dd = c.fetchall()
        columns_set = dd[0][0]
        c.close()
        return columns_set

    @staticmethod
    def __set_config_value(the_value):
        conn = sqlite3.connect( 'rt_config.db' )
        c = conn.cursor()
        c.execute( 'UPDATE display_config SET config_value=\'{0}\' WHERE name=\'columns\''.format( the_value ) )
        conn.commit()
        c.close()

    @staticmethod
    def get_columns_setting():
        columns_set = NPartColumnSettingDialog.__get_config_value()
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
