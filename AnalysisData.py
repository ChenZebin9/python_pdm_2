""" 分解EXCEL表的Comment数据 """
import xlwings as xw
import Com

dd = ('FromStorage', 'Contract', 'Price', 'RollBack', 'OriginalRecord')
dc = ('K', 'L', 'M', 'N', 'O')

for i in range( 2, 264 ):
    comment = xw.Range( f'J{i}' ).value
    if comment is not None and len( comment ) > 0:
        dict_data = Com.str_2_dict( comment )
        for j in range( 0, 5 ):
            t = dd[j]
            if t in dict_data:
                c = dc[j]
                xw.Range( f'{c}{i}' ).value = dict_data[t]
