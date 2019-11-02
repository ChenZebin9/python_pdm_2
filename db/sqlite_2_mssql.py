# coding=gbk
import pymssql
import sqlite3


def get_zd_erp_data(database):
    """ 从SQLite数据库读取中德ERP的数据 """
    c = database.cursor()
    c.execute( 'SELECT * FROM part_info' )
    rs = c.fetchall()
    result = []
    for r in rs:
        result.append( (r[0], r[1], r[2]) )
    c.close()
    return result


def push_zd_erp_data(database, all_data, create_table=False):
    """ 将数据输出到MSSQL数据库中 """
    c = database.cursor()
    if create_table:
        c.execute( '''
        CREATE TABLE JJPart.ZdErp
        (
            ErpId char(13) NOT NULL,
            Description varchar(256) NOT NULL,
            Unit varchar(16) NOT NULL,
            CONSTRAINT pk_zd_erp PRIMARY KEY (ErpId)
        )
        ''' )
    for d in all_data:
        c.execute( f'INSERT INTO [JJPart].[ZdErp] VALUES (\'{d[0]}\', \'{d[1]}\', \'{d[2]}\')' )
    database.commit()


def create_product_tables(database):
    """ 在MSSQL中创建 Product 的相关数据表 """
    c = database.cursor()
    c.execute( '''
    CREATE TABLE JJSale.Company
    (
        CompanyCode VARCHAR(128) PRIMARY KEY,
        Name VARCHAR(512) NOT NULL,
        ShortName VARCHAR(20) NOT NULL,
        Address VARCHAR(512) NOT NULL,
        Phone VARCHAR(128),
        Contact VARCHAR(128),
        wayTo TEXT
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJSale.Contact
    (
        Company VARCHAR(128) NOT NULL,
        Name VARCHAR(512) NOT NULL,
        Phone VARCHAR(128),
        Email VARCHAR(256),
        Comment TEXT,
        PRIMARY KEY (Company, Name),
        FOREIGN KEY (Company) REFERENCES JJSale.Company (CompanyCode)
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJCom.HR
    (
        PersonCode CHAR(7) NOT NULL PRIMARY KEY,
        Name VARCHAR(50) NOT NULL,
        Comment TEXT
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJProduce.ProductStatus
    (
        StatusName VARCHAR(20) PRIMARY KEY,
        StatusOrder INT NOT NULL,
        comment TEXT
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJProduce.ProductType
    (
        TypeShortName VARCHAR(20) PRIMARY KEY,
        TypeName VARCHAR(256) NOT NULL
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJProduce.Product
    (
        ProductId VARCHAR(50) PRIMARY KEY,
        ProductType VARCHAR(20) NOT NULL,
        ActualStatus VARCHAR(20),
        LastStatusChangedDate DATETIME,
        DeclaredStatus VARCHAR(20),
        DeclaredFinishedDate VARCHAR(20),
        CostType VARCHAR(20) NOT NULL DEFAULT '配件',
        ProductComment TEXT,
        StatusComment TEXT,
        Config TEXT,
        ParentProduct VARCHAR(50),
        FOREIGN KEY (ProductType) REFERENCES JJProduce.ProductType (TypeShortName),
        FOREIGN KEY (ActualStatus) REFERENCES JJProduce.ProductStatus (StatusName),
        FOREIGN KEY (DeclaredStatus) REFERENCES JJProduce.ProductStatus (statusName),
        FOREIGN KEY (ParentProduct) REFERENCES JJProduce.Product (ProductId),
        CHECK (CostType='配件' OR CostType='工具' OR CostType='低耗' OR CostType='未确定')
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJProduce.ProductProperty
    (
        ProductId VARCHAR(50) NOT NULL,
        PropertyName VARCHAR(50) NOT NULL,
        PropertyValue TEXT,
        PropertyIndex TINYINT NOT NULL DEFAULT 1,
        PRIMARY KEY(ProductId, PropertyName),
        FOREIGN KEY(ProductId) REFERENCES JJProduce.Product (ProductId)
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJProduce.Tag
    (
        Id INT PRIMARY KEY,
        TagName TEXT NOT NULL,
        ParentId INT REFERENCES JJProduce.Tag (Id),
        SortIndex INT NOT NULL DEFAULT 1
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJProduce.ProductTag
    (
        ProductId VARCHAR(50) REFERENCES JJProduce.Product (ProductId) NOT NULL,
        TagId INT REFERENCES JJProduce.Tag (Id) NOT NULL,
        CONSTRAINT pk_product_tag PRIMARY KEY (ProductId, TagId)
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJSale.Contract
    (
        ContractCode VARCHAR(128) PRIMARY KEY,
        ContractDate DATETIME,
        Company VARCHAR(128) NOT NULL,
        TerminalCompany VARCHAR(128),
        FOREIGN KEY (Company) REFERENCES JJSale.Company (CompanyCode),
        FOREIGN KEY (TerminalCompany) REFERENCES JJSale.Company (CompanyCode)
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJSale.ProductSale
    (
        Product VARCHAR(50) NOT NULL PRIMARY KEY,
        Contract VARCHAR(128) NOT NULL,
        Comment TEXT,
        FOREIGN KEY (Product) REFERENCES JJProduce.Product (ProductId),
        FOREIGN KEY (Contract) REFERENCES JJSale.Contract (ContractCode)
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJSale.Shipment
    (
        BillNumber VARCHAR(20) PRIMARY KEY,
        Source VARCHAR(128),
        Dest VARCHAR(128),
        _when DATETIME NOT NULL,
        Comment TEXT,
        FOREIGN KEY (Source) REFERENCES JJSale.Company (CompanyCode),
        FOREIGN KEY (Dest) REFERENCES JJSale.Company (CompanyCode)
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJSale.ProductShipped
    (
        Shipment VARCHAR(20) NOT NULL,
        Product VARCHAR(50) NOT NULL,
        PRIMARY KEY (Shipment, Product),
        FOREIGN KEY (Product) REFERENCES JJProduce.Product (ProductId),
        FOREIGN KEY (Shipment) REFERENCES JJSale.Shipment (BillNumber)
    );
    ''' )
    c.execute( '''
    CREATE TABLE JJSale.ServiceRecord
    (
        ServiceId VARCHAR(50) NOT NULL PRIMARY KEY,
        ProductId VARCHAR(50),
        ServiceDate DATETIME,
        Operator CHAR(7),
        Description TEXT,
        FOREIGN KEY (ProductId) REFERENCES JJProduce.Product (ProductId),
        FOREIGN KEY (Operator) REFERENCES JJCom.HR (PersonCode)
    );
    ''' )
    # MSSQL 的视图不能使用 ORDER BY
    c.execute( '''
    CREATE VIEW [JJSale].[ShipmentDetail]
    AS SELECT [p].[ProductId], [p].[ProductType], [p].[ProductComment], [s].[BillNumber],
    [c].[Name] AS [FromWhere], [c_1].[Name] AS [ToWhere], [s].[_when] AS [When]
    FROM [JJProduce].[Product] AS [p] INNER JOIN([JJSale].[ProductShipped] AS [sp] LEFT JOIN
    [JJSale].[Shipment] AS [s] ON [sp].[Shipment] = [s].[BillNumber]) ON [p].[ProductId] = [sp].[Product] LEFT JOIN
    [JJSale].[Company] AS [c] ON [s].[Source] = [c].[CompanyCode] LEFT JOIN
    [JJSale].[Company] AS [c_1] ON [s].[Dest] = [c_1].[CompanyCode];
    ''' )
    c.execute( '''
    CREATE VIEW [JJSale].[SoldOutDetail]
    AS SELECT [p].[ProductId], [p].[ProductType], [p].[ProductComment], [p].[Config], [p].[StatusComment],
    [s].[ContractCode], [s].[ContractDate], [c].[Name] AS [ContractCompany], [c_1].[name] AS [TerminalCompany]
    FROM ([JJProduce].[Product] AS [p] INNER JOIN ([JJSale].[Company] AS [c] INNER JOIN
    ([JJSale].[ProductSale] AS [sp] INNER JOIN [JJSale].[Contract] AS [s] ON [sp].[Contract] = [s].[ContractCode])
    ON [c].[CompanyCode] = [s].[Company]) ON [p].[ProductId] = [sp].[Product]) LEFT JOIN
    [JJSale].[Company] AS [c_1] ON [s].[TerminalCompany] = [c_1].[CompanyCode];
    ''' )
    database.commit()


def fill_product_tables(data_from, data_to):
    c_f = data_from.cursor()
    c_t = data_to.cursor()

    c_f.execute( 'SELECT * FROM Customer_Company' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute(
            f'INSERT INTO JJSale.Company VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )},{ff( r[3] )},{ff( r[4] )},'
            f'{ff( r[5] )},{ff( r[6] )})' )

    c_f.execute( 'SELECT * FROM Customer_Contact' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute(
            f'INSERT INTO JJSale.Contact VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )},{ff( r[3] )},{ff( r[4] )})' )

    c_f.execute( 'SELECT * FROM HR_Employee' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute( f'INSERT INTO JJCom.HR VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )})' )

    c_f.execute( 'SELECT * FROM Product_Status' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute( f'INSERT INTO JJProduce.ProductStatus VALUES ({ff( r[0] )}, {r[1]},{ff( r[2] )})' )

    c_f.execute( 'SELECT * FROM Product_Type' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute( f'INSERT INTO JJProduce.ProductType VALUES ({ff( r[0] )},{ff( r[1] )})' )

    c_f.execute( 'SELECT DISTINCT parentProduct FROM Product_Product WHERE parentProduct IS NOT NULL' )
    rs = c_f.fetchall()
    temp = []
    for r in rs:
        temp.append( r[0] )
    for t in temp:
        c_f.execute( 'SELECT * FROM Product_Product WHERE productId=\'{0}\''.format( t ) )
        rs = c_f.fetchall()
        insert_product_record( rs[0], c_t )
    c_f.execute( 'SELECT * FROM Product_Product' )
    rs = c_f.fetchall()
    for r in rs:
        try:
            insert_product_record( r, c_t )
        except:
            print( '已有记录了。' )

    c_f.execute( 'SELECT * FROM Product_Property' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute( f'INSERT INTO JJProduce.ProductProperty VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )},{r[3]})' )

    c_f.execute( 'SELECT * FROM Tag' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute( f'INSERT INTO JJProduce.Tag VALUES ({r[0]}, {ff( r[1] )},{fi( r[2] )}, {r[3]})' )
    c_f.execute( 'SELECT * FROM Product_Tag' )
    rs = c_f.fetchall()
    for r in rs:
        sql = f'INSERT INTO JJProduce.ProductTag VALUES ({ff( r[0] )}, {r[1]})'
        c_t.execute( sql )

    c_f.execute( 'SELECT * FROM Sale_Contract' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute( f'INSERT INTO JJSale.Contract VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )},{ff( r[3] )})' )

    c_f.execute( 'SELECT * FROM Sale_ProductSale' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute( f'INSERT INTO JJSale.ProductSale VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )})' )

    c_f.execute( 'SELECT * FROM Sale_Shipment' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute(
            f'INSERT INTO JJSale.Shipment VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )}, {ff( r[3] )},{ff( r[4] )})' )

    c_f.execute( 'SELECT * FROM Sale_ProductShipped' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute( f'INSERT INTO JJSale.ProductShipped VALUES ({ff( r[0] )}, {ff( r[1] )})' )

    c_f.execute( 'SELECT * FROM Service_Record' )
    rs = c_f.fetchall()
    for r in rs:
        c_t.execute(
            f'INSERT INTO JJSale.ServiceRecord VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )}, {ff( r[3] )},'
            f'{ff( r[4] )})' )

    data_to.commit()


def ff(value):
    # 规范化数据库的字符变量
    if value is None or len( value ) < 1:
        return 'NULL'
    else:
        return f'\'{value}\''


def fi(value):
    # 规范化数据库的整型变量
    if value is None:
        return 'NULL'
    else:
        return value


def insert_product_record(r, c):
    sql = f'INSERT INTO JJProduce.Product VALUES ({ff( r[0] )}, {ff( r[1] )},{ff( r[2] )},' \
        f'{ff( r[3] )},{ff( r[4] )},{ff( r[5] )},{ff( r[6] )},{ff( r[7] )}, {ff( r[8] )},' \
        f'{ff( r[9] )},{ff( r[10] )})'
    c.execute( sql )


if __name__ == '__main__':
    sqlite_database = sqlite3.connect( 'zd_erp.db' )
    mssql_database = pymssql.connect( server='191.1.6.103', user='sa', password='8893945',
                                      database='Greatoo_JJ_Database' )
    # rs = get_zd_erp_data( sqlite_database )
    # push_zd_erp_data( mssql_database, rs, False )
    # create_product_tables(mssql_database)
    sqlite_database.close()

    sqlite_database = sqlite3.connect( 'product_datas.db' )
    fill_product_tables( sqlite_database, mssql_database )
    mssql_database.close()
    sqlite_database.close()
