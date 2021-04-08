# -*- coding: utf-8 -*-

# Form implementation generated from reading CreatePartDialog.ui file 'CreateRequirementDialog.CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(716, 459)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(190, 100, 200, 142))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.v1_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.v1_layout.setContentsMargins(0, 0, 0, 0)
        self.v1_layout.setObjectName("v1_layout")
        self.f2_layout = QtWidgets.QFormLayout()
        self.f2_layout.setContentsMargins(2, 2, 2, 2)
        self.f2_layout.setObjectName("f2_layout")
        self.v1_layout.addLayout(self.f2_layout)
        self.h2_layout = QtWidgets.QHBoxLayout()
        self.h2_layout.setObjectName("h2_layout")
        self.dataTableView = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.dataTableView.setObjectName("dataTableView")
        self.h2_layout.addWidget(self.dataTableView)
        self.v3_layout = QtWidgets.QVBoxLayout()
        self.v3_layout.setObjectName("v3_layout")
        self.addItemButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addItemButton.sizePolicy().hasHeightForWidth())
        self.addItemButton.setSizePolicy(sizePolicy)
        self.addItemButton.setObjectName("addItemButton")
        self.v3_layout.addWidget(self.addItemButton)
        self.removeItemButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.removeItemButton.setObjectName("removeItemButton")
        self.v3_layout.addWidget(self.removeItemButton)
        self.h2_layout.addLayout(self.v3_layout)
        self.v1_layout.addLayout(self.h2_layout)
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
        Dialog.setWindowTitle(_translate("Dialog", "创建物料需求"))
        self.addItemButton.setText(_translate("Dialog", "+"))
        self.removeItemButton.setText(_translate("Dialog", "-"))
