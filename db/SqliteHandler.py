from db.DatabaseHandler import *
import sqlite3


class SqliteHandler( DatabaseHandler ):

    def get_available_supply_operation_bill(self, prefix=None):
        pass

    def select_process_data(self, process_type=1):
        pass

    def create_supply_operation(self, data):
        pass

    def create_picking_record(self, data):
        pass

    def next_available_part_id(self):
        pass

    def set_part_id_2_prepared(self, part_id):
        pass

    def create_a_new_part(self, part_id, name, english_name, description, comment, tag_dict):
        pass

    def update_part_info(self, part_id, name, english_name, description, comment):
        pass

    def insert_requirements(self, bill_data, items_data):
        pass

    def get_require_bill(self, prefix=None, bill_num=None):
        pass

    def get_erp_info(self, erp_code):
        pass

    def get_products_by_id(self, product_id):
        pass

    def get_all_storing_position(self):
        pass

    def get_storing(self, part_id=None, position=None):
        pass

    def del_tag_from_part(self, tag_id, part_id):
        sql = 'DELETE FROM part_tag WHERE tag_id={0} AND part_id={1}'.format( tag_id, part_id )
        self.__c.execute( sql )
        self.__conn.commit()

    def del_one_tag(self, tag_id):
        del_link_sql = 'DELETE FROM part_tag WHERE tag_id={0}'.format( tag_id )
        self.__c.execute( del_link_sql )
        del_tag_sql = 'DELETE FROM tag WHERE id={0}'.format( tag_id )
        self.__c.execute( del_tag_sql )
        self.__conn.commit()

    def rename_one_tag(self, tag_id, tag_name):
        update_tag_sql = 'UPDATE tag SET tag_name=\'{0}\' WHERE id={1}'.format( tag_name, tag_id )
        self.__c.execute( update_tag_sql )
        self.__conn.commit()

    def set_tag_2_part(self, tag_id, part_id):
        check_tag_link = 'SELECT part_id FROM part_tag WHERE part_id={0} AND tag_id={1}'.format( part_id, tag_id )
        self.__c.execute( check_tag_link )
        if len( self.__c.fetchall() ) > 0:
            return False
        insert_tag_link = 'INSERT INTO part_tag VALUES ({0}, {1})'.format( part_id, tag_id )
        self.__c.execute( insert_tag_link )
        self.__conn.commit()
        return True

    def copy(self):
        return 'SQLite3', SqliteHandler( database_file=self.__db_file, copy=True, conn=self.__conn )

    def create_one_tag(self, name, parent_id):
        tag_count = 'SELECT MAX(id) FROM tag'
        self.__c.execute( tag_count )
        next_id = self.__c.fetchone()[0] + 1
        if parent_id is None:
            sort_count = 'SELECT MAX(sort_index) FROM tag WHERE parent_id is NULL'
            self.__c.execute( sort_count )
            next_sort_index = self.__c.fetchone()[0] + 1
            insert_sql = 'INSERT INTO tag VALUES ({0}, \'{1}\', NULL, {2})'.format( next_id, name, next_sort_index )
        else:
            sort_count = 'SELECT MAX(sort_index) FROM tag WHERE parent_id={0}'.format( parent_id )
            self.__c.execute( sort_count )
            the_sort = self.__c.fetchone()[0]
            if the_sort is None:
                next_sort_index = 1
            else:
                next_sort_index = the_sort + 1
            insert_sql = 'INSERT INTO tag VALUES ({0}, \'{1}\', {2}, {3})'.format( next_id, name,
                                                                                   parent_id, next_sort_index )
        self.__c.execute( insert_sql )
        self.__conn.commit()
        return next_id

    def save_change(self):
        if self.__conn is not None:
            self.__conn.commit()

    def get_tags_2_part(self, part_id):
        sql = 'SELECT t.id, t.tag_name, t.parent_id, t.sort_index ' \
              'FROM tag AS t INNER JOIN part_tag AS p ON t.id=p.tag_id ' \
              'WHERE p.part_id={0}'.format( part_id )
        self.__c.execute( sql )
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
                sql = '{1} id={0}'.format( tag_id, sql )
                factor = True
            if name is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} tag_name LIKE \'%{0}%\''.format( name, sql )
                factor = True
            if parent_id is not None:
                if factor:
                    sql += ' AND'
                sql = '{1} parent_id={0}'.format( parent_id, sql )
            sql += ' ORDER BY sort_index, id'
        self.__c.execute( sql )
        return self.__c.fetchall()

    def __init__(self, database_file, copy=False, conn=None):
        self.__db_file = database_file
        # 为解决多线程的问题
        if not copy:
            self.__conn = sqlite3.connect( database_file, check_same_thread=False )
        else:
            self.__conn = conn
        self.__conn.isolation_level = None
        self.__conn.row_factory = sqlite3.Row
        self.__c = self.__conn.cursor()

    def get_parts(self, part_id=None, name=None, english_name=None, description=None):
        if part_id is None and name is None and english_name is None and description is None:
            sql = 'SELECT * FROM part_view ORDER BY id'
        elif part_id is not None:
            sql = 'SELECT * FROM part_view WHERE id={0}'.format( part_id )
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
        sql = 'SELECT file_path FROM part_2_file WHERE part_id={0}'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        result = []
        for r in rs:
            result.append( r[0] )
        return result

    def get_thumbnail_2_part(self, part_id, ver=None):
        sql = 'SELECT thumbnail, version FROM part_thumbnail ' \
              'WHERE part_id={0} ORDER BY version DESC'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs[0][0]

    def get_children(self, part_id):
        sql = 'SELECT relation_index, id, name, english_name, status,' \
              ' description, comment, qty_1, qty_2, relation_id FROM part_relation_view ' \
              'WHERE parent_part_id={0} ORDER BY relation_index'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_parents(self, part_id):
        sql = 'SELECT b.relation_index, b.parent_part_id, a.name, a.english_name, a.status,' \
              ' a.description,  b.comment, b.qty_1, b.qty_2, b.id AS relation_id' \
              ' FROM part_view AS a INNER JOIN part_relation AS b ON a.id = b.parent_part_id' \
              ' WHERE b.child_part_id={0}' \
              ' ORDER BY b.parent_part_id, b.relation_index'.format( part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        return rs

    def get_sub_tag_by_part_and_tag_name(self, part_id, tag_name):
        tt = self.get_tags( name=tag_name )
        if len( tt ) < 1:
            return None
        sql = 'SELECT t.tag_name ' \
              'FROM tag AS t INNER JOIN part_tag AS p ON t.id=p.tag_id ' \
              'WHERE t.parent_id={0} AND p.part_id={1}'.format( tt[0][0], part_id )
        self.__c.execute( sql )
        rs = self.__c.fetchall()
        if len( rs ) < 1:
            return None
        temp = []
        for r in rs:
            temp.append( r[0] )
        return ' '.join( temp )

    def close(self):
        try:
            if self.__c is not None:
                self.__c.close()
            if self.__conn is not None:
                self.__conn.close()
        except:
            pass

    def sort_one_tag_to_index(self, tag_id, target_index):
        sql = 'UPDATE tag SET sort_index={0} WHERE id={1}'.format( target_index, tag_id )
        self.__c.execute( sql )

    def set_tag_parent(self, tag_id, parent_id):
        if parent_id is not None:
            sql = 'UPDATE tag SET parent_id={0} WHERE id={1}'.format( parent_id, tag_id )
        else:
            sql = 'UPDATE tag SET parent_id=NULL WHERE id={0}'.format( tag_id )
        self.__c.execute( sql )

    def get_pick_record_throw_erp(self, erp_id, which_company=1, top=2):
        """ 获取巨轮智能的ERP领料记录 """
        return None

    def get_price_from_self_record(self, part_id, top=2):
        """ 获取本系统的价格记录信息 """
        return None

    def get_erp_data(self, erp_code):
        pass
