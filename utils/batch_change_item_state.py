# coding=gbk
""" �����޸������״̬ """
import xlwings as xw
import os


class BatchStateChange:
    """
    ִ�иù��ܵ�����
    """

    def __init__(self, vault, database):
        self.__vault = vault
        self.__database: MssqlHandler = database
        self.__item_list = []
        self.__related_file_dict = {}

    def run(self):
        """ �������� """
        self.__get_target_items()
        print( '�ռ�Ŀ��������ɡ�' )
        self.__rock_back_state()
        # self.__change_state()
        print( 'ת��Ŀ��״̬��ɡ�' )

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
                # ��ȫ��תΪ����׼״̬
                for f in files:
                    tf = f.upper()
                    if tf.endswith( 'SLDPRT' ) or tf.endswith( 'SLDDRW' ):
                        try:
                            s = status[i][0]
                            if s != '������':
                                continue
                            self.__vault.ChangeState( f, '����׼', 'Change State by Admin 5' )
                            print( f'����\'{f}\'��״̬����' )
                        except Exception as ex:
                            print( f'{f}ת��ʱ����:{str( ex )}' )
                    i += 1

    def __change_state(self):
        for item in self.__item_list:
            if item in self.__related_file_dict:
                data_s = self.__related_file_dict[item]
                files = data_s[0]
                status = data_s[1]
                i = 0
                # ��ȫ��תΪ����׼״̬
                for f in files:
                    tf = f.upper()
                    if tf.endswith( 'SLDPRT' ) or tf.endswith( 'SLDDRW' ):
                        try:
                            s = status[i][0]
                            if s == '�����':
                                self.__vault.ChangeState( f, 'У����', 'Change State by Admin 1' )
                                self.__vault.ChangeState( f, '����׼', 'Change State by Admin 2' )
                            elif s == 'У����':
                                self.__vault.ChangeState( f, '����׼', 'Change State by Admin 2' )
                            elif s == '�����':
                                self.__vault.ChangeState( f, '����׼', 'Change State by Admin 3' )
                            elif s == '������':
                                print( f'\'{f}\'�ѱ�����' )
                                continue
                            self.__vault.ChangeState( f, '������', 'Change State by Admin 4' )
                            print( f'����\'{f}\'��״̬����' )
                        except Exception as ex:
                            print( f'{f}ת��ʱ����:{str( ex )}' )
                    i += 1


if __name__ == '__main__':
    # ������Ŀ¼�������ϼ�Ŀ¼��
    p = os.path.abspath( os.path.join( os.getcwd(), ".." ) )
    print(f'��ǰ�Ĺ���Ŀ¼Ϊ��{p}')
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
