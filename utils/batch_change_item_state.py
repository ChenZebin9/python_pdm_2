# coding=gbk
""" 批量修改零件的状态 """
import xlwings as xw
import os


class BatchStateChange:
    """
    执行该功能的主题
    """

    def __init__(self, vault, database):
        self.__vault = vault
        self.__database: MssqlHandler = database
        self.__item_list = []
        self.__related_file_dict = {}

    def run(self):
        """ 运行主体 """
        self.__get_target_items()
        print( '收集目标数据完成。' )
        self.__rock_back_state()
        # self.__change_state()
        print( '转换目标状态完成。' )

    def __get_target_items(self, part_id=None):
        i = 1
        while True:
            cell = xw.Range( f'A{i}' )
            i += 1
            if cell.height < 1.0:
                continue
            v = cell.value
            if type( v ) == int or type( v ) == float:
                self.__item_list.append( int( v ) )
            elif type( v ) == str:
                try:
                    id = int( v.lstrip( '0' ) )
                    self.__item_list.append( id )
                except:
                    continue
            elif v is None or len( v ) == 0:
                break

        for item in self.__item_list:
            files = self.__database.get_files_2_part( item )
            if len( files ) > 0:
                st_list = []
                for f in files:
                    st = self.__get_item_status( f )
                    st_list.append( st )
                self.__related_file_dict[item] = (files, st_list)

    def __get_item_status(self, file_path):
        try:
            ss = self.__vault.GetFileStatus( file_path )
            return ss[1], ss[2]
        except:
            return None

    def __rock_back_state(self):
        for item in self.__item_list:
            if item in self.__related_file_dict:
                data_s = self.__related_file_dict[item]
                files = data_s[0]
                status = data_s[1]
                i = 0
                # 先全部转为已批准状态
                for f in files:
                    tf = f.upper()
                    if tf.endswith( 'SLDPRT' ) or tf.endswith( 'SLDDRW' ):
                        try:
                            s = status[i][0]
                            if s != '锁定中':
                                continue
                            self.__vault.ChangeState( f, '已批准', 'Change State by Admin 5' )
                            print( f'更改\'{f}\'的状态……' )
                        except Exception as ex:
                            print( f'{f}转换时出错:{str( ex )}' )
                    i += 1

    def __change_state(self):
        for item in self.__item_list:
            if item in self.__related_file_dict:
                data_s = self.__related_file_dict[item]
                files = data_s[0]
                status = data_s[1]
                i = 0
                # 先全部转为已批准状态
                for f in files:
                    tf = f.upper()
                    if tf.endswith( 'SLDPRT' ) or tf.endswith( 'SLDDRW' ):
                        try:
                            s = status[i][0]
                            if s == '设计中':
                                self.__vault.ChangeState( f, '校对中', 'Change State by Admin 1' )
                                self.__vault.ChangeState( f, '已批准', 'Change State by Admin 2' )
                            elif s == '校对中':
                                self.__vault.ChangeState( f, '已批准', 'Change State by Admin 2' )
                            elif s == '审核中':
                                self.__vault.ChangeState( f, '已批准', 'Change State by Admin 3' )
                            elif s == '锁定中':
                                print( f'\'{f}\'已被锁定' )
                                continue
                            self.__vault.ChangeState( f, '锁定中', 'Change State by Admin 4' )
                            print( f'更改\'{f}\'的状态……' )
                        except Exception as ex:
                            print( f'{f}转换时出错:{str( ex )}' )
                    i += 1


if __name__ == '__main__':
    # 将工作目录设置在上级目录中
    p = os.path.abspath( os.path.join( os.getcwd(), ".." ) )
    print(f'当前的工作目录为：{p}')
    os.chdir( p )

    import clr

    clr.FindAssembly( 'dlls/EpdmLib.dll' )
    clr.AddReference( 'dlls/EpdmLib' )
    from EpdmLib import *
    from db.MssqlHandler import MssqlHandler

    the_vault = EpdmLib()
    the_database = MssqlHandler( server='191.1.6.103', database='Greatoo_JJ_Database',
                                 user='sa', password='8893945' )

    app = BatchStateChange( the_vault, the_database )
    app.run()
    the_database.close()
