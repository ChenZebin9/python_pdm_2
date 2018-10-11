""" 建立sqlite数据库文件的表结构 """
import sqlite3


class SqliteBuilder:

    def __init__(self, file_path):
        self.db = sqlite3.connect(file_path)
        c = self.db.cursor()

        c.execute('''
        CREATE TABLE Part_Group
        (
            groupName VARCHAR(20) PRIMARY KEY
        )
        ''')
        c.execute('''
        CREATE TABLE Part_Status
        (
            statusId TINYINT PRIMARY KEY,
            statusDescription VARCHAR(50) NOT NULL
        )
        ''')
        c.execute('''
        CREATE TABLE Part_Type
        (
            typeId TINYINT PRIMARY KEY,
            typeName VARCHAR(50) NOT NULL,
            groupName VARCHAR(20) NOT NULL,
            FOREIGN KEY (groupName) REFERENCES Part_Group (groupName)
        )
        ''')
        c.execute('''
        CREATE TABLE Part_Tag
        (
            tag VARCHAR(20) PRIMARY KEY,
            upperTag VARCHAR(20),
            FOREIGN KEY (upperTag) REFERENCES Part_Tag (tag)
        )
        ''')
        c.execute('''
        CREATE TABLE Part_IdenticalPart
        (
            id INT PRIMARY KEY,
            description TEXT NOT NULL,
            status TINYINT NOT NULL,
            code NCHAR(20),
            FOREIGN KEY (status) REFERENCES Part_Status (statusId)
        )
        ''')
        c.execute('''
        CREATE TABLE Part_Part
        (
            partId INT PRIMARY KEY,
            status TINYINT NOT NULL,
            type TINYINT NOT NULL,
            description1 VARCHAR(50) NOT NULL,
            description2 VARCHAR(70),
            description3 VARCHAR(50),
            description4 VARCHAR(50) NOT NULL,
            description5 VARCHAR(130),
            description6 VARCHAR(20),
            comment TEXT,
            groupName VARCHAR(20) NOT NULL,
            FOREIGN KEY (groupName) REFERENCES Part_Group (groupName),
            FOREIGN KEY (status) REFERENCES Part_Status (statusId),
            FOREIGN KEY (type) REFERENCES Part_Type (typeId)
        )
        ''')
        c.execute('''
        CREATE TABLE Part_PartRelation
        (
            partRelationId INT PRIMARY KEY,
            parentPart INT NOT NULL,
            childPart INT NOT NULL,
            qty REAL NOT NULL,
            unitString VARCHAR(20) NOT NULL,
            number INT NOT NULL,
            comment TEXT NULL,
            actualQty REAL NOT NULL,
            storingLink TINYINT NOT NULL DEFAULT 0,
            FOREIGN KEY (parentPart) REFERENCES Part_Part (partId),
            FOREIGN KEY (childPart) REFERENCES Part_Part (partId)
            CHECK (unitString='件' OR unitString='米' OR unitString='千克' OR unitString='平方厘米' OR unitString='升')
        )
        ''')
        c.execute('''
        CREATE TABLE Part_FileRelation
        (
            id INT PRIMARY KEY,
            partId INT NOT NULL,
            filePath VARCHAR(256) NOT NULL,
            FOREIGN KEY (partId) REFERENCES Part_Part (partId)
        )
        ''')
        c.execute('''
        CREATE TABLE Part_IdenticalPart_Link
        (
            id INT PRIMARY KEY,
            functionId INT NOT NULL,
            partId INT NOT NULL,
            evaluate TINYINT NOT NULL,
            qtyProp REAL NOT NULL DEFAULT 1.0,
            FOREIGN KEY (partId) REFERENCES Part_Part (partId),
            FOREIGN KEY (functionId) REFERENCES Part_IdenticalPart (id),
            CHECK (evaluate>0 AND evaluate<=10)
        )
        ''')


if __name__ == '__main__':
    SqliteBuilder('tttt.sqlite3')
