# coding=gbk

import datetime
import shutil
import sqlite3
import time

import pyodbc


def CN(dd):
    """ 将多组数据进行整理 """
    return dd


def CNN(dd):
    """ 将多组数据进行整理 """
    values = []
    for d in dd:
        if d is None:
            values.append( 'NULL' )
        else:
            if type( d ) == str:
                values.append( f'\"{d}\"' )
            elif isinstance( d, datetime.datetime ):
                values.append( f'\"{d.strftime( "%Y-%m-%d %H:%M:%S" )}\"' )
            else:
                values.append( str( d ) )
    if len( values ) > 0:
        return ','.join( values )
    return ''


db_file = 'greatoo_jj_3.db'

user_db_name = input( '请输入数据库名称（直接按Enter接受默认名称）：' )
print( '数据库文件名称为：' )
if user_db_name == '':
    print( 'greatoo_jj_3.db。' )
else:
    print( user_db_name )
    db_file = user_db_name

# 复制文件
original_db_file = r"D:\__resource\Greatoo_JJ.db"
dest_db_file = f'.\\{db_file}'
shutil.copyfile( original_db_file, dest_db_file )

conn = pyodbc.connect('DRIVER={SQL Server};SERVER=191.1.6.103;UID=_user;PWD=123456;DATABASE=Greatoo_JJ_Database')
c = conn.cursor()

t_conn = sqlite3.connect( db_file )
t_c = t_conn.cursor()

print( '开始填充数据……' )
begin_time = datetime.datetime.now()

# dbo_Groups
c.execute( 'SELECT * FROM [dbo].[Groups]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [dbo_Groups] VALUES ({CNN( r )})' )
print( '完成 dbo_Groups' )

# dbo_T_City
c.execute( 'SELECT * FROM [dbo].[T_City]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [dbo_T_City] VALUES ({CNN( r )})' )
print( '完成 dbo_T_City' )

# dbo_T_Province
c.execute( 'SELECT * FROM [dbo].[T_Province]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [dbo_T_Province] VALUES ({CNN( r )})' )
print( '完成 dbo_T_Province' )

# dbo_Users
c.execute( 'SELECT * FROM [dbo].[Users]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [dbo_Users] VALUES ({CNN( r )})' )
print( '完成 dbo_Users' )

# JJCom_Competence
c.execute( 'SELECT * FROM [JJCom].[Competence]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCom_Competence] VALUES ({CNN( r )})' )
print( '完成 JJCom_Competence' )

# JJCom_Department
c.execute( 'SELECT * FROM [JJCom].[Department]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCom_Department] VALUES ({CNN( r )})' )
print( '完成 JJCom_Department' )

# JJCom_HR
c.execute( 'SELECT * FROM [JJCom].[HR]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCom_HR] VALUES ({CNN( r )})' )
print( '完成 JJCom_HR' )

# JJPart_PartGroup
c.execute( 'SELECT * FROM [JJPart].[PartGroup]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJPart_PartGroup] VALUES ({CNN( r )})' )
print( '完成 JJPart_PartGroup' )

# JJPart_PartType
c.execute( 'SELECT * FROM [JJPart].[PartType]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJPart_PartType] VALUES ({CNN( r )})' )
print( '完成 JJPart_PartType' )

# JJPart_PartStatus
c.execute( 'SELECT * FROM [JJPart].[PartStatus]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJPart_PartStatus] VALUES ({CNN( r )})' )
print( '完成 JJPart_PartStatus' )

# JJPart_Part
try:
    c.execute( 'SELECT * FROM [JJPart].[Part]' )
    rs = c.fetchall()
    for r in rs:
        sql = f'INSERT INTO [JJPart_Part] VALUES (?,?,?,?,?,?,?,?,?,?,?)'
        t_c.execute( sql, CN( r ) )
    print( '完成 JJPart_Part' )
except Exception as ex:
    raise ex

# JJCom_Tag
c.execute( 'SELECT * FROM [JJCom].[Tag]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCom_Tag] VALUES ({CNN( r )})' )
print( '完成 JJCom_Tag' )

# JJCom_PartTag
c.execute( 'SELECT * FROM [JJCom].[PartTag]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCom_PartTag] VALUES ({CNN( r )})' )
print( '完成 JJCom_PartTag' )

# JJCom_PersonLimit
c.execute( 'SELECT * FROM [JJCom].[PersonLimit]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCom_PersonLimit] VALUES ({CNN( r )})' )
print( '完成 JJCom_PersonLimit' )

# JJCom_WorkIn
c.execute( 'SELECT * FROM [JJCom].[WorkIn]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCom_WorkIn] VALUES ({CNN( r )})' )
print( '完成 JJCom_WorkIn' )

# JJCost_PurchaseLink
c.execute( 'SELECT * FROM [JJCost].[PurchaseLink]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_PurchaseLink] VALUES ({CNN( r )})' )
print( '完成 JJCost_Supplier' )

# JJCost_Supplier
c.execute( 'SELECT * FROM [JJCost].[Supplier]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_Supplier] VALUES ({CNN( r )})' )
print( '完成 JJCost_Supplier' )

# JJCost_Contact
c.execute( 'SELECT * FROM [JJCost].[Contact]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_Contact] VALUES ({CNN( r )})' )
print( '完成 JJCost_Contact' )

# JJCost_Quotation
try:
    c.execute( 'SELECT * FROM [JJCost].[Quotation]' )
    rs = c.fetchall()
    for r in rs:
        sql = f'INSERT INTO [JJCost_Quotation] VALUES ({CNN( r )})'
        t_c.execute( sql )
    print( '完成 JJCost_Quotation' )
except Exception as ex:
    raise ex

# JJCost_GoodsReceiptBill
c.execute( 'SELECT * FROM [JJCost].[GoodsReceiptBill]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_GoodsReceiptBill] VALUES ({CNN( r )})' )
print( '完成 JJCost_GoodsReceiptBill' )

# JJCost_Invoice
c.execute( 'SELECT * FROM [JJCost].[Invoice]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_Invoice] VALUES ({CNN( r )})' )
print( '完成 JJCost_Invoice' )

# JJCost_PayRecord
c.execute( 'SELECT * FROM [JJCost].[PayRecord]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_PayRecord] VALUES ({CNN( r )})' )
print( '完成 JJCost_PayRecord' )

# JJCost_PurchaseStatus
c.execute( 'SELECT * FROM [JJCost].[PurchaseStatus]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_PurchaseStatus] VALUES ({CNN( r )})' )
print( '完成 JJCost_PurchaseStatus' )

# JJCost_Quotation2FileLink
c.execute( 'SELECT * FROM [JJCost].[Quotation2FileLink]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_Quotation2FileLink] VALUES ({CNN( r )})' )
print( '完成 JJCost_Quotation2FileLink' )

# JJCost_QuotationItem
c.execute( 'SELECT * FROM [JJCost].[QuotationItem]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_QuotationItem] VALUES ({CNN( r )})' )
print( '完成 JJCost_QuotationItem' )

# JJCost_ReceiptListItem
c.execute( 'SELECT * FROM [JJCost].[ReceiptListItem]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_ReceiptListItem] VALUES ({CNN( r )})' )
print( '完成 JJCost_ReceiptListItem' )

# JJCost_Supplier2
c.execute( 'SELECT * FROM [JJCost].[Supplier2]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_Supplier2] VALUES ({CNN( r )})' )
print( '完成 JJCost_Supplier2' )

# JJCost_TaxRate
c.execute( 'SELECT * FROM [JJCost].[TaxRate]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJCost_TaxRate] VALUES ({CNN( r )})' )
print( '完成 JJCost_TaxRate' )

# JJPart_FileRelation
c.execute( 'SELECT * FROM [JJPart].[FileRelation]' )
rs = c.fetchall()
for r in rs:
    sql = 'INSERT INTO [JJPart_FileRelation] VALUES ({0}, {1}, \'{2}\', NULL)'.format( r[0], r[1], r[2] )
    t_c.execute( sql )
print( '完成 JJPart_FileRelation' )

# JJPart_IdenticalPart
c.execute( 'SELECT * FROM [JJPart].[IdenticalPart]' )
rs = c.fetchall()
for r in rs:
    sql = f'INSERT INTO [JJPart_IdenticalPart] VALUES (?,?,?,?)'
    t_c.execute( sql, CN( r ) )
print( '完成 JJPart_IdenticalPart' )

# JJPart_IdenticalPartLink
c.execute( 'SELECT * FROM [JJPart].[IdenticalPartLink]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJPart_IdenticalPartLink] VALUES ({CNN( r )})' )
print( '完成 JJPart_IdenticalPartLink' )

# JJPart_PartOwner
c.execute( 'SELECT * FROM [JJPart].[PartOwner]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJPart_PartOwner] VALUES ({CNN( r )})' )
print( '完成 JJPart_PartOwner' )

# JJPart_PartRelation
c.execute( 'SELECT * FROM [JJPart].[PartRelation]' )
rs = c.fetchall()
for r in rs:
    tt = CN( r )
    sql = \
        f'INSERT INTO [JJPart_PartRelation] VALUES (?,?,?,?,?,?,?,?,?)'
    t_c.execute( sql, tt )
print( '完成 JJPart_PartRelation' )

# JJPart_PartThumbnail
c.execute( 'SELECT * FROM [JJPart].[PartThumbnail]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( 'INSERT INTO [JJPart_PartThumbnail] VALUES ({0}, ?, {1})'.format( r[0], r[2] ), (r[1],) )
print( '完成 JJPart_PartThumbnail' )

# JJPart_UnresolvedPdfLink
c.execute( 'SELECT * FROM [JJPart].[UnresolvedPdfLink]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJPart_UnresolvedPdfLink] VALUES ({CNN( r )})' )
print( '完成 JJPart_UnresolvedPdfLink' )

# JJPart_ZdErp
c.execute( 'SELECT * FROM [JJPart].[ZdErp]' )
rs = c.fetchall()
for r in rs:
    sql = f'INSERT INTO [JJPart_ZdErp] VALUES (?,?,?)'
    t_c.execute( sql, CN( r ) )
print( '完成 JJPart_ZdErp' )

# JJPart_JlErp
unit_list = (
    "付", "套", "件", "个", "片", "块", "台", "条", "支", "粒", "公斤", "米",
    "升", "吨", "盒", "袋", "根", "桶", "张", "只", "瓶", "箱", "双", "卷",
    "包", "把", "立方米", "平方厘米", "组", "圈", "平方米", "对", "立方厘米", "斤")
jl_con = pyodbc.connect('DRIVER={SQL Server};Server=191.1.0.4;UID=ops_dev;PWD=123@greatoo;DATABASE=JL_Mould')
jl_c = jl_con.cursor()
sql = f'SELECT [ITEM_NO], [item_describe], [UNIT] FROM [dbo].[ops_v_item]'
jl_c.execute( sql )
rs = jl_c.fetchall()
for r in rs:
    if r is None:
        continue
    unit_code = -1
    if type( r[2] ) == int:
        unit_code = r[2]
    elif type( r[2] ) == str and len( r[2] ) > 0:
        try:
            unit_code = int( r[2].lstrip( '0' ) )
        except:
            unit_code = -1
    if unit_code > 33 or r[1] is None:
        continue
    unit_str = '件' if unit_code < 0 else unit_list[unit_code - 1]
    sql = f'INSERT INTO [JJPart_JlErp] VALUES (?,?,?)'
    t_c.execute( sql, [r[0], r[1], unit_str] )
print( '完成 JJPart_JlErp' )

# JJProduce_ProductType
c.execute( 'SELECT * FROM [JJProduce].[ProductType]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJProduce_ProductType] VALUES ({CNN( r )})' )
print( '完成 JJProduce_ProductType' )

# JJProduce_ProductStatus
c.execute( 'SELECT * FROM [JJProduce].[ProductStatus]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJProduce_ProductStatus] VALUES ({CNN( r )})' )
print( '完成 JJProduce_ProductStatus' )

# JJProduce_Product
c.execute( 'SELECT * FROM [JJProduce].[Product]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJProduce_Product] VALUES ({CNN( r )})' )
print( '完成 JJProduce_Product' )

# JJProduce_ProduceTask
c.execute( 'SELECT * FROM [JJProduce].[ProduceTask]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJProduce_ProduceTask] VALUES ({CNN( r )})' )
print( '完成 JJProduce_ProduceTask' )

# JJProduce_ProductProperty
c.execute( 'SELECT * FROM [JJProduce].[ProductProperty]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJProduce_ProductProperty] VALUES ({CNN( r )})' )
print( '完成 JJProduce_ProductProperty' )

# JJProduce_Tag
c.execute( 'SELECT * FROM [JJProduce].[Tag]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJProduce_Tag] VALUES ({CNN( r )})' )
print( '完成 JJProduce_Tag' )

# JJProduce_ProductTag
c.execute( 'SELECT * FROM [JJProduce].[ProductTag]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJProduce_ProductTag] VALUES ({CNN( r )})' )
print( '完成 JJProduce_ProductTag' )

# JJProduce_StatusChangedRecord
c.execute( 'SELECT * FROM [JJProduce].[StatusChangedRecord]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJProduce_StatusChangedRecord] VALUES ({CNN( r )})' )
print( '完成 JJProduce_StatusChangedRecord' )

# JJSale_Company
c.execute( 'SELECT * FROM [JJSale].[Company]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJSale_Company] VALUES ({CNN( r )})' )
print( '完成 JJSale_Company' )

# JJSale_Contact
c.execute( 'SELECT * FROM [JJSale].[Contact]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJSale_Contact] VALUES ({CNN( r )})' )
print( '完成 JJSale_Contact' )

# JJSale_Contract
c.execute( 'SELECT * FROM [JJSale].[Contract]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJSale_Contract] VALUES ({CNN( r )})' )
print( '完成 JJSale_Contract' )

# JJSale_ProductSale
c.execute( 'SELECT * FROM [JJSale].[ProductSale]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJSale_ProductSale] VALUES ({CNN( r )})' )
print( '完成 JJSale_ProductSale' )

# JJSale_Shipment
c.execute( 'SELECT * FROM [JJSale].[Shipment]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJSale_Shipment] VALUES ({CNN( r )})' )
print( '完成 JJSale_Shipment' )

# JJSale_ProductShipped
c.execute( 'SELECT * FROM [JJSale].[ProductShipped]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJSale_ProductShipped] VALUES ({CNN( r )})' )
print( '完成 JJSale_ProductShipped' )

# JJSale_ServiceRecord
c.execute( 'SELECT * FROM [JJSale].[ServiceRecord]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJSale_ServiceRecord] VALUES ({CNN( r )})' )
print( '完成 JJSale_ServiceRecord' )

# JJStorage_ErpPickingRecord
c.execute( 'SELECT * FROM [JJStorage].[ErpPickingRecord]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_ErpPickingRecord] VALUES ({CNN( r )})' )
print( '完成 JJStorage_ErpPickingRecord' )

# JJStorage_ErpPickingLink
c.execute( 'SELECT * FROM [JJStorage].[ErpPickingLink]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_ErpPickingLink] VALUES ({CNN( r )})' )
print( '完成 JJStorage_ErpPickingLink' )

# JJStorage_ErpPickingType
c.execute( 'SELECT * FROM [JJStorage].[ErpPickingType]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_ErpPickingType] VALUES ({CNN( r )})' )
print( '完成 JJStorage_ErpPickingType' )

# JJStorage_ErpPickingTypeLink
c.execute( 'SELECT * FROM [JJStorage].[ErpPickingTypeLink]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_ErpPickingTypeLink] VALUES ({CNN( r )})' )
print( '完成 JJStorage_ErpPickingTypeLink' )

# JJStorage_KbnSupplyBill
c.execute( 'SELECT * FROM [JJStorage].[KbnSupplyBill]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_KbnSupplyBill] VALUES ({CNN( r )})' )
print( '完成 JJStorage_KbnSupplyBill' )

# JJStorage_KbnSupplyItem
c.execute( 'SELECT * FROM [JJStorage].[KbnSupplyItem]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_KbnSupplyItem] VALUES ({CNN( r )})' )
print( '完成 JJStorage_KbnSupplyItem' )

# JJStorage_OperationBill
c.execute( 'SELECT * FROM [JJStorage].[OperationBill]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_OperationBill] VALUES ({CNN( r )})' )
print( '完成 JJStorage_OperationBill' )

# JJStorage_StoringType
c.execute( 'SELECT * FROM [JJStorage].[StoringType]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_StoringType] VALUES ({CNN( r )})' )
print( '完成 JJStorage_StoringType' )

# JJStorage_PartStoring
c.execute( 'SELECT * FROM [JJStorage].[PartStoring]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_PartStoring] VALUES ({CNN( r )})' )
print( '完成 JJStorage_PartStoring' )

# JJStorage_Storing
c.execute( 'SELECT * FROM [JJStorage].[Storing]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_Storing] VALUES ({CNN( r )})' )
print( '完成 JJStorage_Storing' )

# JJStorage_Storing2
c.execute( 'SELECT * FROM [JJStorage].[Storing2]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_Storing2] VALUES ({CNN( r )})' )
print( '完成 JJStorage_Storing2' )

# JJStorage_SupplyRecordProcess
c.execute( 'SELECT * FROM [JJStorage].[SupplyRecordProcess]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_SupplyRecordProcess] VALUES ({CNN( r )})' )
print( '完成 JJStorage_SupplyRecordProcess' )

# JJStorage_SupplyOperationRecord
c.execute( 'SELECT * FROM [JJStorage].[SupplyOperationRecord]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_SupplyOperationRecord] VALUES ({CNN( r )})' )
print( '完成 JJStorage_SupplyOperationRecord' )

# JJStorage_SupplyRecordLink
c.execute( 'SELECT * FROM [JJStorage].[SupplyRecordLink]' )
rs = c.fetchall()
for r in rs:
    t_c.execute( f'INSERT INTO [JJStorage_SupplyRecordLink] VALUES ({CNN( r )})' )
print( '完成 JJStorage_SupplyRecordLink' )

# dbo_DatabaseVersion	
end_time = datetime.datetime.now()
time_string = end_time.strftime( "%Y-%m-%d %H:%M:%S" )
t_c.execute( f'INSERT INTO [dbo_DatabaseVersion] VALUES (\"{time_string}\")' )
print( '完成 dbo_DatabaseVersion' )

t_conn.commit()
t_c.close()
t_conn.close()

delta = end_time - begin_time
delta_gm_time = time.gmtime( delta.total_seconds() )
duration_str = time.strftime( "%H:%M:%S", delta_gm_time )
print( f'完成。运行时长：{duration_str}' )
