# coding=gbk
from ui3.HandleEntranceDialog import *
from PyQt5.QtWidgets import (QDialog)
from ui3.NHandleRequirementDialog import NHandleRequirementDialog


class NHandleEntranceDialog( QDialog, Ui_Dialog ):

    def __init__(self, parent=None, database=None, config_dict=None):
        self.__parent = parent
        self.__database = database
        self.__operator = config_dict['Operator']
        self.__data = []
        super( NHandleEntranceDialog, self ).__init__( parent )
        self.setModal( True )
        self.setup_ui()
        self.init_data()

    def setup_ui(self):
        super( NHandleEntranceDialog, self ).setupUi( self )
        self.setLayout( self.g1_layout )

        # 相应方法的链接
        self.toBuyPushButton.clicked.connect( lambda: self.__do_handle( mode=1 ) )
        self.toProducePushButton.clicked.connect( lambda: self.__do_handle( mode=2 ) )
        self.toStoragePushButton.clicked.connect( lambda: self.__do_handle( mode=3 ) )
        self.toPickPushButton.clicked.connect( lambda: self.__do_handle( mode=4 ) )

    def init_data(self):
        """
        初始化数据
        :return:
        """
        p_d = [self.__database.select_process_data( process_type=1 ),
               self.__database.select_process_data( process_type=2 ),
               self.__database.select_process_data( process_type=3 ),
               self.__database.select_process_data( process_type=4 )]
        self.toBuyPushButton.setEnabled( p_d[0][0] > 0 )
        self.toBuyLabel.setText( '{0}'.format( p_d[0][0] ) )
        self.toProducePushButton.setEnabled( p_d[1][0] > 0 )
        self.toProduceLabel.setText( '{0}'.format( p_d[1][0] ) )
        self.toStoragePushButton.setEnabled( p_d[2][0] > 0 )
        self.toStorageLabel.setText( '{0}'.format( p_d[2][0] ) )
        self.toPickPushButton.setEnabled( p_d[3][0] > 0 )
        self.toPickLabel.setText( '{0}'.format( p_d[3][0] ) )
        self.__data = p_d

    def __do_handle(self, mode=1):
        """
        根据不同的mode，执行具体的配料程序
        :param mode: 1=投料（请购），2=派工，3=入库，4=退库
        :return:
        """
        the_config = {'Operator': self.__operator, 'Process': mode, 'Data': self.__data[mode - 1]}
        dialog = NHandleRequirementDialog( parent=self.__parent, database=self.__database, config_dict=the_config )
        dialog.show()
        self.close()
