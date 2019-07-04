import xlrd


class ExcelHandler2:
    """ 使用 xlrd 速度比较快 """

    def __init__(self, file_name):
        # 要加 formatting_info=True 才能获得单元格的格式
        self.__book = xlrd.open_workbook(file_name, formatting_info=True)

    def close(self):
        pass

    def get_sheets_name(self):
        return self.__book.sheet_names()

    def get_datas(self, sheet_name):
        ss = self.__book.sheet_by_name(sheet_name)
        columns = []
        datas = {}
        cinfomap = ss.colinfo_map
        rinfomap = ss.rowinfo_map
        for col_index in range(ss.ncols):
            if cinfomap.get(col_index, 0) and cinfomap[col_index].hidden == 1:
                continue
            tcell = ss.cell(0, col_index)
            col_name = tcell.value
            columns.append(col_name)
            data = []
            for row_index in range(1, ss.nrows):
                if rinfomap.get(row_index, 0) and rinfomap[row_index].hidden == 1:
                    continue
                tcell = ss.cell(row_index, col_index)
                vv = tcell.value
                if vv is None:
                    vv = ''
                data.append(vv)
            datas[col_name] = data
        return columns, datas
