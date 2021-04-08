# coding=gbk
from PyQt5.QtWidgets import QDialog, QMessageBox

from UiFrame import PartInfoPanel
from ui.CreatePartDialog import Ui_Dialog


class NCreatePartDialog( QDialog, Ui_Dialog ):
    ComTag = ('类别', '标准', '品牌', '来源', '单位', '产品')

    def __init__(self, parent, database):
        self.__parent = parent
        self.__database = database
        super( NCreatePartDialog, self ).__init__( parent )
        self.__part_info_panel = PartInfoPanel( parent=self, mode=1 )
        self.__has_created = False
        self.setup_ui()
        self.__init_data()

    def setup_ui(self):
        super( NCreatePartDialog, self ).setupUi( self )
        self.v_2_layout.addWidget( self.__part_info_panel )
        self.setLayout( self.v_1_layout )

    def __init_data(self):
        self.available_id = self.__database.next_available_part_id()
        tag_dict = {}
        top_tag_names = self.__database.get_tags()
        for t in top_tag_names:
            tag_name = t[1]
            if t[1] in NCreatePartDialog.ComTag:
                sub_tags = self.__database.get_tags( parent_id=t[0] )
                value_list = []
                for s_t in sub_tags:
                    value_list.append( s_t[1] )
                tag_dict[t[1]] = value_list
            else:
                tag_dict[tag_name] = None
        self.__part_info_panel.init_data( self.available_id, tag_dict )

    def accept(self):
        try:
            # 创建新单元
            part_data = self.__part_info_panel.get_part_info()
            # 进行数据有效性的评估
            if len( part_data[1] ) < 1:
                raise Exception( '名称不能为空。' )
            if len( part_data[2] ) < 1:
                raise Exception( 'The english name couldn\'t empty.' )
            if not ('类别' in part_data[5]):
                QMessageBox.warning(self, '数据不完整', '类别必须要选择！', QMessageBox.Ok)
                self.reject()
                return
            self.__database.create_a_new_part( part_data[0], part_data[1], part_data[2], part_data[3],
                                               part_data[4], part_data[5] )
            QMessageBox.information(self, '', f'完成创建{part_data[0]}。', QMessageBox.Ok)
            self.__has_created = True
            self.reject()
        except Exception as ex:
            QMessageBox.warning( self, '创建时出错', f'{ex}', QMessageBox.Ok )

    def reject(self):
        if not self.__has_created:
            self.__database.set_part_id_2_prepared( self.available_id )
        super( NCreatePartDialog, self ).reject()
