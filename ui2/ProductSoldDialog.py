# -*- coding: utf-8 -*-

# Form implementation generated from reading CreatePartDialog.ui file 'ProductSoldDialog.CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(644, 460)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(180, 100, 195, 165))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.v1_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.v1_layout.setContentsMargins(0, 0, 0, 0)
        self.v1_layout.setObjectName("v1_layout")
        self.v2_layout = QtWidgets.QVBoxLayout()
        self.v2_layout.setObjectName("v2_layout")
        self.f3_layout = QtWidgets.QFormLayout()
        self.f3_layout.setContentsMargins(2, 2, 2, 2)
        self.f3_layout.setSpacing(5)
        self.f3_layout.setObjectName("f3_layout")
        self.v2_layout.addLayout(self.f3_layout)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.v2_layout.addWidget(self.label)
        self.listWidget = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.listWidget.setObjectName("listWidget")
        self.v2_layout.addWidget(self.listWidget)
        self.v1_layout.addLayout(self.v2_layout)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.v1_layout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect( Dialog.accept )
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "产品"))
