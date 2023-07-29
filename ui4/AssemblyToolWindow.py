# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AssemblyToolWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(919, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 919, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(self.menubar)
        self.menu_3.setObjectName("menu_3")
        self.menu_4 = QtWidgets.QMenu(self.menu_3)
        self.menu_4.setObjectName("menu_4")
        self.menu_7 = QtWidgets.QMenu(self.menu_3)
        self.menu_7.setObjectName("menu_7")
        self.menu_5 = QtWidgets.QMenu(self.menubar)
        self.menu_5.setObjectName("menu_5")
        self.menu_6 = QtWidgets.QMenu(self.menu_5)
        self.menu_6.setObjectName("menu_6")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.quitAction = QtWidgets.QAction(MainWindow)
        self.quitAction.setObjectName("quitAction")
        self.addProgressAction = QtWidgets.QAction(MainWindow)
        self.addProgressAction.setObjectName("addProgressAction")
        self.calculationMaterialAction = QtWidgets.QAction(MainWindow)
        self.calculationMaterialAction.setObjectName("calculationMaterialAction")
        self.noKbnAction = QtWidgets.QAction(MainWindow)
        self.noKbnAction.setCheckable(True)
        self.noKbnAction.setChecked(True)
        self.noKbnAction.setObjectName("noKbnAction")
        self.importZdStoringAction = QtWidgets.QAction(MainWindow)
        self.importZdStoringAction.setObjectName("importZdStoringAction")
        self.importJlStoringAction = QtWidgets.QAction(MainWindow)
        self.importJlStoringAction.setObjectName("importJlStoringAction")
        self.importSiteStoringAction = QtWidgets.QAction(MainWindow)
        self.importSiteStoringAction.setObjectName("importSiteStoringAction")
        self.generateBomAction = QtWidgets.QAction(MainWindow)
        self.generateBomAction.setObjectName("generateBomAction")
        self.action_3 = QtWidgets.QAction(MainWindow)
        self.action_3.setObjectName("action_3")
        self.action_4 = QtWidgets.QAction(MainWindow)
        self.action_4.setObjectName("action_4")
        self.action_6 = QtWidgets.QAction(MainWindow)
        self.action_6.setObjectName("action_6")
        self.importZdFoundationDataAction = QtWidgets.QAction(MainWindow)
        self.importZdFoundationDataAction.setObjectName("importZdFoundationDataAction")
        self.pickupFromJlAction = QtWidgets.QAction(MainWindow)
        self.pickupFromJlAction.setObjectName("pickupFromJlAction")
        self.pickupFromZdAction = QtWidgets.QAction(MainWindow)
        self.pickupFromZdAction.setObjectName("pickupFromZdAction")
        self.pickupFromSiteAction = QtWidgets.QAction(MainWindow)
        self.pickupFromSiteAction.setObjectName("pickupFromSiteAction")
        self.calculateThrListAction = QtWidgets.QAction(MainWindow)
        self.calculateThrListAction.setObjectName("calculateThrListAction")
        self.adminRightAction = QtWidgets.QAction(MainWindow)
        self.adminRightAction.setObjectName("adminRightAction")
        self.modifyStockAction = QtWidgets.QAction(MainWindow)
        self.modifyStockAction.setObjectName("modifyStockAction")
        self.readProductListAction = QtWidgets.QAction(MainWindow)
        self.readProductListAction.setObjectName("readProductListAction")
        self.menu.addSeparator()
        self.menu.addAction(self.readProductListAction)
        self.menu.addAction(self.adminRightAction)
        self.menu.addSeparator()
        self.menu.addAction(self.quitAction)
        self.menu_2.addAction(self.addProgressAction)
        self.menu_2.addSeparator()
        self.menu_2.addAction(self.generateBomAction)
        self.menu_4.addAction(self.noKbnAction)
        self.menu_7.addAction(self.pickupFromZdAction)
        self.menu_7.addAction(self.pickupFromJlAction)
        self.menu_7.addAction(self.pickupFromSiteAction)
        self.menu_3.addAction(self.calculationMaterialAction)
        self.menu_3.addAction(self.calculateThrListAction)
        self.menu_3.addAction(self.menu_7.menuAction())
        self.menu_3.addSeparator()
        self.menu_3.addAction(self.menu_4.menuAction())
        self.menu_6.addAction(self.importZdStoringAction)
        self.menu_6.addAction(self.importJlStoringAction)
        self.menu_6.addSeparator()
        self.menu_6.addAction(self.importSiteStoringAction)
        self.menu_5.addAction(self.importZdFoundationDataAction)
        self.menu_5.addSeparator()
        self.menu_5.addAction(self.menu_6.menuAction())
        self.menu_5.addAction(self.modifyStockAction)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())
        self.menubar.addAction(self.menu_5.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.menu_2.setTitle(_translate("MainWindow", "派工"))
        self.menu_3.setTitle(_translate("MainWindow", "配料"))
        self.menu_4.setTitle(_translate("MainWindow", "设置"))
        self.menu_7.setTitle(_translate("MainWindow", "领料"))
        self.menu_5.setTitle(_translate("MainWindow", "数据"))
        self.menu_6.setTitle(_translate("MainWindow", "导入仓储数据"))
        self.quitAction.setText(_translate("MainWindow", "退出"))
        self.quitAction.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.addProgressAction.setText(_translate("MainWindow", "添加工序"))
        self.addProgressAction.setShortcut(_translate("MainWindow", "Ctrl+P"))
        self.calculationMaterialAction.setText(_translate("MainWindow", "计算物料"))
        self.calculationMaterialAction.setShortcut(_translate("MainWindow", "Ctrl+R"))
        self.noKbnAction.setText(_translate("MainWindow", "不计KBN"))
        self.importZdStoringAction.setText(_translate("MainWindow", "中德仓库..."))
        self.importJlStoringAction.setText(_translate("MainWindow", "巨轮仓库..."))
        self.importSiteStoringAction.setText(_translate("MainWindow", "现场..."))
        self.generateBomAction.setText(_translate("MainWindow", "生成清单..."))
        self.action_3.setText(_translate("MainWindow", "中德仓储数据"))
        self.action_4.setText(_translate("MainWindow", "巨轮仓储数据"))
        self.action_6.setText(_translate("MainWindow", "现场仓储数据"))
        self.importZdFoundationDataAction.setText(_translate("MainWindow", "导入中德物料基础数据..."))
        self.pickupFromJlAction.setText(_translate("MainWindow", "巨轮..."))
        self.pickupFromZdAction.setText(_translate("MainWindow", "中德..."))
        self.pickupFromSiteAction.setText(_translate("MainWindow", "现场..."))
        self.calculateThrListAction.setText(_translate("MainWindow", "根据清单配料..."))
        self.adminRightAction.setText(_translate("MainWindow", "获取管理员权限"))
        self.modifyStockAction.setText(_translate("MainWindow", "修改库存"))
        self.readProductListAction.setText(_translate("MainWindow", "打开产品清单"))
