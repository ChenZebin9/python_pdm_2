# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(607, 331)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 50, 551, 271))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.v_1_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.v_1_layout.setContentsMargins(0, 0, 0, 0)
        self.v_1_layout.setObjectName("v_1_layout")
        self.v_2_layout = QtWidgets.QVBoxLayout()
        self.v_2_layout.setObjectName("v_2_layout")
        self.v_1_layout.addLayout(self.v_2_layout)
        self.h_2_layout = QtWidgets.QHBoxLayout()
        self.h_2_layout.setObjectName("h_2_layout")
        self.refButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.refButton.setObjectName("refButton")
        self.h_2_layout.addWidget(self.refButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.h_2_layout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.h_2_layout.addWidget(self.buttonBox)
        self.v_1_layout.addLayout(self.h_2_layout)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "创建新单元"))
        self.refButton.setText(_translate("Dialog", "参考"))
