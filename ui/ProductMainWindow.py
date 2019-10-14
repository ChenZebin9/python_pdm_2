# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProductMainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(722, 606)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMaximumSize(QtCore.QSize(716, 16777215))
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 801, 551))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.productTab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.productTab.sizePolicy().hasHeightForWidth())
        self.productTab.setSizePolicy(sizePolicy)
        self.productTab.setObjectName("productTab")
        self.tabWidget.addTab(self.productTab, "")
        self.customerTab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.customerTab.sizePolicy().hasHeightForWidth())
        self.customerTab.setSizePolicy(sizePolicy)
        self.customerTab.setObjectName("customerTab")
        self.tabWidget.addTab(self.customerTab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 722, 26))
        self.menubar.setObjectName("menubar")
        self.productTopMenu = QtWidgets.QMenu(self.menubar)
        self.productTopMenu.setObjectName("productTopMenu")
        self.customerTopMenu = QtWidgets.QMenu(self.menubar)
        self.customerTopMenu.setObjectName("customerTopMenu")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.exitAction = QtWidgets.QAction(MainWindow)
        self.exitAction.setObjectName("exitAction")
        self.addProductAction = QtWidgets.QAction(MainWindow)
        self.addProductAction.setObjectName("addProductAction")
        self.productTopMenu.addAction(self.addProductAction)
        self.menu.addAction(self.exitAction)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.productTopMenu.menuAction())
        self.menubar.addAction(self.customerTopMenu.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "产品管理"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.productTab), _translate("MainWindow", "产品"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.customerTab), _translate("MainWindow", "客户"))
        self.productTopMenu.setTitle(_translate("MainWindow", "产品"))
        self.customerTopMenu.setTitle(_translate("MainWindow", "客户"))
        self.menu.setTitle(_translate("MainWindow", "全局"))
        self.exitAction.setText(_translate("MainWindow", "退出"))
        self.exitAction.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.addProductAction.setText(_translate("MainWindow", "添加产品"))
