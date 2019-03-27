from PyQt5.QtWidgets import (QFileDialog, QMessageBox)
from ui.NImportSettingDialog import (NImportSettingDialog)
from excel.ExcelHandler import (ExcelHandler2)


class DataImporter:

    @staticmethod
    def import_data_4_parts_list(parent=None, title=None, database=None):
        try:
            selected_file, _ = QFileDialog.getOpenFileName(
                parent=parent,
                caption=title,
                filter='Excel File (*.xls *.xlsx);;Text Files (*.txt)')
            if selected_file == '':
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
