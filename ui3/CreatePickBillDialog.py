# -*- coding: utf-8 -*-

# Form implementation generated from reading ListDisplayDialog.CreatePartDialog.ui file 'CreatePickBillDialog.ListDisplayDialog.CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(483, 396)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 481, 391))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.mainVLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.mainVLayout.setContentsMargins(0, 0, 0, 0)
        self.mainVLayout.setObjectName("mainVLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(2, 2, 2, 2)
        self.formLayout.setObjectName("formLayout")
        self.mainVLayout.addLayout(self.formLayout)
        self.midHL = QtWidgets.QHBoxLayout()
        self.midHL.setContentsMargins(2, 2, 2, 2)
        self.midHL.setObjectName("midHL")
        self.itemsTableView = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.itemsTableView.setObjectName("itemsTableView")
        self.midHL.addWidget(self.itemsTableView)
        self.midRightHL = QtWidgets.QVBoxLayout()
        self.midRightHL.setObjectName("midRightHL")
        self.addButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addButton.sizePolicy().hasHeightForWidth())
        self.addButton.setSizePolicy(sizePolicy)
        self.addButton.setMinimumSize(QtCore.QSize(0, 0))
        self.addButton.setBaseSize(QtCore.QSize(40, 0))
        self.addButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.addButton.setObjectName("addButton")
        self.midRightHL.addWidget(self.addButton)
        self.removeButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.removeButton.setMinimumSize(QtCore.QSize(0, 0))
        self.removeButton.setObjectName("removeButton")
        self.midRightHL.addWidget(self.removeButton)
        self.midHL.addLayout(self.midRightHL)
        self.mainVLayout.addLayout(self.midHL)
        self.bottomHL = QtWidgets.QHBoxLayout()
        self.bottomHL.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.bottomHL.setObjectName("bottomHL")
        self.theDialogButtonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.theDialogButtonBox.sizePolicy().hasHeightForWidth())
        self.theDialogButtonBox.setSizePolicy(sizePolicy)
        self.theDialogButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.theDialogButtonBox.setObjectName("theDialogButtonBox")
        self.bottomHL.addWidget(self.theDialogButtonBox)
        self.mainVLayout.addLayout(self.bottomHL)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "创建领料单"))
        self.addButton.setText(_translate("Dialog", "+"))
        self.removeButton.setText(_translate("Dialog", "-"))

