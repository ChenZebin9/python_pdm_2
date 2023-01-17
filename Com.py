# coding=gbk
""" 一些通用的、基础的功能 """
import sqlite3
from functools import reduce
import clr
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QPlainTextEdit

import Com

local_config_file = ''


def dict_2_str(the_dict):
    """
    dict 转 str, dict中的key和value，不能有：及%
    :param the_dict:
    :return:
    """
    temp_list = []
    for k in the_dict:
        v = the_dict[k]
        temp_list.append(f'{k}:{v}')
    return '#'.join(temp_list)


def str_2_dict(the_str):
    """
    str 转 dict
    :param the_str:
    :return:
    """
    result_dict = {}
    temp_list = the_str.split('#')
    for t in temp_list:
        k_v = t.split(':')
        result_dict[k_v[0]] = k_v[1]
    return result_dict


def str2float(s):
    """
    将str转换为float
    :param s:
    :return:
    """
    return reduce(lambda x, y: x + int2dec(y), map(str2int, s.split('.')))


def char2num(s):
    return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]


def str2int(s):
    return reduce(lambda x, y: x * 10 + y, map(char2num, s))


def intLen(i):
    return len('%d' % i)


def int2dec(i):
    return i / (10 ** intLen(i))


class Queue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) <= 0

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

    def is_exist(self, item):
        return item in self.items

    def current_list(self):
        return self.items


def capture_image(part_id):
    """
    截图，并返回数据
    :param part_id: 零件号，用于生成临时文件
    :return: byte[] or null
    """
    clr.FindAssembly('dlls/Greatoo_JJ_Com.dll')
    clr.AddReference('dlls/Greatoo_JJ_Com')
    from Greatoo_JJ_Com import CaptureImage
    part_id_s = '{:08d}'.format(part_id)
    t = CaptureImage.CaptureOne(part_id_s)
    result = None
    if t is not None:
        result = t
    clr.clrModule('dlls/Greatoo_JJ_Com')
    return result


def get_property_value(name):
    conn = sqlite3.connect(Com.local_config_file)
    c = conn.cursor()
    c.execute(f'SELECT [PropertyValue] FROM [operation_property] WHERE [PropertyName]=\'{name}\'')
    dd = c.fetchall()
    conn.close()
    if len(dd) < 1:
        return ''
    else:
        return dd[0][0]


def save_property_value(name, value):
    conn = sqlite3.connect(Com.local_config_file)
    c = conn.cursor()
    c.execute(f'SELECT [PropertyValue] FROM [operation_property] WHERE [PropertyName]=\'{name}\'')
    dd = c.fetchall()
    if len(dd) < 1:
        c.execute(f'INSERT INTO [operation_property] VALUES (\'{name}\', \'{value}\')')
    else:
        c.execute(f'UPDATE [operation_property] SET [PropertyValue]=\'{value}\' WHERE [PropertyName]=\'{name}\'')
    conn.commit()
    conn.close()


class MyInputDialog(QDialog):

    def __init__(self, parent, title='输入', _txt=''):
        """
        多行的文本的输入框
        :param parent:
        :param _txt: 预定义的对话框
        """
        super(QDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.__text_edit_line = QPlainTextEdit()
        self.txt = ''
        if _txt is not None and len(_txt) > 1:
            self.__text_edit_line.setPlainText(_txt)
            self.txt = _txt
        self.__button_box = QDialogButtonBox()
        self.__button_box.setOrientation(Qt.Horizontal)
        self.__button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Yes)
        self.__button_box.accepted.connect(self.accept)
        self.__button_box.rejected.connect(self.reject)
        __layout = QtWidgets.QVBoxLayout()
        __layout.addWidget(self.__text_edit_line)
        __layout.addWidget(self.__button_box)
        self.setLayout(__layout)
        self.setMinimumHeight(160)

    def accept(self):
        self.txt = self.__text_edit_line.toPlainText()
        super(MyInputDialog, self).accept()

    def reject(self):
        self.txt = ''
        super(MyInputDialog, self).reject()
