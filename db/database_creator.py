""" 建立sqlite数据库文件的表结构 """
import sqlite3
import os


class DatabaseCreator:

    def __init__(self, file_path):
        self.db = sqlite3.connect(file_path)
        c = self.db.cursor()

        c.execute('''
        CREATE TABLE status
        (
            id INT CONSTRAINT pk_part_status PRIMARY KEY,
            description TEXT NOT NULL
        )
        ''')
        c.execute('''
        CREATE TABLE tag
        (
            id INT CONSTRAINT pk_tag PRIMARY KEY NOT NULL,
            tag_name TEXT NOT NULL,
            parent_id INT REFERENCES tag (id),
            sort_index INT NOT NULL DEFAULT 1
        )
        ''')
        c.execute('''
        CREATE TABLE part
        (
            id INT CONSTRAINT pk_part PRIMARY KEY NOT NULL,
            status_id INT REFERENCES status (id),
            name TEXT NOT NULL,
            english_name TEXT NOT NULL,
            description TEXT NULL,
            comment TEXT NULL
        )
        ''')
        c.execute('''
        CREATE TABLE part_relation
        (
            id INT CONSTRAINT pk_part_relation PRIMARY KEY NOT NULL,
            child_part_id INT REFERENCES part (id) NOT NULL,
            parent_part_id INT REFERENCES part (id) NOT NULL,
            qty_1 REAL NOT NULL,
            qty_2 REAL NOT NULL,
            relation_index INT NOT NULL,
            comment TEXT NULL
        )
        ''')
        c.execute('''
        CREATE TABLE part_2_file
        (
            part_id INT REFERENCES part (id) NOT NULL,
            file_path TEXT NOT NULL,
            CONSTRAINT pk_part_2_file PRIMARY KEY (part_id, file_path)
        )
        ''')
        c.execute('''
        CREATE TABLE part_tag
        (
            part_id INT REFERENCES part (id) NOT NULL,
            tag_id INT REFERENCES tag (id) NOT NULL,
            CONSTRAINT pk_part_tag PRIMARY KEY (part_id, tag_id)
        )
        ''')
        create_view_sql = 'CREATE VIEW part_view AS ' \
                          'SELECT a.id, a.name, a.english_name, a.description, b.description AS status FROM ' \
                          'part AS a INNER JOIN status AS b ON a.status_id=b.id WHERE a.status_id>80'
        c.execute( create_view_sql )
        create_view_sql = 'CREATE VIEW part_relation_view AS ' \
                          'SELECT a.id, b.parent_part_id, a.name, a.english_name, a.description, a.status, ' \
                          'b.qty_1, b.qty_2, b.relation_index, b.comment FROM ' \
                          'part_view AS a INNER JOIN part_relation AS b ON a.id=b.child_part_id ' \
                          'ORDER BY b.parent_part_id, b.relation_index'
        c.execute( create_view_sql )
        c.execute( '''
        CREATE TABLE part_thumbnail
        (
            part_id INT REFERENCES part (id) NOT NULL,
            version INT NOT NULL,
            thumbnail BLOB NOT NULL,
            CONSTRAINT pk_part_thumbnail PRIMARY KEY (part_id, version)
        )
        ''' )


if __name__ == '__main__':
    database_file = 'greatoo_jj.db'
    if os.path.exists(database_file):
        os.remove(database_file)
    DatabaseCreator( database_file )
