# coding=gbk

from PyQt5.QtCore import (Qt, QItemSelectionModel, QDate, QModelIndex)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtWidgets import (QDialog, QMessageBox, QAbstractItemView, QItemDelegate, QDialogButtonBox, QSplitter,
                             QFrame, QVBoxLayout, QInputDialog)

from Part import Part
from db.DatabaseHandler import DatabaseHandler
from ui3.HandleRequirementDialog import *


class NHandleRequirementDialog( QDialog, Ui_Dialog ):

    def __init__(self, parent=None, database=None, config_dict=None):
        self.__parent = parent
        self.__database: DatabaseHandler = database
        # ������Ա
        self.__operator = config_dict['Operator']
        if self.__operator is None:
            self.__operator = '�����ߣ�'
        # ���Բ���������
        self.__data_s = config_dict['Data']
        # ��ǰ�Ľ׶�
        self.__current_process = config_dict['Process']
        self.__source_data = QStandardItemModel()
        self.__dest_data = QStandardItemModel()
        # ���׶ε��ر����
        self.__default_storage = None
        # ������������
        self.__sort_flags = {}
        # ���������������Ķ�Ӧ��ϵ
        self.__row_map = {}
        super( NHandleRequirementDialog, self ).__init__( parent )
        self.setModal( True )
        self.setup_ui()
        self.init_data()

    def setup_ui(self):
        super( NHandleRequirementDialog, self ).setupUi( self )
        main_layout = QVBoxLayout( self )
        self.setLayout( main_layout )

        splitter = QSplitter( Qt.Vertical )
        top_frame = QFrame()
        top_frame.setLayout( self.h2_layout )
        mid_frame = QFrame()
        mid_frame.setLayout( self.h2_2_layout )
        splitter.addWidget( self.sourceRequirementTableView )
        splitter.addWidget( mid_frame )
        splitter.addWidget( self.destRequirementTableView )
        mid_frame.setFixedHeight( 30 )

        main_layout.addWidget( top_frame )
        main_layout.addWidget( splitter )
        main_layout.addWidget( self.buttonBox )

        self.searchItemComboBox.addItems( ['����', '����', '��ע'] )
        self.searchItemComboBox.setCurrentIndex( 0 )

        self.sourceRequirementTableView.setModel( self.__source_data )
        self.sourceRequirementTableView.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.sourceRequirementTableView.setSelectionMode( QAbstractItemView.ExtendedSelection )
        self.sourceRequirementTableView.setEditTriggers( QAbstractItemView.NoEditTriggers )
        self.destRequirementTableView.setModel( self.__dest_data )
        self.destRequirementTableView.horizontalHeader().setStretchLastSection( True )
        self.destRequirementTableView.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.destRequirementTableView.setSelectionMode( QAbstractItemView.ExtendedSelection )
        self.__source_data.setHorizontalHeaderLabels(
            ['����', '�����', '����', '�е����ϱ���', '����', '���´���', '����', '��ע'] )
        dest_headers = ['�����', '����', '�е����ϱ���', '����', '��ע']
        if self.__current_process == 3:
            dest_headers.extend( ['��λ', 'ȥ˰����'] )
        self.__dest_data.setHorizontalHeaderLabels( dest_headers )
        readonly_delegate = ReadOnlyDelegate()
        for i in range( 3 ):
            self.destRequirementTableView.setItemDelegateForColumn( i, readonly_delegate )

        # һЩ��Ӧ����
        self.sourceRequirementTableView.horizontalHeader().sectionClicked.connect( self.__sort_by_column )
        self.pushForwardButton.clicked.connect( lambda: self.__how_to_handle_the_source( 1 ) )
        self.rollBackButton.clicked.connect( lambda: self.__how_to_handle_the_source( 2 ) )
        self.cancelRequirementButton.clicked.connect( lambda: self.__how_to_handle_the_source( 3 ) )
        self.destRequirementTableView.selectionModel().selectionChanged.connect( self.__dest_selected_changed )
        self.removeButton.clicked.connect( lambda: self.__how_to_handle_the_dest( 1 ) )

        # һЩ��ʼ������ʾ����
        current_title = self.windowTitle()
        if self.__current_process == 1:
            post_fix = 'Ͷ��'
        elif self.__current_process == 2:
            post_fix = '�ɹ�'
        elif self.__current_process == 3:
            post_fix = '���'
        else:
            post_fix = '�˿�'
        self.setWindowTitle( f'{current_title} - {post_fix}' )

        # ���ݲ�ͬ��ģʽĳЩ����Ҫ��������
        if self.__current_process == 1 or self.__current_process == 2:
            # Ͷ�Ϻ��ɹ������ܡ����ˡ���ֻ�ܡ�ǰ���������ϡ�
            self.rollBackButton.setEnabled( False )
        if self.__current_process == 4:
            # �˿�ʱ�����ܡ����ˡ��͡�ȡ����
            self.rollBackButton.setEnabled( False )
            self.cancelRequirementButton.setEnabled( False )

    def accept(self):
        when_do = QDate.currentDate().toString( 'yyMMdd' )
        try:
            next_process = 13
            bill_type = '��ⵥ'
            operation_data = []
            if self.__current_process == 1 or self.__current_process == 2:
                if self.__current_process == 1:
                    next_process = 11
                    bill_type = 'Ͷ�ϵ�'
                else:
                    next_process = 12
                    bill_type = '�ɹ���'
                operation_data = []
                record_count = self.__dest_data.rowCount()
                for i in range( record_count ):
                    # TODO Ҫ�����������֤
                    # TODO ��ⵥҪ�в�λ�����򷢳�����
                    first_item_in_row: QStandardItem = self.__dest_data.item( i, 0 )
                    link_item_nr = first_item_in_row.data( Qt.UserRole + 2 )
                    qty_item: QStandardItem = self.__dest_data.item( i, 3 )
                    the_qty = qty_item.data( Qt.EditRole )
                    comment_item: QStandardItem = self.__dest_data.item( i, 4 )
                    the_comment = comment_item.text()
                    operation_data.append( [link_item_nr, the_qty, the_comment] )
            elif self.__current_process == 3:
                record_count = self.__dest_data.rowCount()
                for i in range( record_count ):
                    first_item_in_row: QStandardItem = self.__dest_data.item( i, 0 )
                    link_item_nr = first_item_in_row.data( Qt.UserRole + 2 )
                    last_process_link = first_item_in_row.data( Qt.UserRole + 3 )
                    qty_item: QStandardItem = self.__dest_data.item( i, 3 )
                    the_qty = qty_item.data( Qt.EditRole )
                    comment_item: QStandardItem = self.__dest_data.item( i, 4 )
                    the_comment = comment_item.text()
                    storage_id = self.__dest_data.item( i, 5 ).text()
                    the_unit_price_temp = self.__dest_data.item( i, 6 ).data( Qt.EditRole )
                    the_unit_price = None
                    if the_unit_price_temp is not None:
                        the_unit_price_str = the_unit_price_temp.strip()
                        if len( the_unit_price_str ) > 0:
                            the_unit_price = float( the_unit_price_str )
                            if the_unit_price < 0.0001:
                                the_unit_price = None
                    operation_data.append(
                        [link_item_nr, the_qty, the_comment, last_process_link, storage_id, the_unit_price] )
            data = {'BillName': when_do, 'Operator': self.__operator,
                    'DoingDate': QDate.currentDate().toString( 'yyyy-MM-dd' ), 'BillType': bill_type,
                    'NextProcess': next_process, 'Items': operation_data}
            neu_bill_name = self.__database.create_supply_operation( data )
            if self.__current_process == 1:
                message = f'�������µ�Ͷ�ϵ��ţ�{neu_bill_name}'
            elif self.__current_process == 2:
                message = f'�������µ��ɹ����ţ�{neu_bill_name}'
            else:
                message = f'�������µ���ⵥ�ţ�{neu_bill_name}'
            QMessageBox.information( self, '���', message, QMessageBox.Ok, QMessageBox.Ok )
            self.close()
        except Exception as ex:
            QMessageBox.critical( self, '����', ex.__str__(), QMessageBox.Ok, QMessageBox.Ok )

    def __how_to_handle_the_dest(self, mode):
        """
        ���ݲ�ͬ��mode���������ƽ�������
        :param mode:
        :return:
        """
        selection_model: QItemSelectionModel = self.destRequirementTableView.selectionModel()
        indexes = selection_model.selectedIndexes()

        # ɾ����ѡ��������
        c = int( len( indexes ) / 5 )
        for i in range( c ):
            first_index: QModelIndex = indexes[i * 5]
            self.__dest_data.removeRow( first_index.row() )

    def __how_to_handle_the_source(self, mode):
        """
        ���ݲ�ͬ��mode�������Ѿ�ѡ��������
        :param mode: 1=����, 2=����, 3=����
        :return:
        """
        selection_model: QItemSelectionModel = self.sourceRequirementTableView.selectionModel()
        indexes = selection_model.selectedIndexes()

        if mode == 1:
            if self.__default_storage is None and self.__current_process == 3:
                # ����Ĭ�ϵĲ�λ
                text, ok = QInputDialog.getText( self, '����', 'Ĭ�ϲ�λ��' )
                if ok:
                    self.__default_storage = text

            cc = int( len( indexes ) / 8 )
            for i in range( cc ):
                # ��ȡԭ��������
                first_item: QStandardItem = self.__source_data.itemFromIndex( indexes[i * 8] )
                row_index = first_item.data( Qt.UserRole + 1 )
                require_item = first_item.data( Qt.UserRole + 2 )
                process_id = -1
                if self.__current_process == 3:
                    process_id = first_item.data( Qt.UserRole + 3 )
                the_row = self.__row_map[row_index]
                part_id = the_row[1].text()
                description = the_row[2].text()
                zd_erp = the_row[3].text()
                qty = the_row[4].data( Qt.DisplayRole )
                done_qty = the_row[5].data( Qt.DisplayRole )
                default_qty = qty - done_qty
                # TODO ���鲻Ҫ�ظ����
                # ����δ��������
                first_dest_item = QStandardItem( part_id )
                first_dest_item.setData( row_index, Qt.UserRole + 1 )
                first_dest_item.setData( require_item, Qt.UserRole + 2 )
                if self.__current_process == 3:
                    first_dest_item.setData( process_id, Qt.UserRole + 3 )
                new_dest_row = [first_dest_item, QStandardItem( description ), QStandardItem( zd_erp )]
                qty_item = QStandardItem()
                qty_item.setData( default_qty, Qt.DisplayRole )
                qty_item.setTextAlignment( Qt.AlignCenter )
                new_dest_row.extend( [qty_item, QStandardItem()] )
                if self.__current_process == 3:
                    # ���ʱ���һЩ���⹤��
                    storage_item = QStandardItem()
                    storage_item.setTextAlignment( Qt.AlignCenter )
                    if self.__default_storage is not None:
                        storage_item.setText( self.__default_storage )
                    unit_price_item = QStandardItem()
                    unit_price_item.setTextAlignment( Qt.AlignCenter )
                    new_dest_row.extend( [storage_item, unit_price_item] )
                self.__dest_data.appendRow( new_dest_row )
        elif mode == 2 or mode == 3:
            a_word = '����' if mode == 2 else '����'
            rsp = QMessageBox.question( self, '', f'ȷ��Ҫ����{a_word}����', QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No )
            if rsp == QMessageBox.No:
                return

            cc = int( len( indexes ) / 8 )
            for i in range( cc ):
                first_item: QStandardItem = self.__source_data.itemFromIndex( indexes[i * 8] )
                row_index = first_item.data( Qt.UserRole + 1 )
                require_item = first_item.data( Qt.UserRole + 2 )
                the_row = self.__row_map[row_index]
                qty = the_row[4].data( Qt.DisplayRole )
                done_qty = the_row[5].data( Qt.DisplayRole )
                default_qty = qty - done_qty
                if mode == 2:
                    # TODO ���С����ˡ�����
                    pass
                else:
                    if self.__current_process == 1 or self.__current_process == 2:
                        self.__database.cancel_material_requirement( require_item, default_qty )
                    elif self.__current_process == 3:
                        item_process_id = first_item.data( Qt.UserRole + 3 )
                        self.__database.cancel_supply_operation( item_process_id, default_qty )
            # ɾ��ԭ���ļ�¼
            for i in range( cc ):
                first_index: QModelIndex = indexes[i * 8]
                self.__source_data.removeRow( first_index.row() )

    def __dest_selected_changed(self, item_1, item_2):
        """
        Ŀ�����Ŀѡ�����ʱ����Ӧ����
        :return:
        """
        select_mode: QItemSelectionModel = self.destRequirementTableView.selectionModel()
        the_first_index = select_mode.selectedIndexes()
        if len( the_first_index ) < 1:
            return
        first_item = self.__dest_data.itemFromIndex( the_first_index[0] )
        i = first_item.data( Qt.UserRole + 1 )
        original_row = self.__row_map[i]
        original_index = self.__source_data.indexFromItem( original_row[0] )
        original_selection: QItemSelectionModel = self.sourceRequirementTableView.selectionModel()
        original_selection.clearSelection()
        original_selection.select( original_index, QItemSelectionModel.Select | QItemSelectionModel.Rows )

    def __sort_by_column(self, column_index):
        """
        �����ͷʱ���Ա����ݽ�������
        :param column_index:
        :return:
        """
        sort_flags = False
        if column_index in self.__sort_flags:
            sort_flags = self.__sort_flags[column_index]
        if sort_flags:
            self.sourceRequirementTableView.sortByColumn( column_index, Qt.AscendingOrder )
            sort_flags = False
        else:
            self.sourceRequirementTableView.sortByColumn( column_index, Qt.DescendingOrder )
            sort_flags = True
        self.__sort_flags[column_index] = sort_flags

    def init_data(self):
        """
        ��ʼ������
        :return:
        """
        i = 0
        for d in self.__data_s[1]:
            part_id = d[2]
            parts = Part.get_parts( self.__database, part_id=part_id )
            if parts is not None and len( parts ) > 0:
                the_part = parts[0]
                part_id = the_part.part_id
                description = the_part.name
                if the_part.description is not None:
                    description += ' {0}'.format( the_part.description )
            elif d[3] is not None:
                temp_description = self.__database.get_erp_info( d[3] )
                if temp_description is None:
                    description = "�������ݣ�"
                else:
                    description = self.__database.get_erp_info( d[3] )[1]
            else:
                QMessageBox.warning( self, '', '������������', QMessageBox.Ok, QMessageBox.Ok )
                continue
            first_item = QStandardItem( d[0] )
            # ��ÿ�е��׸���Ԫ�����ϼǺ�
            first_item.setData( i, Qt.UserRole + 1 )
            first_item.setData( d[1], Qt.UserRole + 2 )
            if self.__current_process == 3:
                # �н�֮ǰ�� Supply Operation �� Id
                first_item.setData( d[9], Qt.UserRole + 3 )
            one_row = [first_item]
            one_row.extend( [QStandardItem( part_id ), QStandardItem( description ), QStandardItem( d[3] )] )
            qty_item = QStandardItem( d[5] )
            # ֱ�� QStandardItem.setData( Decimal, Qt.DisplayRole ) �޷���ʾ��
            qty_item.setData( float( d[5] ), Qt.DisplayRole )
            qty_item.setTextAlignment( Qt.AlignCenter )
            one_row.append( qty_item )
            u_doing_qty = d[6] + d[7]
            u_qty_item = QStandardItem( u_doing_qty )
            u_qty_item.setData( float( u_doing_qty ), Qt.DisplayRole )
            u_qty_item.setTextAlignment( Qt.AlignCenter )
            one_row.append( u_qty_item )
            one_row.append( QStandardItem( d[4].strftime( '%Y/%m/%d' ) ) )
            one_row.append( QStandardItem( d[8] ) )
            self.__row_map[i] = one_row
            self.__source_data.appendRow( one_row )
            i += 1
        self.sourceRequirementTableView.resizeColumnsToContents()
        self.sourceRequirementTableView.horizontalHeader().setStretchLastSection( True )
        self.sourceRequirementTableView.horizontalHeader().setSectionsClickable( True )
        self.sourceRequirementTableView.horizontalHeader().setSortIndicatorShown( True )


class ReadOnlyDelegate( QItemDelegate ):

    def createEditor(self, parent, option, index):
        return None

    def __init__(self, parent=None):
        super().__init__( parent )
