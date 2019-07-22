import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QListWidgetItem)

from ui.PartColumnSettingDialog import Ui_Dialog


class NPartColumnSettingDialog(QDialog, Ui_Dialog):

    # 在可配置的列之前的固定列
    Before_columns = ( '序号', '名称', '英文名称', '描述', '状态' )
    # 在可配置的列之后的固定列
    After_columns = ( '备注', )

    def __init__(self, parent, columns_list, db_file):
        self.__parent = parent
        # 可配置的列，通过tag计算而出
        self.__columns = columns_list
        self.__db_file = db_file
        super(NPartColumnSettingDialog, self).__init__(parent)
        self.__setup_ui()

    def __setup_ui(self):
        super( NPartColumnSettingDialog, self ).setupUi( self )
        self.setFixedSize(380, 300)
        dd = self.__get_config_value()
        before_columns_set = dd[0]
        columns_set = dd[1]
        after_columns_set = dd[2]

        index = 0
        for b_c in NPartColumnSettingDialog.Before_columns:
            item = QListWidgetItem(b_c)
            if before_columns_set[index] == '1':
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.columnListWidget.addItem(item)
            index += 1

        for column in self.__columns:
            item = QListWidgetItem(column[1])
            item.setData(Qt.UserRole, column[0])
            is_checked = Qt.Unchecked
            if column[0] in columns_set:
                is_checked = Qt.Checked
            item.setCheckState(is_checked)
            self.columnListWidget.addItem(item)

        index = 0
        for a_c in NPartColumnSettingDialog.After_columns:
            item = QListWidgetItem(a_c)
            if after_columns_set[index] == '1':
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.columnListWidget.addItem(item)
            index += 1

    def accept(self):
        setting = []
        columns_count = self.columnListWidget.count()
        b_c = len( NPartColumnSettingDialog.Before_columns )
        b_set = []
        m_c = b_c + len( self.__columns )
        a_set = []
        for i in range(0, columns_count):
            item: QListWidgetItem = self.columnListWidget.item( i )
            if i < b_c:
                if item.checkState() == Qt.Checked:
                    b_set.append('1')
                else:
                    b_set.append('0')
            elif b_c <= i < m_c:
                if item.checkState() == Qt.Checked:
                    setting.append( item.data( Qt.UserRole ) )
            else:
                if item.checkState() == Qt.Checked:
                    a_set.append('1')
                else:
                    a_set.append('0')
        self.__set_config_value( ','.join(b_set), setting, ','.join(a_set) )
        self.__parent.set_display_columns(self.get_columns_setting())
        self.__parent.refresh_part_list()
        self.close()

    def __get_config_value(self):
        conn = sqlite3.connect( self.__db_file )
        c = conn.cursor()
        c.execute( 'SELECT config_value FROM display_config WHERE name=\'before_columns\'' )
        dd = c.fetchall()
        before_columns_set = dd[0][0].split(',')
        c.execute( 'SELECT column_id FROM display_columns' )
        dd = c.fetchall()
        columns_set = []
        for d in dd:
            columns_set.append( d[0] )
        c.execute( 'SELECT config_value FROM display_config WHERE name=\'after_columns\'' )
        dd = c.fetchall()
        after_columns_set = [dd[0][0]]
        conn.close()
        return before_columns_set, columns_set, after_columns_set

    def __set_config_value(self, before_set, the_value, after_set):
        conn = sqlite3.connect( self.__db_file )
        c = conn.cursor()
        c.execute( 'UPDATE display_config SET config_value=\'{0}\' WHERE name=\'before_columns\''.format(before_set) )
        c.execute( 'DELETE FROM display_columns')
        for i in the_value:
            c.execute( 'INSERT INTO display_columns VALUES ({0})'.format( i ) )
        c.execute( 'UPDATE display_config SET config_value=\'{0}\' WHERE name=\'after_columns\''.format( after_set ) )
        conn.commit()
        conn.close()

    def get_columns_setting(self):
        columns_set = self.__get_config_value()
        before_columns_flags = columns_set[0]
        after_columns_flags = columns_set[2]
        result = []
        result_str = []
        index = 0
        for c in before_columns_flags:
            ii = int(c)
            result.append(ii)
            if ii == 1:
                result_str.append(NPartColumnSettingDialog.Before_columns[index])
            index += 1
        for c in self.__columns:
            ii = c[0]
            if ii in columns_set[1]:
                result.append( ii )
                result_str.append( c[1] )
        index = 0
        for c in after_columns_flags:
            ii = int(c)
            result.append( ii )
            if ii == 1:
                result_str.append( NPartColumnSettingDialog.After_columns[index] )
            index += 1
        return result, result_str
