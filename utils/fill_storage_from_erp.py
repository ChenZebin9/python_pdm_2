# coding=gbk
""" 从第一个Excel表获取库存信息，填入到第二个Excel表中 """
import xlwings as xw

max_row = int( input( '最大的行号：' ) ) + 1

storage_dict = {}

for i in range( 2, max_row ):
    erp_code = xw.Range( f'A{i}' ).value
    qty = xw.Range( f'G{i}' ).value
    all_price = xw.Range( f'I{i}' ).value
    u_price = all_price / qty
    if erp_code in storage_dict:
        dd = storage_dict[erp_code]
        o_qty = dd[0]
        o_u_price = dd[1]
        n_qty = qty + o_qty
        n_all_price = qty * u_price + o_qty * o_u_price
        storage_dict[erp_code] = (n_qty, n_all_price / n_qty)
    else:
        storage_dict[erp_code] = (qty, u_price)

print( '数据收集完毕，激活目标清单，按任意键继续……' )
input( 'to be continue' )

max_row = int( input( '最大的行号：' ) ) + 1
column = input( '物料编码，库存，单价所在的列：' )

for i in range( 2, max_row ):
    erp_code = xw.Range( f'{column[0]}{i}' ).value
    if erp_code is None or len( erp_code ) != 13:
        continue
    if erp_code in storage_dict:
        dd = storage_dict[erp_code]
        xw.Range( f'{column[1]}{i}' ).value = dd[0]
        xw.Range( f'{column[2]}{i}' ).value = dd[1]

print( '填充完成。' )
