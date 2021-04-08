# coding=gbk
""" ��������Excel�ļ����е�ERP�Ĳɹ�����������Ϊ���ݿ� """

import xlwings as xw
import sqlite3
import datetime


def trn(s):
    if s is None:
        return 'NULL'
    if isinstance( s, datetime.datetime ):
        ttt = s.__format__( '%Y-%m-%d' )
        return f'\'{ttt}\''
    if str.isspace( s ):
        return 'NULL'
    ss = s.strip()
    if len( ss ) < 1:
        return 'NULL'
    return f'\'{ss}\''


def trn2(ii):
    if ii is None:
        return 'NULL'
    return ii


# ʹ�÷�����
# 1. ����Ӧ���б����е�ERPϵͳ�е�������
#  1.1. ע������ERP���е�ERP�Ĺ�Ӧ��Ŀ¼��һֱ�ġ�
# 2. ��ERPϵͳ�У���ѯ�ɹ�����������������
#  2.1. ע��ERP�������Ĳɹ�������һ�����������޷������ģ�������BUG��
#  2.2. ע�������ɹ������������������������ݣ�����ĵ�����ÿ����Ľ�Ҫ���и��ġ�
# 3. ��Ҫ�ı��������������ļ�������ʾ������¼�����ݣ����������ļ�����Ϊ��zd_erp_purchase.db��
# 4. ��PDM���������嵥��������֮ǰ�����������ݣ���䡶��Ӧ�̡��͡�ȥ˰���ۡ���ע�������У�
#  4.1. �е�ERP���ϱ�ţ�H��
#  4.2. ����ERP���ϱ�ţ�G��
#  4.3. �������е¹�Ӧ�̺�ȥ˰���ۣ�N��O��
#  4.4. �����ľ��ֹ�Ӧ�̺�ȥ˰���ۣ�P��Q��
#  4.5. ע�⣬֮ǰҪ���������кš�

db_name = 'zd_erp_purchase.db'

con = sqlite3.connect( db_name )
c = con.cursor()

c.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type=\'table\' AND name=\'JJCost_Supplier2\'' )
rs = c.fetchone()
if rs[0] == 0:
    print( '����JJCost_Supplier2��' )
    c.execute( """
        CREATE TABLE [JJCost_Supplier2](
            [code] VARCHAR(15) NOT NULL PRIMARY KEY,
            [name] VARCHAR(256) NOT NULL,
            [short_name] VARCHAR(50)
        )
        """ )

c.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type=\'table\' AND name=\'JJCost_ErpPurchase\'' )
rs = c.fetchone()
if rs[0] == 0:
    print( '����JJCost_ErpPurchase��' )
    c.execute( """
        CREATE TABLE [JJCost_ErpPurchase](
            [erp_code] CHAR(13) NOT NULL,
            [bill_nr] CHAR(11) NOT NULL,
            [when_] DATETIME,
            [supplier] VARCHAR(15) NOT NULL REFERENCES [JJCost_Supplier2] ([code]),
            [qty] FLOAT,
            [tax_rate] FLOAT,
            [unit_price_not_tax] MONEY,
            PRIMARY KEY ([erp_code], [bill_nr])
        )
        """ )

c.execute( 'SELECT COUNT(*) FROM sqlite_master WHERE type=\'table\' AND name=\'JJCost_JL_ErpPurchase\'' )
rs = c.fetchone()
if rs[0] == 0:
    print( '����JJCost_JL_ErpPurchase��' )
    c.execute( """
        CREATE TABLE [JJCost_JL_ErpPurchase](
            [erp_code] CHAR(13) NOT NULL,
            [bill_nr] CHAR(11) NOT NULL,
            [when_] DATETIME,
            [supplier] VARCHAR(15) NOT NULL REFERENCES [JJCost_Supplier2] ([code]),
            [qty] FLOAT,
            [tax_rate] FLOAT,
            [unit_price_not_tax] MONEY,
            PRIMARY KEY ([erp_code], [bill_nr])
        )
        """ )

r = input( 'build supplier? n or y?' )

if r == 'y' or r == 'Y':
    for i in range( 2, 3000 ):
        code = xw.Range( f'B{i}' ).value
        if code is None or str.isspace( code ):
            break
        name = xw.Range( f'C{i}' ).value
        short_name = xw.Range( f'D{i}' ).value
        sql = f'SELECT [name] FROM [JJCost_Supplier2] WHERE [code]={trn( code )}'
        c.execute( sql )
        rr = c.fetchall()
        if len( rr ) < 1:
            sql = f'INSERT INTO [JJCost_Supplier2] VALUES ({trn( code )}, {trn( name )}, {trn( short_name )})'
            c.execute( sql )
    print( '���Supplier����䡣' )

r = input( 'build purchase bill? n or y?' )

if r == 'y' or r == 'Y':
    r = input( 'ZD data? n or y?' )
    dd = 'JJCost_ErpPurchase'
    if r != 'y' and r != 'Y':
        dd = 'JJCost_JL_ErpPurchase'
    for i in range( 2, 20000 ):
        bill = xw.Range( f'A{i}' ).value
        if bill is None or str.isspace( bill ):
            break
        supplier = xw.Range( f'B{i}' ).value
        c.execute( f'SELECT [code] FROM [JJCost_Supplier2] WHERE [name]=\'{supplier.strip()}\'' )
        rr = c.fetchone()
        if rr is None:
            continue
        s_code = rr[0]
        erp_code = xw.Range( f'E{i}' ).value
        when = xw.Range( f'Q{i}' ).value
        qty = xw.Range( f'I{i}' ).value
        tax_rate = xw.Range( f'C{i}' ).value
        unit_price_with_tax = xw.Range( f'P{i}' ).value
        unit_price_no_tax = None
        if unit_price_with_tax is not None and unit_price_with_tax != '.':
            tt = 1.0
            if tax_rate is not None:
                t = float( tax_rate )
                tt += t / 100.0
            unit_price_no_tax = float( unit_price_with_tax ) / tt
        sql = f'SELECT [erp_code] FROM [{dd}] WHERE [erp_code]={trn( erp_code )} AND [bill_nr]={trn( bill )}'
        c.execute( sql )
        rr = c.fetchall()
        if len( rr ) < 1:
            sql = f'INSERT INTO [{dd}] VALUES ({trn( erp_code )}, {trn( bill )}, {trn( when )}, {trn( s_code )}, ' \
                  f'{trn2( qty )}, {trn2( tax_rate )}, {trn2( unit_price_no_tax )})'
        else:
            sql = f'UPDATE [{dd}] SET [when_]={trn( when )}, [supplier]={trn( s_code )}, [qty]={trn2( qty )}, ' \
                  f'[tax_rate]={trn2( tax_rate )}, [unit_price_not_tax]={trn2( unit_price_no_tax )} ' \
                  f'WHERE [erp_code]={trn( erp_code )} AND [bill_nr]={trn( bill )}'
        c.execute( sql )
        print( sql )
    print( '���Bill����䡣' )

r = input( 'fill supplier? n or y?' )
if r == 'y' or r == 'Y':
    cc = int( input( 'max row number:' ) )
    xw.Range( 'N1' ).value = 'ZD Supplier'
    xw.Range( 'O1' ).value = 'ZD unit price'
    xw.Range( 'P1' ).value = 'JL Supplier'
    xw.Range( 'Q1' ).value = 'JL unit price'
    ccc = 1
    while True:
        if ccc > 2:
            break
        dd = 'JJCost_ErpPurchase'
        c_col = 'H'
        s_col = 'N'
        u_p_col = 'O'
        if ccc == 2:
            dd = 'JJCost_JL_ErpPurchase'
            c_col = 'G'
            s_col = 'P'
            u_p_col = 'Q'
        for i in range( 2, cc + 1 ):
            erp_code = xw.Range( f'{c_col}{i}' ).value
            if erp_code is None or str.isspace( erp_code ):
                continue
            sql = f'SELECT [supplier], [unit_price_not_tax] FROM [{dd}] WHERE [erp_code]={trn( erp_code )} ORDER BY [when_] DESC'
            c.execute( sql )
            rr = c.fetchone()
            if rr is not None:
                sql = f'SELECT [name] FROM [JJCost_Supplier2] WHERE [code]={trn( rr[0] )}'
                c.execute( sql )
                rrr = c.fetchone()
                u_p = rr[1]
                ss = 'no_found'
                if rrr is not None:
                    ss = rrr[0]
                xw.Range( f'{s_col}{i}' ).value = ss
                xw.Range( f'{u_p_col}{i}' ).value = u_p
        ccc += 1

    print( '��ɹ�Ӧ�̵���䡣' )

con.commit()

c.close()
con.close()
