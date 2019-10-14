# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProductInfoDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 371, 271))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.main_h_box = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.main_h_box.setContentsMargins(0, 0, 0, 0)
        self.main_h_box.setObjectName("main_h_box")
        self.inner_v_box = QtWidgets.QVBoxLayout()
        self.inner_v_box.setObjectName("inner_v_box")
        self.form_box = QtWidgets.QFormLayout()
        self.form_box.setObjectName("form_box")
        self.inner_v_box.addLayout(self.form_box)
        self.inner_h_box = QtWidgets.QHBoxLayout()
        self.inner_h_box.setObjectName("inner_h_box")
        self.inner_v_box.addLayout(self.inner_h_box)
        self.main_h_box.addLayout(self.inner_v_box)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.horizontalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.main_h_box.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "产品信息"))

