from db.DatabaseHandler import *
import pymssql


class MssqlHandler(DatabaseHandler):

    def __init__(self, server, database, user, password):
        self.__conn = pymssql.connect(server=server, user=user, password=password, database=database)
        self.__c = self.__conn.cursor()

    def get_parts(self, part_id=None, name=None, english_name=None, description=None):
        select_cmd = 'SELECT t.PartID AS id, t.Description1 AS name, t.Description4 AS english_name,' \
                     ' t.Description2 AS description, s.StatusDescrption AS status, t.Comment AS comment'
        from_database = 'FROM JJPart.Part AS t INNER JOIN JJPart.PartStatus AS s ON t.StatusType=s.StatusID'
        default_where = 't.StatusType=90 OR t.StatusType=100'
        if part_id is None and name is None and english_name is None and description is None:
            sql = '{0} {1} WHERE {2} ORDER BY t.PartID'.format(select_cmd, from_database, default_where)
        elif part_id is not None:
            sql = '{0} {1} WHERE {3} AND t.PartID={2}'.format(select_cmd, from_database, part_id, default_where)
        else:
            search_filter = ''
            if name is not None:
                search_filter += 't.Description1 LIKE \'%{0}%\''.format( name )
            if english_name is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 't.Description4 LIKE \'%{0}%\''.format( english_name )
            if description is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 't.Description2 LIKE \'%{0}%\''.format( description )
            sql = '{1} {2} WHERE {3} AND {0} ORDER BY t.PartID'.format( search_filter, select_cmd,
                                                                        from_database, default_where )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_tags(self, tag_id=None, name=None, parent_id=None):
        if tag_id is None and name is None and parent_id is None:
            # 找出没有父标签的标签
            sql = 'SELECT * FROM JJCom.Tag WHERE parent_id is NULL AND id > 0 ORDER BY id'
        else:
            sql = 'SELECT * FROM JJCom.Tag WHERE'
            factor = False
            if tag_id is not None:
                sql = '{1} id={0}'.format(tag_id, sql)
                factor = True
            if name is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} tag_name LIKE \'%{0}%\''.format(name, sql)
                factor = True
            if parent_id is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} parent_id={0}'.format(parent_id, sql)
            sql += ' ORDER BY sort_index, id'
        self.__c.execute(sql)
        return self.__c.fetchall()

    def get_tags_2_part(self, part_id):
        sql = 'SELECT t.id, t.tag_name, t.parent_id, t.sort_index ' \
              'FROM JJCom.Tag AS t INNER JOIN JJCom.PartTag AS p ON t.id=p.tag_id ' \
              'WHERE p.part_id={0}'.format( part_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_sub_tag_by_part_and_tag_name(self, part_id, tag_name):
        tt = self.get_tags( name=tag_name )
        if len( tt ) < 1:
            return None
        sql = 'SELECT t.tag_name ' \
              'FROM JJCom.Tag AS t INNER JOIN JJCom.PartTag AS p ON t.id=p.tag_id ' \
              'WHERE t.parent_id={0} AND p.part_id={1}'.format( tt[0][0], part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs[0][0]

    def get_parts_2_tag(self, tag_id):
        sql = 'SELECT id, name, english_name, description, status, comment ' \
              'FROM JJPart.PartTagView WHERE tag_id={0}'.format( tag_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_files_2_part(self, part_id):
        sql = 'SELECT FilePath FROM JJPart.FileRelation WHERE PartID={0}'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    def get_thumbnail_2_part(self, part_id, ver=None):
        sql = 'SELECT Thumbnail, Version FROM JJPart.PartThumbnail ' \
              'WHERE PartId={0} ORDER BY Version DESC'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs[0][0]

    def get_children(self, part_id):
        sql = 'SELECT Number AS relation_index, PartID AS id, Description1 AS name, Description4 AS english_name,' \
              ' StatusType AS status, Description2 AS description, Comment AS comment, Quantity AS qty_1,' \
              ' ActualQty AS qty_2, PartRelationID AS relation_id FROM JJPart.ChildParts ' \
              'WHERE ParentPart={0} ORDER BY Number'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def close(self):
        if self.__conn is not None:
            self.__conn.close()

    def save_change(self):
        if self.__conn is not None:
            self.__conn.commit()

    def sort_one_tag_to_index(self, tag_id, target_index):
        sql = 'UPDATE JJCom.Tag SET sort_index={0} WHERE id={1}'.format( target_index, tag_id )
        self.__c.execute( sql )

    def set_tag_parent(self, tag_id, parent_id):
        if parent_id is not None:
            sql = 'UPDATE JJCom.Tag SET parent_id={0} WHERE id={1}'.format(parent_id, tag_id)
        else:
            sql = 'UPDATE JJCom.Tag SET parent_id=NULL WHERE id={0}'.format(tag_id)
        self.__c.execute(sql)
