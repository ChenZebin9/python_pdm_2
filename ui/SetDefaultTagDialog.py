# -*- coding: utf-8 -*-

# Form implementation generated from reading ListDisplayDialog.CreatePartDialog.ui file 'SetDefaultTagDialog.ListDisplayDialog.CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 20, 251, 261))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.h_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setObjectName("h_layout")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect( Dialog.accept )
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "选择标签组"))


