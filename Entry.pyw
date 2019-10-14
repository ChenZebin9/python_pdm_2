import configparser
import sys
import os
import sqlite3

from PyQt5.QtWidgets import QApplication
from NEntranceDialog import NEntranceDialog


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


if __name__ == '__main__':
    """ app = QApplication(sys.argv) 要放置在最前面，否则会出现许多可怪的问题。 """
    app = QApplication( sys.argv )
    entrance_dialog = NEntranceDialog( parent=None )
    func_index = entrance_dialog.exec()
    if func_index == 1:
        from NPartMainWindow import NPartMainWindow
        from db.DatabaseHandler import DatabaseHandler
        from db.SqliteHandler import SqliteHandler
        from db.MssqlHandler import MssqlHandler

        database_handler: DatabaseHandler = None
        init_config: InitConfig = None
        try:
            config = configparser.ConfigParser()
            if not config.read( 'pdm_config.ini', encoding='GBK' ):
                raise Exception( 'INI file not found.' )
            init_config = InitConfig()
            mode = config.getint( 'Config', 'Mode' )
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
                    vault.Login( vault_name )
                    user_name = vault.GetUserName()
                    work_folder = vault.GetRootFolder()
                    server = config.get( 'Online', 'server' )
                    user = config.get( 'Online', 'user' )
                    password = config.get( 'Online', 'password' )
                    database_name = config.get( 'Online', 'database' )
                    database_handler = MssqlHandler( server, database_name, user, password )
                except:
                    print( '无法进入在线登陆模式。' )
                    vault = None
                    mode = 1
            if mode == 1:
                work_folder = config.get( 'Database', 'Folder' )
                user_name = config.get( 'Database', 'UserName' )
                database_file = config.get( 'Database', 'DatabaseFile' )
                database_handler = SqliteHandler( database_file )
            myWin = NPartMainWindow( database=database_handler, username=user_name,
                                     work_folder=work_folder, pdm_vault=vault, mode=mode )
            myWin.add_config_and_init( solidWorks_app, init_config.db_name )
            myWin.show()
            sys.exit( app.exec_() )
        # except Exception as e:
        #     print('Error: ' + str(e))
        finally:
            if database_handler is not None:
                database_handler.close()
    elif func_index == 2:
        from NProductMainWindow import NProductMainWindow
        from db.ProductDatasHandler import SqliteHandler as ProductDatabase

        database = ProductDatabase( r'db/produce_datas.db' )
        theDialog = NProductMainWindow( parent=None, database=database )
        theDialog.show()
        sys.exit( app.exec_() )
    elif func_index == 3:
        pass
    elif func_index == 4:
        import NCreatePickBillDialog
        NCreatePickBillDialog.run_function()
