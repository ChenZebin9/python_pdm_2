import configparser
import sys
import os
import sqlite3

from PyQt5.QtWidgets import QApplication

from NPartMainWindow import NPartMainWindow
from db.DatabaseHandler import DatabaseHandler
from db.SqliteHandler import SqliteHandler
from db.MssqlHandler import MssqlHandler


class InitConfig:

    def __init__(self):
        self.db_name = 'rt_config.db'
        if os.path.exists(self.db_name):
            return
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE display_config
        (
            name TEXT CONSTRAINT pk_display_config PRIMARY KEY NOT NULL,
            config_value TEXT NOT NULL
        )
        ''')
        c.execute('INSERT INTO display_config VALUES (\'columns\', \'1,1,0,1,0,0,1,1,0,0,0,1\')')
        c.execute('INSERT INTO display_config VALUES (\'default_tag_group\', \'-1\')')
        conn.commit()
        conn.close()


if __name__ == '__main__':
    database_handler: DatabaseHandler = None
    init_config: InitConfig = None
    try:
        config = configparser.ConfigParser()
        if not config.read('pdm_config.ini', encoding='GBK'):
            raise Exception('INI file not found.')
        init_config = InitConfig()
        mode = config.getint('Config', 'Mode')
        work_folder = None
        user_name = None
        vault = None
        solidWorks_app = None
        to_offline = False
        if mode == 0:
            try:
                import clr
                clr.FindAssembly('EpdmLib.dll')
                from EpdmLib import *
                vault = EpdmLib()
                solidWorks_app = SolidWorksApi()
                vault_name = config.get('Online', 'vault')
                vault.Login(vault_name)
                user_name = vault.GetUserName()
                work_folder = vault.GetRootFolder()
                server = config.get('Online', 'server')
                user = config.get('Online', 'user')
                password = config.get('Online', 'password')
                database_name = config.get('Online', 'database')
                database_handler = MssqlHandler(server, database_name, user, password)
            except:
                print('无法进入在线登陆模式。')
                mode = 1
        if mode == 1:
            work_folder = config.get('Database', 'Folder')
            user_name = config.get('Database', 'UserName')
            database_file = config.get('Database', 'DatabaseFile')
            database_handler = SqliteHandler(database_file)
        app = QApplication(sys.argv)
        myWin = NPartMainWindow( database=database_handler, username=user_name,
                                 work_folder=work_folder, pdm_vault=vault, mode=mode )
        myWin.add_config(solidWorks_app, init_config.db_name)
        myWin.show()
        sys.exit(app.exec_())
    except Exception as e:
        print('Error: ' + str(e))
    finally:
        if database_handler is not None:
            database_handler.close()
