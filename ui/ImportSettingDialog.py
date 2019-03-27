# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportSettingDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setModal(True)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 381, 281))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.v_box = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.setObjectName("v_box")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.sheetComboBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.sheetComboBox.setObjectName("sheetComboBox")
        self.horizontalLayout.addWidget(self.sheetComboBox)
        self.v_box.addLayout(self.horizontalLayout)
        self.dataConfigTableWidget = QtWidgets.QTableWidget(self.verticalLayoutWidget)
        self.dataConfigTableWidget.setObjectName("dataConfigTableWidget")
        self.dataConfigTableWidget.setColumnCount(0)
        self.dataConfigTableWidget.setRowCount(0)
        self.v_box.addWidget(self.dataConfigTableWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.v_box.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "数据表："))

