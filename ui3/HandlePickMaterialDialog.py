# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HandlePickMaterialDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(668, 500)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(90, 40, 421, 351))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.v_1_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.v_1_layout.setContentsMargins(2, 2, 2, 2)
        self.v_1_layout.setObjectName("v_1_layout")
        self.h_2_layout = QtWidgets.QHBoxLayout()
        self.h_2_layout.setObjectName("h_2_layout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.h_2_layout.addWidget(self.label)
        self.beginDateEdit = QtWidgets.QDateEdit(self.verticalLayoutWidget)
        self.beginDateEdit.setObjectName("beginDateEdit")
        self.h_2_layout.addWidget(self.beginDateEdit)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.h_2_layout.addWidget(self.label_2)
        self.endDateEdit = QtWidgets.QDateEdit(self.verticalLayoutWidget)
        self.endDateEdit.setObjectName("endDateEdit")
        self.h_2_layout.addWidget(self.endDateEdit)
        self.v_1_layout.addLayout(self.h_2_layout)
        self.materialTableView = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.materialTableView.setObjectName("materialTableView")
        self.v_1_layout.addWidget(self.materialTableView)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.v_1_layout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "起始日期"))
        self.label_2.setText(_translate("Dialog", "结束日期"))
