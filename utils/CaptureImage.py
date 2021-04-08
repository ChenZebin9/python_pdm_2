import binascii
import os
import sys
import tempfile

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QRect, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QBitmap, QPainter, QPen, QBrush, QPixmap
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class WScreenShot( QDialog ):
    win = ''
    image_file = None

    @classmethod
    def run(cls):
        cls.win = cls()
        cls.win.show()

    def __init__(self, parent=None):
        super( WScreenShot, self ).__init__( parent )
        self.__parent = parent
        self.setWindowFlags( Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint )
        self.setStyleSheet( '''background-color:black; ''' )
        self.setWindowOpacity( 0.6 )
        # desktop = QApplication.desktop()
        # desktopRect = desktop.availableGeometry()
        desktopRect = QDesktopWidget().screenGeometry()
        # TODO 多屏幕时的处理
        # if QDesktopWidget().screenCount() > 1:
        #     right = desktopRect.right() * (QDesktopWidget().screenCount() - 1)
        #     desktopRect.adjust( 0, 0, right, 0 )
        self.setGeometry( desktopRect )
        self.setCursor( Qt.CrossCursor )
        self.blackMask = QBitmap( desktopRect.size() )
        self.blackMask.fill( Qt.black )
        self.mask = self.blackMask.copy()
        self.isDrawing = False
        self.startPoint = QPoint()
        self.endPoint = QPoint()

    def paintEvent(self, event):
        if self.isDrawing:
            self.mask = self.blackMask.copy()
            pp = QPainter( self.mask )
            pen = QPen()
            pen.setStyle( Qt.NoPen )
            pp.setPen( pen )
            brush = QBrush( Qt.white )
            pp.setBrush( brush )
            pp.drawRect( QRect( self.startPoint, self.endPoint ) )
            self.setMask( QBitmap( self.mask ) )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPoint = event.pos()
            self.endPoint = self.startPoint
            self.isDrawing = True

    def mouseMoveEvent(self, event):
        if self.isDrawing:
            self.endPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.endPoint = event.pos()
            # PySide2
            # screenshot = QPixmap.grabWindow(QApplication.desktop().winId())
            # PyQt5
            # screenshot = QApplication.primaryScreen().grabWindow(0)
            # 通用
            screenshot = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId())

            # 试图改进多屏显示
            # i = 0
            # for s in QApplication.screens():
            #     ss = s.grabWindow(QApplication.desktop().winId())
            #     ss.save(f'D:/tttt_{i}.jpg', format='JPG', quality=100)
            #     i += 1
            # screenshot = QApplication.screenAt(self.startPoint).grabWindow(QApplication.desktop().winId())
            # screenshot.save( 'D:/tttt.jpg', format='JPG', quality=100 )

            rect = QRect( self.startPoint, self.endPoint )
            outputRegion = screenshot.copy( rect )
            # 生成一个临时文件
            tmp_fd, temp_filename = tempfile.mkstemp( suffix='.jpg' )
            WScreenShot.image_file = temp_filename
            outputRegion.save( temp_filename, format='JPG', quality=100 )
            os.close( tmp_fd )
            self.close()

    def keyReleaseEvent(self, event):
        if event.button() == Qt.Key_Escape:
            WScreenShot.image_file = None
            self.close()

    @staticmethod
    def __joinImages(images):
        """
        水平拼接图片
        :param images: 图片的列表
        :return:
        """
        width = 0
        height = 0
        for i in images:
            img: QPixmap = i
            width += img.width()
            if img.height() > height:
                height = img.height()
        new_image = QPixmap( width, height )

        painter = QPainter()
        painter.begin( new_image )
        x_number = 0
        for i in images:
            img: QPixmap = i
            painter.drawPixmap( x_number, 0, img )
            x_number += img.width()
        painter.end()

        return new_image


class ConfirmImage( QDialog ):

    def __init__(self, image_file, parent=None):
        super( ConfirmImage, self ).__init__( parent )
        self.__image = image_file
        self.__image_data = None

        self.setWindowTitle( '确认图片？' )
        self.setFixedSize( 300, 340 )
        flags = self.windowFlags()
        self.setWindowFlags( flags | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint )
        v_layout = QVBoxLayout()

        image_label = QLabel()
        image_label.setAlignment( Qt.AlignCenter )
        img = QPixmap( image_file )
        self.__display_image = img.scaled( 300, 300, aspectRatioMode=Qt.KeepAspectRatio )
        image_label.setPixmap( self.__display_image )
        v_layout.addWidget( image_label )

        self.buttonBox = QDialogButtonBox( self )
        self.buttonBox.setOrientation( Qt.Horizontal )
        self.buttonBox.setStandardButtons( QDialogButtonBox.Yes | QDialogButtonBox.No )
        v_layout.addWidget( self.buttonBox )

        self.setLayout( v_layout )

        self.buttonBox.accepted.connect( self.accept )
        self.buttonBox.rejected.connect( self.reject )

    def accept(self):
        ba = QByteArray()
        bu = QBuffer( ba )
        bu.open( QIODevice.WriteOnly )
        ok = self.__display_image.save( bu, 'jpg' )
        if ok:
            data = '0x'.encode( 'ascii' ) + binascii.hexlify( ba )
            self.__image_data = data
        self.reject()

    def reject(self):
        super( ConfirmImage, self ).reject()

    def keyReleaseEvent(self, event):
        if event.button() == Qt.Key_Escape:
            self.reject()

    def get_img_data(self):
        return self.__image_data


if __name__ == '__main__':
    app = QApplication( sys.argv )
    WScreenShot.run()
    app.exec_()
    print( WScreenShot.image_file )
    os.unlink( WScreenShot.image_file )
