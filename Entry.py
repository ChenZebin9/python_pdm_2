import configparser
import sys
import os
import sqlite3

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMessageBox

import Com
from ui.NEntranceDialog import NEntranceDialog


class InitConfig:

    def __init__(self):
        cwd = os.getcwd()
        print('当前运行目录是：{0}'.format(cwd))
        self.db_name = '{0}\\rt_config.db'.format(cwd)
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.c.execute('SELECT [name] FROM [sqlite_master] WHERE [type]=\'table\'')
        ts = self.c.fetchall()
        table_names = []
        for t in ts:
            table_names.append(t[0])
        if 'display_config' not in table_names:
            self.__create_display_config()
        if 'display_columns' not in table_names:
            self.__create_display_columns()
        if 'operation_property' not in table_names:
            self.__create_operation_property()
        self.conn.commit()
        self.conn.close()

    def __create_display_config(self):
        self.c.execute('''
                CREATE TABLE [display_config]
                (
                    [name] TEXT PRIMARY KEY NOT NULL,
                    [config_value] TEXT NOT NULL
                )
                ''')
        self.c.execute('INSERT INTO [display_config] VALUES (\'columns\', \'1,1,0,1,0,0,1,1,0,0,0,1\')')
        self.c.execute('INSERT INTO [display_config] VALUES (\'default_tag_group\', \'-1\')')
        self.c.execute('INSERT INTO [display_config] VALUES (\'before_columns\', \'1,1,0,1,0\')')
        self.c.execute('INSERT INTO [display_config] VALUES (\'after_columns\', \'0\')')

    def __create_display_columns(self):
        self.c.execute('CREATE TABLE [display_columns]([column_id] INT PRIMARY KEY)')
        column_id_s = (1, 15, 16, 2111)
        for i in column_id_s:
            self.c.execute(f'INSERT INTO [display_columns] VALUES ({i})')

    def __create_operation_property(self):
        self.c.execute('''
            CREATE TABLE [operation_property](
                [PropertyName] NVARCHAR(256) PRIMARY KEY NOT NULL, 
                [PropertyValue] NVARCHAR(256) NOT NULL)
            ''')
        self.c.execute('INSERT INTO [operation_property] VALUES (\'load_path\', \'D:/\')')
        self.c.execute('INSERT INTO [operation_property] VALUES (\'save_path\', \'D:/\')')


def Get_mssql_config(config: configparser, lock_mode=None):
    """ 获取在线或者离线模式，MSSQL的设置。 """
    mode = config.getint('Config', 'mode')
    server = '191.1.6.103'
    user = '_user'
    password = '123456'
    database_name = 'Greatoo_JJ_Database'
    if lock_mode is not None:
        mode = lock_mode
    if mode == 0:
        server = config.get('Online', 'server')
        user = config.get('Online', 'user')
        password = config.get('Online', 'password')
        database_name = config.get('Online', 'database')
    elif mode == 1:
        server = config.get('Offline', 'local_server')
        user = config.get('Offline', 'local_user')
        password = config.get('Offline', 'local_password')
        database_name = config.get('Offline', 'local_database')
    return mode, server, database_name, user, password


if __name__ == '__main__':
    """ app = QApplication(sys.argv) 要放置在最前面，否则会出现许多可怪的问题。 """
    app = QApplication(sys.argv)

    version = '1.6.2.13'

    config = configparser.ConfigParser()
    if not config.read('pdm_config.ini', encoding='GBK'):
        raise Exception('INI file not found.')
    database_setting = Get_mssql_config(config)
    mode = database_setting[0]
    if mode == 2:
        resp = QMessageBox.question(None, '询问', '是否在线登录？',
                                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                    QMessageBox.Yes)
        if resp == QMessageBox.Cancel:
            sys.exit(0)
        elif resp == QMessageBox.Yes:
            mode = 0
        else:
            mode = 1

    icon = QIcon()
    icon.addPixmap(QPixmap('OPS_ING_MMI.ico'), QIcon.Normal, QIcon.Off)

    entrance_dialog = NEntranceDialog(parent=None)
    entrance_dialog.setWindowIcon(icon)
    entrance_dialog.setWindowTitle(version)
    func_index = entrance_dialog.exec()

    init_config = InitConfig()
    Com.local_config_file = init_config.db_name

    if func_index == 1:
        from ui.NPartMainWindow import NPartMainWindow
        from db.DatabaseHandler import DatabaseHandler
        from db.SqliteHandler import SqliteHandler
        from db.MssqlHandler import MssqlHandler

        database_handler: DatabaseHandler = None

        try:
            local_folder = config.get('Offline', 'local_folder')
            work_folder = None
            user_name = None
            vault = None
            solidWorks_app = None
            to_offline = False

            if mode == 0:
                try:
                    import clr

                    clr.FindAssembly('dlls/EpdmLib.dll')
                    clr.AddReference('dlls/EpdmLib')
                    from EpdmLib import *

                    vault_name = config.get('Online', 'vault')
                    vault = EpdmLib(vault_name)
                    solidWorks_app = SolidWorksApi()
                    user_name = vault.GetUserName()
                    work_folder = vault.GetRootFolder()
                    database_handler = MssqlHandler(*database_setting[1:])
                except Exception as ex:
                    QMessageBox.warning(None, '异常', str(ex))
                    QMessageBox.warning(None, '', '无法在线登录！将使用离线方式。')
                    vault = None
                    mode = 1
            if mode == 1:
                database_type = config.getint('Offline', 'database_type')
                work_folder = config.get('Offline', 'folder')
                if database_type == 2:
                    # 使用 Sqlite 的数据库模式
                    user_name = config.get('Offline', 'userName')
                    database_file = config.get('Offline', 'database_file')
                    database_handler = SqliteHandler(database_file)
                elif database_type == 1:
                    # 使用 MSSQL 的数据库模式
                    database_setting = Get_mssql_config(config, lock_mode=1)
                    database_handler = MssqlHandler(*database_setting[1:])
            myWin = NPartMainWindow(database=database_handler, username=user_name,
                                    work_folder=work_folder, pdm_vault=vault, mode=mode,
                                    local_folder=local_folder)
            myWin.setWindowIcon(icon)
            myWin.add_config(solidWorks_app, init_config.db_name)
            myWin.show()
            sys.exit(app.exec_())
        except Exception as ex:
            QMessageBox.warning(None, '启动时出错', str(ex))
            # raise ex
        finally:
            if database_handler is not None and database_handler.get_database_type() != 'SQLite':
                database_handler.close()
    elif func_index == 2:
        from ui2.NProductMainWindow import NProductMainWindow
        from db.ProductDatasHandler import MssqlHandler as Mssql_Database, SqliteHandler as Sqlite_Database

        try:
            if mode == 0:
                database = Mssql_Database(*database_setting[1:])
            else:
                user_name = config.get('Offline', 'userName')
                database_file = config.get('Offline', 'database_file')
                database = Sqlite_Database(database_file)
            theDialog = NProductMainWindow(parent=None, database=database, offline=mode)
            theDialog.setWindowIcon(icon)
            theDialog.show()
            sys.exit(app.exec_())
        except Exception as ex:
            QMessageBox.warning(None, '启动时出错', str(ex))
            sys.exit(-1)
    elif func_index == 3:
        """ 生产配料管理 """
        from ui4.NAssemblyToolWindow import NAssemblyToolWindow
        from db.SqliteHandler import SqliteHandler
        from db.MssqlHandler import MssqlHandler

        user_name = config.get('Offline', 'userName')
        assigned_material_dir = config.get('MaterialSupply', 'assigned_dir')
        if mode == 0:
            database = MssqlHandler(*database_setting[1:])
        else:
            database_file = config.get('Offline', 'database_file')
            database = SqliteHandler(database_file)
        theDialog = NAssemblyToolWindow(parent=None, database=database, user=user_name, _dir=assigned_material_dir)
        theDialog.setWindowIcon(icon)
        theDialog.show()
        sys.exit(app.exec_())
    elif func_index == 4:
        from ui4.NReplaceItemInExcelDialog import NReplaceItemInExcelDialog
        from db.DatabaseHandler import DatabaseHandler
        from db.SqliteHandler import SqliteHandler
        from db.MssqlHandler import MssqlHandler

        if mode == 0:
            database = MssqlHandler(*database_setting[1:])
        else:
            database_file = config.get('Offline', 'database_file')
            database = SqliteHandler(database_file)

        icon = QIcon()
        icon.addPixmap(QPixmap('OPS_ING_MMI.ico'), QIcon.Normal, QIcon.Off)

        dialog = NReplaceItemInExcelDialog(parent=None, database=database)
        _title = dialog.windowTitle() + f' v{version}' + ('（离线）' if mode == 1 else '')
        dialog.setWindowTitle(_title)
        dialog.setWindowIcon(icon)
        dialog.show()
        sys.exit(app.exec_())

"""
历史：
1.4.0.2 2022.01.08 改变了截图的方式，采用clr的方法。
1.4.2.5 2022.07.08 改正了子项目排序的问题。
1.4.3.5 2022.07.09 标签采用后台更新。子项目增加了代替的功能。

1.6.2.4 2023.03.08 更正了领料，导入和导出的问题。

1.6.2.7 2023.04.26 由于Epdm升级至2019版而导致奔溃的临时修改。临时版本！将登录库改为Greatoo_Ops，但工作目录仍未D:\\Greatoo_JJ。
1.6.2.8 2023.04.27 完全转至Greatoo_Ops库的工作模式。

1.6.2.11 2023.06.16 增加了双击DWG文件时的FTP关联。
1.6.2.12 2023.07.03 增加了生产配料管理模块的手工操作功能。
"""
