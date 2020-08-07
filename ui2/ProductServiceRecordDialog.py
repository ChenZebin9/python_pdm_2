# -*- coding: utf-8 -*-

# Form implementation generated from reading ListDisplayDialog.CreatePartDialog.ui file 'ProductServiceRecordDialog.ListDisplayDialog.CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 180)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 85, 54))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.h_layout = QtWidgets.QHBoxLayout(self.verticalLayoutWidget)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setObjectName("h_layout")
        self.f_layout = QtWidgets.QFormLayout()
        self.f_layout.setObjectName("f_layout")
        self.h_layout.addLayout(self.f_layout)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.h_layout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "售后服务"))

