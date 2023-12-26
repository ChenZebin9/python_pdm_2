from ui.SetDefaultTagDialog import *
from PyQt5.QtWidgets import (QDialog, QRadioButton)
from Part import Tag
import sqlite3


class NSetDefaultDialog(QDialog, Ui_Dialog):

    __select_resource = [1, 15, 16, 266, 1288, 2064, 4339]

    def __init__(self, parent=None, database=None, config_file=None):
        self.__parent = parent
        self.__database = database
        self.__config_file = config_file
        self.__radio_btn = {}
        self.__conn = sqlite3.connect(config_file)
        self.__c = self.__conn.cursor()
        super(NSetDefaultDialog, self).__init__(parent)
        self.setModal(True)
        self.__select_tag = self.__get_previous_setting()
        self.setup_ui()

    def setup_ui(self):
        super(NSetDefaultDialog, self).setupUi(self)
        btn = QRadioButton('None')
        self.__radio_btn['None'] = -1
        self.h_layout.addWidget(btn)
        if self.__select_tag == -1:
            btn.toggle()
        btn.toggled.connect( self.__btn_statue )
        for ii in self.__select_resource:
            the_tag: Tag = Tag.get_tags(self.__database, tag_id=ii)[0]
            btn = QRadioButton(the_tag.name)
            if self.__select_tag == ii:
                btn.toggle()
            btn.toggled.connect(self.__btn_statue)
            self.__radio_btn[the_tag.name] = ii
            self.h_layout.addWidget(btn)

    def __get_previous_setting(self):
        self.__c.execute('SELECT config_value FROM display_config WHERE name=\'default_tag_group\'')
        value = self.__c.fetchone()[0]
        return int(value)

    def __set_setting(self):
        self.__c.execute('UPDATE display_config SET config_value=\'{0}\' WHERE name=\'default_tag_group\''
                         .format(self.__select_tag))
        self.__conn.commit()

    def __btn_statue(self, statue):
        if not statue:
            return
        btn = self.sender()
        text = btn.text()
        self.__select_tag = self.__radio_btn[text]
        print( 'Default Tag to: {0}'.format(self.__select_tag) )

    def accept(self):
        self.__parent.set_default_tag_group_2_add(self.__select_tag)
        self.__set_setting()
        self.close()

    def closeEvent(self, event):
        self.__conn.close()
        event.accept()
