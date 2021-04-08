# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HandleRequirementDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(697, 551)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(50, 20, 561, 32))
        self.layoutWidget.setObjectName("layoutWidget")
        self.h2_2_layout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.h2_2_layout.setContentsMargins(2, 2, 2, 2)
        self.h2_2_layout.setObjectName("h2_2_layout")
        self.cancelRequirementButton = QtWidgets.QPushButton(self.layoutWidget)
        self.cancelRequirementButton.setObjectName("cancelRequirementButton")
        self.h2_2_layout.addWidget(self.cancelRequirementButton)
        self.rollBackButton = QtWidgets.QPushButton(self.layoutWidget)
        self.rollBackButton.setObjectName("rollBackButton")
        self.h2_2_layout.addWidget(self.rollBackButton)
        self.pushForwardButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushForwardButton.setObjectName("pushForwardButton")
        self.h2_2_layout.addWidget(self.pushForwardButton)
        self.removeButton = QtWidgets.QPushButton(self.layoutWidget)
        self.removeButton.setObjectName("removeButton")
        self.h2_2_layout.addWidget(self.removeButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.h2_2_layout.addItem(spacerItem)
        self.layoutWidget1 = QtWidgets.QWidget(Dialog)
        self.layoutWidget1.setGeometry(QtCore.QRect(78, 70, 551, 32))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.h2_layout = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.h2_layout.setContentsMargins(2, 2, 2, 2)
        self.h2_layout.setObjectName("h2_layout")
        self.searchItemComboBox = QtWidgets.QComboBox(self.layoutWidget1)
        self.searchItemComboBox.setObjectName("searchItemComboBox")
        self.h2_layout.addWidget(self.searchItemComboBox)
        self.filterlineEdit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.filterlineEdit.setObjectName("filterlineEdit")
        self.h2_layout.addWidget(self.filterlineEdit)
        self.doSearchButton = QtWidgets.QPushButton(self.layoutWidget1)
        self.doSearchButton.setObjectName("doSearchButton")
        self.h2_layout.addWidget(self.doSearchButton)
        self.cleanSearchButton = QtWidgets.QPushButton(self.layoutWidget1)
        self.cleanSearchButton.setObjectName("cleanSearchButton")
        self.h2_layout.addWidget(self.cleanSearchButton)
        self.sourceRequirementTableView = QtWidgets.QTableView(Dialog)
        self.sourceRequirementTableView.setGeometry(QtCore.QRect(152, 131, 407, 123))
        self.sourceRequirementTableView.setObjectName("sourceRequirementTableView")
        self.destRequirementTableView = QtWidgets.QTableView(Dialog)
        self.destRequirementTableView.setGeometry(QtCore.QRect(152, 300, 407, 124))
        self.destRequirementTableView.setObjectName("destRequirementTableView")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(310, 440, 281, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.button_h_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.button_h_layout.setContentsMargins(2, 2, 2, 2)
        self.button_h_layout.setObjectName("button_h_layout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.button_h_layout.addItem(spacerItem1)
        self.okButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.okButton.setObjectName("okButton")
        self.button_h_layout.addWidget(self.okButton)
        self.closeButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.closeButton.setObjectName("closeButton")
        self.button_h_layout.addWidget(self.closeButton)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "处理需求"))
        self.cancelRequirementButton.setText(_translate("Dialog", "作废"))
        self.rollBackButton.setText(_translate("Dialog", "回退"))
        self.pushForwardButton.setText(_translate("Dialog", "处理"))
        self.removeButton.setText(_translate("Dialog", "删除"))
        self.doSearchButton.setText(_translate("Dialog", "检索"))
        self.cleanSearchButton.setText(_translate("Dialog", "清除"))
        self.okButton.setText(_translate("Dialog", "OK"))
        self.closeButton.setText(_translate("Dialog", "Close"))
