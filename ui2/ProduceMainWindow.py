# -*- coding: utf-8 -*-

# Form implementation generated from reading ListDisplayDialog.CreatePartDialog.ui file 'ProduceMainWindow.ListDisplayDialog.CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(917, 668)
        self.RequirementCentralWidget = QtWidgets.QWidget(MainWindow)
        self.RequirementCentralWidget.setObjectName("RequirementCentralWidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.RequirementCentralWidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(59, 9, 611, 491))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.v_layout_1 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.v_layout_1.setContentsMargins(0, 0, 0, 0)
        self.v_layout_1.setObjectName("v_layout_1")
        self.h_layout_1_1 = QtWidgets.QHBoxLayout()
        self.h_layout_1_1.setObjectName("h_layout_1_1")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.h_layout_1_1.addWidget(self.label, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.ContractComboBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ContractComboBox.sizePolicy().hasHeightForWidth())
        self.ContractComboBox.setSizePolicy(sizePolicy)
        self.ContractComboBox.setObjectName("ContractComboBox")
        self.h_layout_1_1.addWidget(self.ContractComboBox)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.h_layout_1_1.addWidget(self.label_2)
        self.ParNameLineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.ParNameLineEdit.setObjectName("ParNameLineEdit")
        self.h_layout_1_1.addWidget(self.ParNameLineEdit)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.h_layout_1_1.addWidget(self.label_3)
        self.PartNrlineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.PartNrlineEdit.setObjectName("PartNrlineEdit")
        self.h_layout_1_1.addWidget(self.PartNrlineEdit)
        self.CleanTextButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CleanTextButton.sizePolicy().hasHeightForWidth())
        self.CleanTextButton.setSizePolicy(sizePolicy)
        self.CleanTextButton.setObjectName("CleanTextButton")
        self.h_layout_1_1.addWidget(self.CleanTextButton)
        self.v_layout_1.addLayout(self.h_layout_1_1)
        self.RequireTreeWidget = QtWidgets.QTreeWidget(self.verticalLayoutWidget)
        self.RequireTreeWidget.setObjectName("RequireTreeWidget")
        self.RequireTreeWidget.headerItem().setText(0, "1")
        self.v_layout_1.addWidget(self.RequireTreeWidget)
        MainWindow.setCentralWidget(self.RequirementCentralWidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 917, 26))
        self.menubar.setObjectName("menubar")
        self.RequirementMenu = QtWidgets.QMenu(self.menubar)
        self.RequirementMenu.setToolTip("")
        self.RequirementMenu.setToolTipsVisible(True)
        self.RequirementMenu.setObjectName("RequirementMenu")
        self.ContractMenu = QtWidgets.QMenu(self.menubar)
        self.ContractMenu.setToolTip("")
        self.ContractMenu.setObjectName("ContractMenu")
        self.WorkgroupMenu = QtWidgets.QMenu(self.menubar)
        self.WorkgroupMenu.setObjectName("WorkgroupMenu")
        self.HelpMenu = QtWidgets.QMenu(self.menubar)
        self.HelpMenu.setObjectName("HelpMenu")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.WorkgroupDockWidget = QtWidgets.QDockWidget(MainWindow)
        self.WorkgroupDockWidget.setObjectName("WorkgroupDockWidget")
        self.WkDockWidgetContents = QtWidgets.QWidget()
        self.WkDockWidgetContents.setObjectName("WkDockWidgetContents")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.WkDockWidgetContents)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(40, 20, 160, 229))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.v_layout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.v_layout_3.setContentsMargins(0, 0, 0, 0)
        self.v_layout_3.setObjectName("v_layout_3")
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_4.setObjectName("label_4")
        self.v_layout_3.addWidget(self.label_4, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.DepartmentTreeView = QtWidgets.QTreeView(self.verticalLayoutWidget_3)
        self.DepartmentTreeView.setObjectName("DepartmentTreeView")
        self.v_layout_3.addWidget(self.DepartmentTreeView)
        self.label_5 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_5.setObjectName("label_5")
        self.v_layout_3.addWidget(self.label_5, 0, QtCore.Qt.AlignLeft)
        self.MemberListView = QtWidgets.QListView(self.verticalLayoutWidget_3)
        self.MemberListView.setObjectName("MemberListView")
        self.v_layout_3.addWidget(self.MemberListView)
        self.WorkgroupDockWidget.setWidget(self.WkDockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.WorkgroupDockWidget)
        self.ContractDockWidget = QtWidgets.QDockWidget(MainWindow)
        self.ContractDockWidget.setAutoFillBackground(False)
        self.ContractDockWidget.setObjectName("ContractDockWidget")
        self.CtDockWidgetContents = QtWidgets.QWidget()
        self.CtDockWidgetContents.setObjectName("CtDockWidgetContents")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.CtDockWidgetContents)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(30, 30, 160, 89))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.v_layout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.v_layout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.v_layout_2.setContentsMargins(0, 0, 0, 0)
        self.v_layout_2.setObjectName("v_layout_2")
        self.CtTableWidget = QtWidgets.QTableWidget(self.verticalLayoutWidget_2)
        self.CtTableWidget.setObjectName("CtTableWidget")
        self.CtTableWidget.setColumnCount(0)
        self.CtTableWidget.setRowCount(0)
        self.v_layout_2.addWidget(self.CtTableWidget)
        self.ContractDockWidget.setWidget(self.CtDockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.ContractDockWidget)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.RequirementMenu.menuAction())
        self.menubar.addAction(self.ContractMenu.menuAction())
        self.menubar.addAction(self.WorkgroupMenu.menuAction())
        self.menubar.addAction(self.HelpMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "中德制造部机加工管理"))
        self.label.setText(_translate("MainWindow", "生产合同"))
        self.label_2.setText(_translate("MainWindow", "零件名"))
        self.label_3.setText(_translate("MainWindow", "零件号"))
        self.CleanTextButton.setText(_translate("MainWindow", "清空"))
        self.RequirementMenu.setStatusTip(_translate("MainWindow", "生产任务（需求）的管理维护。"))
        self.RequirementMenu.setTitle(_translate("MainWindow", "任务"))
        self.ContractMenu.setStatusTip(_translate("MainWindow", "生产合同的管理维护。"))
        self.ContractMenu.setTitle(_translate("MainWindow", "合同"))
        self.WorkgroupMenu.setToolTip(_translate("MainWindow", "组织架构的管理维护。"))
        self.WorkgroupMenu.setStatusTip(_translate("MainWindow", "组织架构的管理维护。"))
        self.WorkgroupMenu.setTitle(_translate("MainWindow", "组织"))
        self.HelpMenu.setStatusTip(_translate("MainWindow", "软件帮助信息。"))
        self.HelpMenu.setTitle(_translate("MainWindow", "帮助"))
        self.menu.setStatusTip(_translate("MainWindow", "软件工具管理。"))
        self.menu.setTitle(_translate("MainWindow", "全局"))
        self.WorkgroupDockWidget.setWindowTitle(_translate("MainWindow", "组织架构"))
        self.label_4.setText(_translate("MainWindow", "部门"))
        self.label_5.setText(_translate("MainWindow", "成员"))
        self.ContractDockWidget.setWindowTitle(_translate("MainWindow", "生产合同"))