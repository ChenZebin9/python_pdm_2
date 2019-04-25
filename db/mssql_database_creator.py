""" 在Greatoo_JJ_Database创建Tag及其与Part的关联 """
import pymssql


class DatabaseCreator:

    def __init__(self):
        self.db = pymssql.connect( server='191.1.6.103', user='sa', password='8893945',
                                   database='Greatoo_JJ_Database' )
        c = self.db.cursor()

        c.execute( '''
        CREATE TABLE JJCom.Tag
        (
            id INT CONSTRAINT pk_tag PRIMARY KEY NOT NULL,
            tag_name TEXT NOT NULL,
            parent_id INT REFERENCES JJCom.Tag (id),
            sort_index INT NOT NULL DEFAULT 1
        )
        ''' )

        c.execute( '''
        CREATE TABLE JJCom.PartTag
        (
            part_id INT REFERENCES JJPart.Part (PartID) NOT NULL,
            tag_id INT REFERENCES JJCom.Tag (id) NOT NULL,
            CONSTRAINT pk_part_tag PRIMARY KEY (part_id, tag_id)
        )
        ''' )

        c.execute('''
        CREATE VIEW JJPart.PartTagView 
        SELECT JJPart.Part.PartID AS id, JJPart.Part.Description1 AS name, JJPart.Part.Description4 AS english_name, 
        JJPart.Part.Description2 AS description, JJPart.PartStatus.StatusDescrption AS status, 
        JJPart.Part.Comment, JJCom.PartTag.tag_id 
        FROM JJPart.Part INNER JOIN JJCom.PartTag ON JJPart.Part.PartID = JJCom.PartTag.part_id INNER JOIN
                      JJPart.PartStatus ON JJPart.Part.StatusType = JJPart.PartStatus.StatusID
        WHERE (JJPart.Part.StatusType = 90) OR (JJPart.Part.StatusType = 100)
        ORDER BY JJCom.PartTag.tag_id, id
        ''')

        self.db.commit()

    def close(self):
        self.db.close()


class DatabaseFiller:

    def __init__(self, database):
        self.__db = database
        c = self.__db.cursor()

        c.execute( 'DELETE FROM JJCom.PartTag' )
        c.execute( 'DELETE FROM JJCom.Tag' )
        c.execute( 'INSERT INTO JJCom.Tag VALUES (0, \'剪切板\', NULL, 1)' )
        index = 1
        c.execute( 'INSERT INTO JJCom.Tag VALUES ({0}, \'类别\', NULL, 1)'.format( index ) )
        classic_list_index = index
        c.execute('SELECT TypeName FROM JJPart.PartType')
        classic_list = c.fetchall()
        index += 1
        t_index = 1
        for ccc in classic_list:
            cc = ccc[0]
            c.execute(
                'INSERT INTO JJCom.Tag VALUES ({0}, \'{1}\', {2}, {3})'.format( index, cc, classic_list_index,
                                                                                t_index ) )
            t_index += 1
            c.execute( 'SELECT PartID FROM JJPart.Part WHERE PartType={0} AND StatusType>80'.format( index - 1 ) )
            rrs = c.fetchall()
            for rr in rrs:
                c.execute( 'INSERT INTO JJCom.PartTag VALUES ({0}, {1})'.format( rr[0], index ) )
            index += 1
        standard_index = index
        c.execute( 'INSERT INTO JJCom.Tag VALUES ({0}, \'标准\', NULL, 1)'.format( standard_index ) )
        index += 1
        brand_index = index
        c.execute( 'INSERT INTO JJCom.Tag VALUES ({0}, \'品牌\', NULL, 1)'.format( brand_index ) )
        index += 1
        c.execute( 'SELECT DISTINCT(Description3) FROM JJPart.Part WHERE StatusType>80 ORDER BY Description3' )
        rs = c.fetchall()
        t_index = 1
        tt_index = 1
        for r in rs:
            print( r )
            if r[0] is None:
                continue
            if str( r[0] ).startswith( 'GB' ) or str( r[0] ).startswith( 'DIN' ):
                c.execute(
                    'INSERT INTO JJCom.Tag VALUES ({0}, \'{1}\', {2}, {3})'
                    .format( index, r[0], standard_index, t_index ) )
                t_index += 1
            else:
                c.execute(
                    'INSERT INTO JJCom.Tag VALUES ({0}, \'{1}\', {2}, {3})'.format( index, r[0], brand_index,
                                                                                    tt_index ) )
                tt_index += 1
            c.execute( 'SELECT PartID FROM JJPart.Part WHERE Description3=\'{0}\''.format( r[0] ) )
            rrs = c.fetchall()
            for rr in rrs:
                c.execute( 'INSERT INTO JJCom.PartTag VALUES ({0}, {1})'.format( rr[0], index ) )
            index += 1
        c.execute( 'INSERT INTO JJCom.Tag VALUES ({0}, \'巨轮智能ERP物料编码\', NULL, 1)'.format( index ) )
        erp_num_index = index
        index += 1
        c.execute( 'SELECT DISTINCT(Description6) FROM JJPart.Part WHERE StatusType>80 ORDER BY Description6' )
        rs = c.fetchall()
        t_index = 1
        for r in rs:
            print( r )
            if r[0] is None:
                continue
            c.execute(
                'INSERT INTO JJCom.Tag VALUES ({0}, \'{1}\', {2}, {3})'.format( index, r[0], erp_num_index, t_index ) )
            t_index += 1
            c.execute( 'SELECT PartID FROM JJPart.Part WHERE Description6=\'{0}\''.format( r[0] ) )
            rrs = c.fetchall()
            for rr in rrs:
                c.execute( 'INSERT INTO JJCom.PartTag VALUES ({0}, {1})'.format( rr[0], index ) )
            index += 1
        c.execute( 'INSERT INTO JJCom.Tag VALUES ({0}, \'外部编码\', NULL, 1)'.format( index ) )
        foreign_code_index = index
        index += 1
        c.execute( 'SELECT DISTINCT(Description5) FROM JJPart.Part WHERE StatusType>80 ORDER BY Description5' )
        rs = c.fetchall()
        t_index = 1
        for r in rs:
            print( r )
            if r[0] is None or r[0] == '':
                continue
            c.execute(
                'INSERT INTO JJCom.Tag VALUES ({0}, \'{1}\', {2}, {3})'.format( index, r[0], foreign_code_index, t_index ) )
            t_index += 1
            c.execute( 'SELECT PartID FROM JJPart.Part WHERE Description5=\'{0}\''.format( r[0] ) )
            rrs = c.fetchall()
            for rr in rrs:
                c.execute( 'INSERT INTO JJCom.PartTag VALUES ({0}, {1})'.format( rr[0], index ) )
            index += 1

        self.__db.commit()


if __name__ == '__main__':
    creator = DatabaseCreator()
    filler = DatabaseFiller(creator.db)
    creator.close()
    print('All Done!')
