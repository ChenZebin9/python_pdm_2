import os

import clr
from PyQt5.QtWidgets import (QMessageBox, QFileDialog)

import Com
from excel.ExcelHandler import (ExcelHandler3, ExcelHandler2)
from ui.NImportSettingDialog import (NImportSettingDialog)


class DataTransport:

    @staticmethod
    def import_data_4_parts_list(parent=None, title=None, database=None):
        try:
            f_spec = 'Excel Files (*.xls *.xlsx);;Text Files (*.txt)'
            previous_path = Com.get_property_value('load_path')
            ini_path = previous_path if previous_path != '' else '.'
            file_name, _ = QFileDialog.getOpenFileName(parent, caption='选择数据文件',
                                                       filter=f_spec, directory=ini_path)
            if file_name == '':
                return
            load_path = os.path.dirname(file_name)
            Com.save_property_value('load_path', load_path)
            dialog = NImportSettingDialog( parent, title, database )
            rows = ('零件号', '巨轮智能ERP物料编码', '巨轮中德ERP物料编码', '外部编码')
            if file_name.upper().endswith( 'TXT' ):
                # TXT文件的处理，只有一栏
                dialog.set_txt_mode( rows, file_name )
                dialog.show()
            else:
                # EXCEL文件的处理，使用 xlrd 比 xlwings 的读取速度快很多
                if file_name[-3:].upper() == 'XLS':
                    excel = ExcelHandler2( file_name )
                else:
                    excel = ExcelHandler3( file_name )
                dialog.set_excel_mode( rows, excel )
                dialog.show()
        except Exception as ex:
            QMessageBox.warning( parent, '', str( ex ), QMessageBox.Ok )

    @staticmethod
    def export_data_2_excel(parent, data):
        f_spec = 'Excel Files (*.xls)'
        previous_path = Com.get_property_value('save_path')
        ini_path = previous_path if previous_path != '' else '.'
        file_name, _ = QFileDialog.getSaveFileName(parent, '保存数据至文件', directory=ini_path, filter=f_spec)
        if file_name == '':
            QMessageBox.information(parent, '', '放弃保存！', QMessageBox.Ok)
            return
        save_path = os.path.dirname(file_name)
        Com.save_property_value('save_path', save_path)
        if not file_name.upper()[-4:] == '.XLS':
            file_name += '.xls'
        data.save( file_name )
        rsp = QMessageBox.question( parent, '', '是否打开文件？', QMessageBox.Yes | QMessageBox.No )
        if rsp == QMessageBox.Yes:
            os.startfile( file_name )

    @staticmethod
    def export_data_2_excel_2(header, data_s):
        clr.FindAssembly('dlls/Greatoo_JJ_Com.dll')
        clr.AddReference('dlls/Greatoo_JJ_Com')
        from Greatoo_JJ_Com import ExportToExcel2
        c = ExportToExcel2()
        return c.ExportList(header, data_s)
