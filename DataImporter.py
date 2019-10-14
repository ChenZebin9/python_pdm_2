import win32con
import win32ui
import os

from PyQt5.QtWidgets import (QMessageBox)

from excel.ExcelHandler import (ExcelHandler2)
from ui.NImportSettingDialog import (NImportSettingDialog)


class DataImporter:

    @staticmethod
    def import_data_4_parts_list(parent=None, title=None, database=None):
        try:
            openFlags = win32con.OFN_FILEMUSTEXIST
            fspec = 'Excel Files (*.xls, *.xlsx)|*.xls;*.xlsx|Text Files (*.txt)|*.txt||'
            dlg = win32ui.CreateFileDialog(1, None, None, openFlags, fspec)
            selected_file = None
            if dlg.DoModal() == win32con.IDOK:
                selected_file = dlg.GetPathName()
            if selected_file is None:
                return None
            file_name = selected_file
            dialog = NImportSettingDialog(parent, title, database)
            rows = ('零件号', '巨轮智能ERP物料编码', '巨轮中德ERP物料编码', '外部编码')
            if file_name.upper().endswith('TXT'):
                # TXT文件的处理，只有一栏
                dialog.set_txt_mode(rows, file_name)
                dialog.show()
            else:
                # EXCEL文件的处理，使用 xlrd 比 xlwings 的读取速度快很多
                excel = ExcelHandler2(file_name)
                dialog.set_excel_mode(rows, excel)
                dialog.show()
        except Exception as ex:
            QMessageBox.warning(parent, '', str(ex), QMessageBox.Ok)

    @staticmethod
    def export_data_2_excel(parent, data):
        fspec = 'Excel Files (*.xls)|*.xls||'
        dlg = win32ui.CreateFileDialog(0, None, None, win32con.OFN_OVERWRITEPROMPT, fspec)
        if dlg.DoModal() != win32con.IDOK:
            QMessageBox.information( parent, '', '放弃保存！', QMessageBox.Ok )
            return
        file_name = dlg.GetPathName()
        if not file_name.upper()[-4:] == '.XLS':
            file_name += '.xls'
        data.save( file_name )
        rsp = QMessageBox.question( parent, '', '是否打开文件？', QMessageBox.Yes | QMessageBox.No )
        if rsp == QMessageBox.Yes:
            os.startfile( file_name )
