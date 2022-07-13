# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ErpItemSelector.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(613, 445)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 20, 571, 401))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.mv_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.mv_layout.setContentsMargins(2, 2, 2, 2)
        self.mv_layout.setSpacing(5)
        self.mv_layout.setObjectName("mv_layout")
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.h_layout.setContentsMargins(2, 2, 2, 2)
        self.h_layout.setSpacing(5)
        self.h_layout.setObjectName("h_layout")
        self.searchLineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.h_layout.addWidget(self.searchLineEdit)
        self.idRadioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.idRadioButton.setObjectName("idRadioButton")
        self.h_layout.addWidget(self.idRadioButton)
        self.desRadioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.desRadioButton.setObjectName("desRadioButton")
        self.h_layout.addWidget(self.desRadioButton)
        self.mv_layout.addLayout(self.h_layout)
        self.itemsTableView = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.itemsTableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.itemsTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.itemsTableView.setObjectName("itemsTableView")
        self.mv_layout.addWidget(self.itemsTableView)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.mv_layout.addWidget(self.buttonBox)
        self.mv_layout.setStretch(0, 5)
        self.mv_layout.setStretch(2, 5)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.idRadioButton.setText(_translate("Dialog", "编码"))
        self.desRadioButton.setText(_translate("Dialog", "描述"))
