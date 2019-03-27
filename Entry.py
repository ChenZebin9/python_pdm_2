import sys
import configparser
from NPartMainWindow import NPartMainWindow
from SqliteHandler import SqliteHandler
from PyQt5.QtWidgets import QApplication, QMessageBox

if __name__ == '__main__':
    database_conn = None
    try:
        config = configparser.ConfigParser()
        if not config.read('pdm_config.ini', encoding='GBK'):
            raise Exception('INI file not found.')
        mode = config.getint('Config', 'Mode')
        vault_name = config.get('Config', 'Vault')
        work_folder = None
        user_name = None
        vault = None
        solidWorks_app = None
        if mode == 0:
            try:
                import clr
                clr.FindAssembly('EpdmLib.dll')
                from EpdmLib import *
                vault = EpdmLib()
                solidWorks_app = SolidWorksApi()
                vault.Login(vault_name)
                user_name = vault.GetUserName()
                work_folder = vault.GetRootFolder()
            except:
                print('无法进入在线登陆模式。')
                work_folder = config.get('Database', 'Folder')
                user_name = config.get('Database', 'UserName')
        elif mode == 1:
            work_folder = config.get('Database', 'Folder')
            user_name = config.get('Database', 'UserName')
        database_file = config.get('Database', 'DatabaseFile')
        database_conn = SqliteHandler(database_file)
        app = QApplication(sys.argv)
        myWin = NPartMainWindow( database=database_conn, username=user_name, work_folder=work_folder, pdm_vault=vault )
        myWin.add_config(solidWorks_app)
        myWin.show()
        sys.exit(app.exec_())
    except Exception as e:
        print('Error: ' + str(e))
    finally:
        if database_conn is not None:
            database_conn.close()
