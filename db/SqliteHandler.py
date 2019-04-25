from db.DatabaseHandler import *
import sqlite3


class SqliteHandler(DatabaseHandler):

    def save_change(self):
        if self.__conn is not None:
            self.__conn.commit()

    def get_tags_2_part(self, part_id):
        sql = 'SELECT t.id, t.tag_name, t.parent_id, t.sort_index ' \
              'FROM tag AS t INNER JOIN part_tag AS p ON t.id=p.tag_id ' \
              'WHERE p.part_id={0}'.format(part_id)
        self.__c.execute(sql)
        return self.__c.fetchall()

    def get_parts_2_tag(self, tag_id):
        sql = 'SELECT id, name, english_name, description, status, comment ' \
              'FROM part_tag_view WHERE tag_id={0}'.format( tag_id )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_tags(self, tag_id=None, name=None, parent_id=None):
        if tag_id is None and name is None and parent_id is None:
            # 找出没有父标签的标签
            sql = 'SELECT * FROM tag WHERE parent_id is NULL AND id > 0 ORDER BY id'
        else:
            sql = 'SELECT * FROM tag WHERE'
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

    def __init__(self, database_file):
        self.__conn = sqlite3.connect(database_file, timeout=30.0)
        self.__c = self.__conn.cursor()

    def get_parts(self, part_id=None, name=None, english_name=None, description=None):
        if part_id is None and name is None and english_name is None and description is None:
            sql = 'SELECT * FROM part_view ORDER BY id'
        elif part_id is not None:
            sql = 'SELECT * FROM part_view WHERE id={0}'.format(part_id)
        else:
            search_filter = ''
            if name is not None:
                search_filter += 'name LIKE \'%{0}%\''.format( name )
            if english_name is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'english_name LIKE \'%{0}%\''.format( english_name )
            if description is not None:
                if len( search_filter ) > 0:
                    search_filter += ' AND '
                search_filter += 'description LIKE \'%{0}%\''.format( description )
            sql = 'SELECT * FROM part_view WHERE {0} ORDER BY id'.format( search_filter )
        self.__c.execute( sql )
        return self.__c.fetchall()

    def get_files_2_part(self, part_id):
        sql = 'SELECT file_path FROM part_2_file WHERE part_id={0}'.format(part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append(r[0])
        return result

    def get_thumbnail_2_part(self, part_id, ver=None):
        sql = 'SELECT thumbnail, version FROM part_thumbnail ' \
              'WHERE part_id={0} ORDER BY version DESC'.format(part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs[0][0]

    def get_children(self, part_id):
        sql = 'SELECT relation_index, id, name, english_name, status,' \
              ' description, comment, qty_1, qty_2, relation_id FROM part_relation_view ' \
              'WHERE parent_part_id={0} ORDER BY relation_index'.format(part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs

    def get_sub_tag_by_part_and_tag_name(self, part_id, tag_name):
        tt = self.get_tags(name=tag_name)
        if len(tt) < 1:
            return None
        sql = 'SELECT t.tag_name ' \
              'FROM tag AS t INNER JOIN part_tag AS p ON t.id=p.tag_id ' \
              'WHERE t.parent_id={0} AND p.part_id={1}'.format(tt[0][0], part_id)
        self.__c.execute(sql)
        rs = self.__c.fetchall()
        if len(rs) < 1:
            return None
        return rs[0][0]

    def close(self):
        if self.__conn is not None:
            self.__conn.close()

    def sort_one_tag_to_index(self, tag_id, target_index):
        sql = 'UPDATE tag SET sort_index={0} WHERE id={1}'.format(target_index, tag_id)
        self.__c.execute(sql)

    def set_tag_parent(self, tag_id, parent_id):
        if parent_id is not None:
            sql = 'UPDATE tag SET parent_id={0} WHERE id={1}'.format(parent_id, tag_id)
        else:
            sql = 'UPDATE tag SET parent_id=NULL WHERE id={0}'.format(tag_id)
        self.__c.execute(sql)
