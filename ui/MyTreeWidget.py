import sys

from PyQt5.QtCore import (Qt, QMimeData)
from PyQt5.QtGui import (QDragEnterEvent, QDragMoveEvent, QDropEvent, QDrag, QKeyEvent, QMouseEvent, QStandardItem,
                         QStandardItemModel)
from PyQt5.QtWidgets import (QTreeWidget, QAbstractItemView, QApplication,
                             QTreeWidgetItem, QMessageBox, QInputDialog, QLineEdit, QTreeView)

from Part import Tag


class MyTreeView( QTreeView ):

    def __init__(self, parent, database):
        super( MyTreeView, self ).__init__( parent )
        self.__parent = parent
        self.__database = database
        self.__could_drag = False
        self.__multi_select = False
        self.__item_at_context_menu: QStandardItem = None
        self.setEditTriggers( QAbstractItemView.NoEditTriggers )
        # self.setDropIndicatorShown( True )
        # self.setDragDropMode( QAbstractItemView.InternalMove )

    def set_edit_mode(self, edit_mode):
        self.__could_drag = edit_mode
        # self.setDragEnabled( edit_mode )
        # self.setAcceptDrops( edit_mode )

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Control and self.__could_drag:
            self.__multi_select = True
            self.setSelectionMode( QAbstractItemView.ExtendedSelection )

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Control and self.__could_drag:
            self.__multi_select = False
            self.setSelectionMode( QAbstractItemView.SingleSelection )

    def startDrag(self, event):
        if not self.__could_drag:
            return
        item = self.currentItem()
        if item is None:
            return
        drag = QDrag( self )
        drag.setMimeData( MyTreeItemMimeData( 'tag', item ) )
        drag.exec( Qt.MoveAction )

    def dragMoveEvent(self, event: QDragMoveEvent):
        target = self.itemAt( event.pos() )
        event.setDropAction( Qt.MoveAction )
        source = event.mimeData().drag_item()
        if target:
            if source.parent() is target.parent():
                parent_item = source.parent()
                if parent_item is not None:
                    ss = parent_item.indexOfChild( source ) - parent_item.indexOfChild( target )
                else:
                    ss = self.indexOfTopLevelItem( source ) - self.indexOfTopLevelItem( target )
                if ss == 1 or ss == 0:
                    event.ignore()
                else:
                    event.accept()
            elif source.parent() is target:
                event.accept()
                self.__show_message( '移动到该队列的最前端。' )
            else:
                event.ignore()
                self.__show_message( '只能在同级间移动。' )
        else:
            if source.parent() is None:
                event.accept()
            else:
                event.ignore()
                self.__show_message( '只能在同级间移动。' )

    def dragEnterEvent(self, event: QDragEnterEvent):
        event.accept()

    def __show_message(self, message):
        if self.__parent is not None:
            self.__parent.set_status_message( message )
        else:
            print( message )

    def dropEvent(self, event: QDropEvent):
        source = event.mimeData().drag_item()
        target = self.itemAt( event.pos() )
        if source == target:
            event.ignore()
            return
        do_save = False
        if target is None:
            if source.parent() is None:
                self.takeTopLevelItem( self.indexOfTopLevelItem( source ) )
                self.insertTopLevelItem( 0, source )
                do_save = True
        else:
            do_save = True
            if source.parent() is target:
                target.removeChild( source )
                target.insertChild( 0, source )
            elif target.parent() is None:
                self.takeTopLevelItem( self.indexOfTopLevelItem( source ) )
                self.insertTopLevelItem( self.indexOfTopLevelItem( target ) + 1, source )
            else:
                parent_item = target.parent()
                parent_item.removeChild( source )
                parent_item.insertChild( parent_item.indexOfChild( target ) + 1, source )
        if do_save and self.__database is not None:
            self.__save_node_sort( source )
            self.__database.save_change()
        event.setDropAction( Qt.MoveAction )
        event.accept()
        super().dropEvent( event )

    def __save_node_sort(self, source: QTreeWidgetItem):
        if source.parent() is None:
            tc = self.topLevelItemCount()
            for ii in range( tc ):
                n = self.topLevelItem( ii )
                self.__save_tag_sort( n, ii )
        else:
            pp = source.parent()
            tc = pp.childCount()
            for ii in range( tc ):
                n = pp.child( ii )
                self.__save_tag_sort( n, ii )

    def __save_tag_sort(self, item, index):
        t = item.data( 0, Qt.UserRole )
        tag_id = t.tag_id
        self.__database.sort_one_tag_to_index( tag_id, index )

    def item_when_right_click(self, item: QStandardItem):
        self.__item_at_context_menu = item

    def create_new_tag(self):
        text, ok_pressed = QInputDialog.getText( self.__parent, '新建标签', '标签名：', QLineEdit.Normal, '' )
        if ok_pressed and text != '':
            top_level = False
            if self.__item_at_context_menu is None:
                tag_id = self.__database.create_one_tag( text, None )
                top_level = True
            else:
                the_tag: Tag = self.__item_at_context_menu.data( Qt.UserRole )
                tag_id = self.__database.create_one_tag( text, the_tag.tag_id )
            new_tag = Tag.get_tags( self.__database, tag_id=tag_id )[0]
            new_node: QStandardItem = QStandardItem()
            new_node.setText( text )
            new_node.setData( new_tag, Qt.UserRole )
            if top_level:
                m: QStandardItemModel = self.model()
                m.appendRow( new_node )
            else:
                self.__item_at_context_menu.appendRow( new_node )

    def del_tag(self):
        ii: QStandardItem = self.__item_at_context_menu
        if ii.hasChildren():
            QMessageBox.warning( self.__parent, '', '存在子标签的标签不能删除。', QMessageBox.Ok )
            return
        resp = QMessageBox.question( self.__parent, '确认', '确定要删除该标签？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No )
        if resp is QMessageBox.No:
            return
        the_tag: Tag = ii.data( Qt.UserRole )
        self.__database.del_one_tag( the_tag.tag_id )
        if ii.parent() is None:
            self.model().removeRow( ii.row() )
        else:
            ii.parent().removeRow( ii.row() )

    def rename_tag(self):
        ii: QStandardItem = self.__item_at_context_menu
        the_tag: Tag = ii.data( Qt.UserRole )
        tag_name = the_tag.name
        text, ok_pressed = QInputDialog.getText( self.__parent, '重命名标签', '标签名：', QLineEdit.Normal, tag_name )
        if ok_pressed and text != '':
            self.__database.rename_one_tag( the_tag.tag_id, text )
            ii.setText( text )
            the_tag.name = text
            ii.setData( the_tag, Qt.UserRole )

    def sort_tag(self):
        ii: QStandardItem = self.__item_at_context_menu
        the_tag: Tag = ii.data( Qt.UserRole )
        done_tag = the_tag.sort_children_by_name( self.__database )
        if done_tag[0]:
            new_children = done_tag[1]
            ii.removeRows( 0, ii.rowCount() )
            for cc in new_children:
                nn = QStandardItem( cc.name )
                nn.setData( cc, Qt.UserRole )
                ii.appendRow( nn )
        self.__database.save_change()

    def cut_tag(self):
        items = []
        if self.__multi_select:
            all_items = self.selectedItems()
            items_dict = {}
            for ii in all_items:
                items_dict[self.__get_item_index( ii )] = ii
            sort_keys = sorted( items_dict )
            for k in sort_keys:
                items.append( items_dict[k] )
        else:
            items.append( self.currentItem() )
        if len( items ) < 1:
            return
        old_parent = items[0].parent()
        if len( items ) > 1:
            count = len( items )
            for ii in range( 1, count ):
                n_item = items[ii].parent()
                if old_parent is not n_item:
                    QMessageBox.warning( self.__parent, '', '不同级别的节点无法进行剪切操作。', QMessageBox.Ok )
                    return
        if old_parent is None:
            for item in items:
                self.takeTopLevelItem( self.indexOfTopLevelItem( item ) )
        else:
            for item in items:
                old_parent.takeChild( old_parent.indexOfChild( item ) )
        for item in items:
            t: Tag = item.data( 0, Qt.UserRole )
            # 将 tag 放置在一个名为“剪切板”的 tag 下面，编号为0。
            self.__database.set_tag_parent( t.tag_id, 0 )
        self.__database.save_change()

    def __get_item_index(self, item: QTreeWidgetItem):
        if item.parent() is None:
            return self.indexOfTopLevelItem( item )
        else:
            pp = item.parent()
            return pp.indexOfChild( item )

    def paste_tag_into(self, to_item):
        if self.__multi_select:
            QMessageBox.warning( self.__parent, '', '按下 Ctrl 时，不允许进行粘帖操作。', QMessageBox.Ok )
            return
        items = Tag.get_tags( self.__database, parent_id=0 )
        if to_item is None:
            last_top_index = self.topLevelItemCount()
            ii = QTreeWidgetItem( self )
            t = items[0]
            ii.setText( 0, t.name )
            self.__database.set_tag_parent( t.tag_id, None )
            ii.setData( 0, Qt.UserRole, t )
            self.insertTopLevelItem( last_top_index, ii )
            cc = 1
            f_ii = ii
            for i in range( 1, len( items ) ):
                t = items[i]
                ii = QTreeWidgetItem( self )
                ii.setText( 0, t.name )
                ii.setData( 0, Qt.UserRole, t )
                self.__database.set_tag_parent( t.tag_id, None )
                self.insertTopLevelItem( last_top_index + cc, ii )
                cc += 1
            self.__save_node_sort( f_ii )
        else:
            resp = QMessageBox.question( self.__parent, '', '同级粘帖？',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
            if resp == QMessageBox.Yes:
                """ 同级粘帖 """
                to_index = self.__get_item_index( to_item ) + 1
                pp = to_item.parent()
                if pp is None:
                    for t in items:
                        ii = QTreeWidgetItem( self )
                        ii.setText( 0, t.name )
                        ii.setData( 0, Qt.UserRole, t )
                        self.insertTopLevelItem( to_index, ii )
                        self.__database.set_tag_parent( t.tag_id, None )
                        to_index += 1
                else:
                    p_t: Tag = pp.data( 0, Qt.UserRole )
                    for t in items:
                        ii = QTreeWidgetItem( pp )
                        ii.setText( 0, t.name )
                        ii.setData( 0, Qt.UserRole, t )
                        self.__database.set_tag_parent( t.tag_id, p_t.tag_id )
                        pp.insertChild( to_index, ii )
                        to_index += 1
                self.__save_node_sort( to_item )
            elif resp == QMessageBox.No:
                """ 粘帖至下一级 """
                to_index = to_item.childCount()
                p_t: Tag = to_item.data( 0, Qt.UserRole )
                ii = QTreeWidgetItem( to_item )
                ii.setText( 0, items[0].name )
                ii.setData( 0, Qt.UserRole, items[0] )
                f_ii = ii
                self.__database.set_tag_parent( items[0].tag_id, p_t.tag_id )
                to_item.insertChild( to_index, ii )
                to_index += 1
                for i in range( 1, len( items ) ):
                    t = items[i]
                    ii = QTreeWidgetItem( to_item )
                    ii.setText( 0, t.name )
                    ii.setData( 0, Qt.UserRole, t )
                    self.__database.set_tag_parent( t.tag_id, p_t.tag_id )
                    to_item.insertChild( to_index, ii )
                    to_index += 1
                self.__save_node_sort( f_ii )
                if not to_item.isExpanded():
                    to_item.setExpanded( True )
        self.__database.save_change()

    def mousePressEvent(self, e: QMouseEvent) -> None:
        index = self.indexAt( e.pos() )
        if index.row() == -1:
            self.setCurrentIndex( index )
        else:
            super( MyTreeView, self ).mousePressEvent( e )

    @staticmethod
    def clipper_not_empty(database):
        tags = database.get_tags( parent_id=0 )
        return len( tags ) > 0


class MyTreeWidget2( QTreeWidget ):
    """ 只能进行同级拖拽的功能 """

    def __init__(self, parent, database=None):
        self.__parent = parent
        self.__database = database
        self.__could_drag = False
        self.__multi_select = False
        self.__item_at_context_menu = None
        super().__init__( parent=parent )
        self.setDropIndicatorShown( True )
        self.setDragDropMode( QAbstractItemView.InternalMove )

    def set_edit_mode(self, edit_mode):
        self.__could_drag = edit_mode
        self.setDragEnabled( edit_mode )
        self.setAcceptDrops( edit_mode )

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Control and self.__could_drag:
            self.__multi_select = True
            self.setSelectionMode( QAbstractItemView.ExtendedSelection )

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Control and self.__could_drag:
            self.__multi_select = False
            self.setSelectionMode( QAbstractItemView.SingleSelection )

    def startDrag(self, event):
        if not self.__could_drag:
            return
        item = self.currentItem()
        if item is None:
            return
        drag = QDrag( self )
        drag.setMimeData( MyTreeItemMimeData( 'tag', item ) )
        drag.exec( Qt.MoveAction )

    def dragMoveEvent(self, event: QDragMoveEvent):
        target = self.itemAt( event.pos() )
        event.setDropAction( Qt.MoveAction )
        source = event.mimeData().drag_item()
        if target:
            if source.parent() is target.parent():
                parent_item = source.parent()
                if parent_item is not None:
                    ss = parent_item.indexOfChild( source ) - parent_item.indexOfChild( target )
                else:
                    ss = self.indexOfTopLevelItem( source ) - self.indexOfTopLevelItem( target )
                if ss == 1 or ss == 0:
                    event.ignore()
                else:
                    event.accept()
            elif source.parent() is target:
                event.accept()
                self.__show_message( '移动到该队列的最前端。' )
            else:
                event.ignore()
                self.__show_message( '只能在同级间移动。' )
        else:
            if source.parent() is None:
                event.accept()
            else:
                event.ignore()
                self.__show_message( '只能在同级间移动。' )

    def dragEnterEvent(self, event: QDragEnterEvent):
        event.accept()

    def __show_message(self, message):
        if self.__parent is not None:
            self.__parent.set_status_message( message )
        else:
            print( message )

    def dropEvent(self, event: QDropEvent):
        source = event.mimeData().drag_item()
        target = self.itemAt( event.pos() )
        if source == target:
            event.ignore()
            return
        do_save = False
        if target is None:
            if source.parent() is None:
                self.takeTopLevelItem( self.indexOfTopLevelItem( source ) )
                self.insertTopLevelItem( 0, source )
                do_save = True
        else:
            do_save = True
            if source.parent() is target:
                target.removeChild( source )
                target.insertChild( 0, source )
            elif target.parent() is None:
                self.takeTopLevelItem( self.indexOfTopLevelItem( source ) )
                self.insertTopLevelItem( self.indexOfTopLevelItem( target ) + 1, source )
            else:
                parent_item = target.parent()
                parent_item.removeChild( source )
                parent_item.insertChild( parent_item.indexOfChild( target ) + 1, source )
        if do_save and self.__database is not None:
            self.__save_node_sort( source )
            self.__database.save_change()
        event.setDropAction( Qt.MoveAction )
        event.accept()
        super().dropEvent( event )

    def __save_node_sort(self, source: QTreeWidgetItem):
        if source.parent() is None:
            tc = self.topLevelItemCount()
            for ii in range( tc ):
                n = self.topLevelItem( ii )
                self.__save_tag_sort( n, ii )
        else:
            pp = source.parent()
            tc = pp.childCount()
            for ii in range( tc ):
                n = pp.child( ii )
                self.__save_tag_sort( n, ii )

    def __save_tag_sort(self, item, index):
        t = item.data( 0, Qt.UserRole )
        tag_id = t.tag_id
        self.__database.sort_one_tag_to_index( tag_id, index )

    def item_when_right_click(self, item):
        self.__item_at_context_menu = item

    def create_new_tag(self):
        text, ok_pressed = QInputDialog.getText( self.__parent, '新建标签', '标签名：', QLineEdit.Normal, '' )
        if ok_pressed and text != '':
            top_level = False
            if self.__item_at_context_menu is None:
                tag_id = self.__database.create_one_tag( text, None )
                top_level = True
                p_node = self
            else:
                the_tag: Tag = self.__item_at_context_menu.data( 0, Qt.UserRole )
                tag_id = self.__database.create_one_tag( text, the_tag.tag_id )
                p_node = self.__item_at_context_menu
            new_tag = Tag.get_tags( self.__database, tag_id=tag_id )[0]
            new_node: QTreeWidgetItem = QTreeWidgetItem( p_node )
            new_node.setText( 0, text )
            new_node.setData( 0, Qt.UserRole, new_tag )
            if top_level:
                self.addTopLevelItem( new_node )
            else:
                # 有问题？建立 QTreeWidgetItem 时，应该注意构造函数的参数。
                ii: QTreeWidgetItem = self.__item_at_context_menu
                ii.addChild( new_node )

    def del_tag(self):
        ii: QTreeWidgetItem = self.__item_at_context_menu
        if ii.childCount() > 0:
            QMessageBox.warning( self.__parent, '', '存在子标签的标签不能删除。', QMessageBox.Ok )
            return
        resp = QMessageBox.question( self.__parent, '确认', '确定要删除该标签？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No )
        if resp is QMessageBox.No:
            return
        the_tag: Tag = ii.data( 0, Qt.UserRole )
        self.__database.del_one_tag( the_tag.tag_id )
        if the_tag.parent_id is None:
            index = self.indexOfTopLevelItem( ii )
            self.takeTopLevelItem( index )
        else:
            parent = ii.parent()
            index = parent.indexOfChild( ii )
            parent.takeChild( index )

    def rename_tag(self):
        ii: QTreeWidgetItem = self.__item_at_context_menu
        the_tag: Tag = ii.data( 0, Qt.UserRole )
        tag_name = the_tag.name
        text, ok_pressed = QInputDialog.getText( self.__parent, '重命名标签', '标签名：', QLineEdit.Normal, tag_name )
        if ok_pressed and text != '':
            self.__database.rename_one_tag( the_tag.tag_id, text )
            ii.setText( 0, text )
            the_tag.name = text
            ii.setData( 0, Qt.UserRole, the_tag )

    def sort_tag(self):
        ii: QTreeWidgetItem = self.__item_at_context_menu
        the_tag: Tag = ii.data( 0, Qt.UserRole )
        done_tag = the_tag.sort_children_by_name( self.__database )
        if done_tag[0]:
            new_children = done_tag[1]
            ii.takeChildren()
            for cc in new_children:
                nn = QTreeWidgetItem( ii )
                nn.setText( 0, cc.name )
                nn.setData( 0, Qt.UserRole, cc )
                ii.addChild( nn )
        self.__database.save_change()

    def cut_tag(self):
        items = []
        if self.__multi_select:
            all_items = self.selectedItems()
            items_dict = {}
            for ii in all_items:
                items_dict[self.__get_item_index( ii )] = ii
            sort_keys = sorted( items_dict )
            for k in sort_keys:
                items.append( items_dict[k] )
        else:
            items.append( self.currentItem() )
        if len( items ) < 1:
            return
        old_parent = items[0].parent()
        if len( items ) > 1:
            count = len( items )
            for ii in range( 1, count ):
                n_item = items[ii].parent()
                if old_parent is not n_item:
                    QMessageBox.warning( self.__parent, '', '不同级别的节点无法进行剪切操作。', QMessageBox.Ok )
                    return
        if old_parent is None:
            for item in items:
                self.takeTopLevelItem( self.indexOfTopLevelItem( item ) )
        else:
            for item in items:
                old_parent.takeChild( old_parent.indexOfChild( item ) )
        for item in items:
            t: Tag = item.data( 0, Qt.UserRole )
            # 将 tag 放置在一个名为“剪切板”的 tag 下面，编号为0。
            self.__database.set_tag_parent( t.tag_id, 0 )
        self.__database.save_change()

    def __get_item_index(self, item: QTreeWidgetItem):
        if item.parent() is None:
            return self.indexOfTopLevelItem( item )
        else:
            pp = item.parent()
            return pp.indexOfChild( item )

    def paste_tag_into(self, to_item):
        if self.__multi_select:
            QMessageBox.warning( self.__parent, '', '按下 Ctrl 时，不允许进行粘帖操作。', QMessageBox.Ok )
            return
        items = Tag.get_tags( self.__database, parent_id=0 )
        if to_item is None:
            last_top_index = self.topLevelItemCount()
            ii = QTreeWidgetItem( self )
            t = items[0]
            ii.setText( 0, t.name )
            self.__database.set_tag_parent( t.tag_id, None )
            ii.setData( 0, Qt.UserRole, t )
            self.insertTopLevelItem( last_top_index, ii )
            cc = 1
            f_ii = ii
            for i in range( 1, len( items ) ):
                t = items[i]
                ii = QTreeWidgetItem( self )
                ii.setText( 0, t.name )
                ii.setData( 0, Qt.UserRole, t )
                self.__database.set_tag_parent( t.tag_id, None )
                self.insertTopLevelItem( last_top_index + cc, ii )
                cc += 1
            self.__save_node_sort( f_ii )
        else:
            resp = QMessageBox.question( self.__parent, '', '同级粘帖？',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
            if resp == QMessageBox.Yes:
                """ 同级粘帖 """
                to_index = self.__get_item_index( to_item ) + 1
                pp = to_item.parent()
                if pp is None:
                    for t in items:
                        ii = QTreeWidgetItem( self )
                        ii.setText( 0, t.name )
                        ii.setData( 0, Qt.UserRole, t )
                        self.insertTopLevelItem( to_index, ii )
                        self.__database.set_tag_parent( t.tag_id, None )
                        to_index += 1
                else:
                    p_t: Tag = pp.data( 0, Qt.UserRole )
                    for t in items:
                        ii = QTreeWidgetItem( pp )
                        ii.setText( 0, t.name )
                        ii.setData( 0, Qt.UserRole, t )
                        self.__database.set_tag_parent( t.tag_id, p_t.tag_id )
                        pp.insertChild( to_index, ii )
                        to_index += 1
                self.__save_node_sort( to_item )
            elif resp == QMessageBox.No:
                """ 粘帖至下一级 """
                to_index = to_item.childCount()
                p_t: Tag = to_item.data( 0, Qt.UserRole )
                ii = QTreeWidgetItem( to_item )
                ii.setText( 0, items[0].name )
                ii.setData( 0, Qt.UserRole, items[0] )
                f_ii = ii
                self.__database.set_tag_parent( items[0].tag_id, p_t.tag_id )
                to_item.insertChild( to_index, ii )
                to_index += 1
                for i in range( 1, len( items ) ):
                    t = items[i]
                    ii = QTreeWidgetItem( to_item )
                    ii.setText( 0, t.name )
                    ii.setData( 0, Qt.UserRole, t )
                    self.__database.set_tag_parent( t.tag_id, p_t.tag_id )
                    to_item.insertChild( to_index, ii )
                    to_index += 1
                self.__save_node_sort( f_ii )
                if not to_item.isExpanded():
                    to_item.setExpanded( True )
        self.__database.save_change()

    def mousePressEvent(self, e: QMouseEvent) -> None:
        index = self.indexAt( e.pos() )
        if index.row() == -1:
            self.setCurrentIndex( index )
        else:
            super( MyTreeWidget2, self ).mousePressEvent( e )

    @staticmethod
    def clipper_not_empty(database):
        tags = database.get_tags( parent_id=0 )
        return len( tags ) > 0


class MyTreeItemMimeData( QMimeData ):
    """ 用于在拖拽中传递数据 """

    def __init__(self, mime_type, item):
        super().__init__()
        self.__mime_type = mime_type
        self.__item = item

    def drag_item(self):
        return self.__item

    def what_kind(self, mime_type):
        return mime_type == self.__mime_type


if __name__ == '__main__':
    app = QApplication( sys.argv )
    w = MyTreeWidget2( None )
    root = QTreeWidgetItem()
    root.setText( 0, 'AAA' )
    w.insertTopLevelItem( 0, root )
    w.set_edit_mode( True )
    children = ['BB', 'CC', 'DD']
    for c in children:
        i = QTreeWidgetItem()
        i.setText( 0, c )
        root.insertChild( 0, i )
    w.show()
    sys.exit( app.exec_() )
