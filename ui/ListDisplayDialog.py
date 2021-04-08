# -*- coding: utf-8 -*-

# Form implementation generated from reading CreatePartDialog.ui file 'ListDisplayDialog.CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_listDisplayDialog(object):
    def setupUi(self, listDisplayDialog):
        listDisplayDialog.setObjectName("listDisplayDialog")
        listDisplayDialog.resize(504, 452)
        self.horizontalLayoutWidget = QtWidgets.QWidget(listDisplayDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 193, 93))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.h_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.h_layout.setContentsMargins(2, 2, 2, 2)
        self.h_layout.setObjectName("h_layout")
        self.theListWidget = QtWidgets.QListWidget(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.theListWidget.sizePolicy().hasHeightForWidth())
        self.theListWidget.setSizePolicy(sizePolicy)
        self.theListWidget.setObjectName("theListWidget")
        self.h_layout.addWidget(self.theListWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.horizontalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.h_layout.addWidget(self.buttonBox)

        self.retranslateUi(listDisplayDialog)
        self.buttonBox.accepted.connect( listDisplayDialog.accept )
        self.buttonBox.rejected.connect(listDisplayDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(listDisplayDialog)

    def retranslateUi(self, listDisplayDialog):
        _translate = QtCore.QCoreApplication.translate
        listDisplayDialog.setWindowTitle(_translate("listDisplayDialog", "列表数据"))
