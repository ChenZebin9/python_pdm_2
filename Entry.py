import configparser
import sys
import os
import sqlite3

from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.NEntranceDialog import NEntranceDialog


class InitConfig:

    def __init__(self):
        cwd = os.getcwd()
        print( '当前运行目录是：{0}'.format( cwd ) )
        self.db_name = '{0}\\rt_config.db'.format( cwd )
        if os.path.exists( self.db_name ):
            return
        conn = sqlite3.connect( self.db_name )
        c = conn.cursor()
        c.execute( '''
        CREATE TABLE display_config
        (
            name TEXT CONSTRAINT pk_display_config PRIMARY KEY NOT NULL,
            config_value TEXT NOT NULL
        )
        ''' )
        c.execute( 'INSERT INTO display_config VALUES (\'columns\', \'1,1,0,1,0,0,1,1,0,0,0,1\')' )
        c.execute( 'INSERT INTO display_config VALUES (\'default_tag_group\', \'-1\')' )
        conn.commit()
        conn.close()


def Get_mssql_config(config: configparser, lock_mode=None):
    """ 获取在线或者离线模式，MSSQL的设置。 """
    mode = config.getint( 'Config', 'mode' )
    server = '191.1.6.103'
    user = '_user'
    password = '123456'
    database_name = 'Greatoo_JJ_Database'
    if lock_mode is not None:
        mode = lock_mode
    if mode == 0:
        server = config.get( 'Online', 'server' )
        user = config.get( 'Online', 'user' )
        password = config.get( 'Online', 'password' )
        database_name = config.get( 'Online', 'database' )
    elif mode == 1:
        server = config.get( 'Offline', 'local_server' )
        user = config.get( 'Offline', 'local_user' )
        password = config.get( 'Offline', 'local_password' )
        database_name = config.get( 'Offline', 'local_database' )
    return mode, server, database_name, user, password


if __name__ == '__main__':
    """ app = QApplication(sys.argv) 要放置在最前面，否则会出现许多可怪的问题。 """
    app = QApplication( sys.argv )

    config = configparser.ConfigParser()
    if not config.read( 'pdm_config.ini', encoding='GBK' ):
        raise Exception( 'INI file not found.' )
    database_setting = Get_mssql_config( config )
    mode = database_setting[0]
    if mode == 2:
        resp = QMessageBox.question( None, '询问', '是否在线登录？', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                     QMessageBox.Yes )
        if resp == QMessageBox.Cancel:
            sys.exit( 0 )
        elif resp == QMessageBox.Yes:
            mode = 0
        else:
            mode = 1

    entrance_dialog = NEntranceDialog( parent=None )
    func_index = entrance_dialog.exec()

    if func_index == 1:
        from ui.NPartMainWindow import NPartMainWindow
        from db.DatabaseHandler import DatabaseHandler
        from db.SqliteHandler import SqliteHandler
        from db.MssqlHandler import MssqlHandler

        database_handler: DatabaseHandler = None
        init_config: InitConfig = None
        try:
            init_config = InitConfig()
            # mode = config.getint( 'Config', 'mode' )
            local_folder = config.get( 'Offline', 'local_folder' )
            work_folder = None
            user_name = None
            vault = None
            solidWorks_app = None
            to_offline = False
            if mode == 0:
                try:
                    import clr

                    clr.FindAssembly( 'dlls/EpdmLib.dll' )
                    clr.AddReference( 'dlls/EpdmLib' )
                    from EpdmLib import *

                    vault = EpdmLib()
                    solidWorks_app = SolidWorksApi()
                    vault_name = config.get( 'Online', 'vault' )
                    user_name = vault.GetUserName()
                    work_folder = vault.GetRootFolder()
                    database_handler = MssqlHandler( *database_setting[1:] )
                except:
                    QMessageBox.warning( None, '', '无法在线登录！将使用离线方式。' )
                    vault = None
                    mode = 1
            if mode == 1:
                database_type = config.getint( 'Offline', 'database_type' )
                work_folder = config.get( 'Offline', 'folder' )
                if database_type == 2:
                    # 使用 Sqlite 的数据库模式
                    user_name = config.get( 'Offline', 'userName' )
                    database_file = config.get( 'Offline', 'database_file' )
                    database_handler = SqliteHandler( database_file )
                elif database_type == 1:
                    # 使用 MSSQL 的数据库模式
                    database_setting = Get_mssql_config( config, lock_mode=1 )
                    database_handler = MssqlHandler( *database_setting[1:] )
            myWin = NPartMainWindow( database=database_handler, username=user_name,
                                     work_folder=work_folder, pdm_vault=vault, mode=mode,
                                     local_folder=local_folder )
            myWin.add_config_and_init( solidWorks_app, init_config.db_name )
            myWin.show()
            sys.exit( app.exec_() )
        except Exception as ex:
            QMessageBox.warning( None, '启动时出错', str( ex ) )
        finally:
            if database_handler is not None:
                database_handler.close()
    elif func_index == 2:
        from ui2.NProductMainWindow import NProductMainWindow
        from db.ProductDatasHandler import MssqlHandler as Mssql_Database, SqliteHandler as Sqlite_Datbase

        try:
            if mode == 0:
                database = Mssql_Database( *database_setting[1:] )
            else:
                user_name = config.get( 'Offline', 'userName' )
                database_file = config.get( 'Offline', 'database_file' )
                database = Sqlite_Datbase( database_file )
            theDialog = NProductMainWindow( parent=None, database=database, offline=mode )
            theDialog.show()
            sys.exit( app.exec_() )
        except Exception as ex:
            QMessageBox.warning( None, '启动时出错', str( ex ) )
            sys.exit( -1 )
    elif func_index == 3:
        """ 采购管理 """
        pass
    elif func_index == 4:
        from ui3 import NCreatePickBillDialog

        NCreatePickBillDialog.run_function( database_setting )
