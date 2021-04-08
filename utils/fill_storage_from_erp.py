# coding=gbk
""" �ӵ�һ��Excel���ȡ�����Ϣ�����뵽�ڶ���Excel���� """
import xlwings as xw

max_row = int( input( '�����кţ�' ) ) + 1

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

print( '�����ռ���ϣ�����Ŀ���嵥�����������������' )
input( 'to be continue' )

max_row = int( input( '�����кţ�' ) ) + 1
column = input( '���ϱ��룬��棬�������ڵ��У�' )

for i in range( 2, max_row ):
    erp_code = xw.Range( f'{column[0]}{i}' ).value
    if erp_code is None or len( erp_code ) != 13:
        continue
    if erp_code in storage_dict:
        dd = storage_dict[erp_code]
        xw.Range( f'{column[1]}{i}' ).value = dd[0]
        xw.Range( f'{column[2]}{i}' ).value = dd[1]

print( '�����ɡ�' )
