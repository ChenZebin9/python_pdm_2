# -*- coding: utf-8 -*-

# Form implementation generated from reading CreatePartDialog.ui file 'HandleEntranceDialog.CreatePartDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(309, 190)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 291, 171))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.g1_layout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.g1_layout.setContentsMargins(2, 2, 2, 2)
        self.g1_layout.setObjectName("g1_layout")
        self.show2BuyPushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.show2BuyPushButton.setObjectName("show2BuyPushButton")
        self.g1_layout.addWidget(self.show2BuyPushButton, 0, 2, 1, 1)
        self.toBuyPushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.toBuyPushButton.setObjectName("toBuyPushButton")
        self.g1_layout.addWidget(self.toBuyPushButton, 0, 0, 1, 1)
        self.toStoragePushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.toStoragePushButton.setObjectName("toStoragePushButton")
        self.g1_layout.addWidget(self.toStoragePushButton, 2, 0, 1, 1)
        self.toPickPushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.toPickPushButton.setObjectName("toPickPushButton")
        self.g1_layout.addWidget(self.toPickPushButton, 3, 0, 1, 1)
        self.toProducePushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.toProducePushButton.setObjectName("toProducePushButton")
        self.g1_layout.addWidget(self.toProducePushButton, 1, 0, 1, 1)
        self.toBuyLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.toBuyLabel.setText("")
        self.toBuyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.toBuyLabel.setObjectName("toBuyLabel")
        self.g1_layout.addWidget(self.toBuyLabel, 0, 1, 1, 1)
        self.toProduceLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.toProduceLabel.setText("")
        self.toProduceLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.toProduceLabel.setObjectName("toProduceLabel")
        self.g1_layout.addWidget(self.toProduceLabel, 1, 1, 1, 1)
        self.toStorageLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.toStorageLabel.setText("")
        self.toStorageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.toStorageLabel.setObjectName("toStorageLabel")
        self.g1_layout.addWidget(self.toStorageLabel, 2, 1, 1, 1)
        self.toPickLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.toPickLabel.setText("")
        self.toPickLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.toPickLabel.setObjectName("toPickLabel")
        self.g1_layout.addWidget(self.toPickLabel, 3, 1, 1, 1)
        self.show2ProducePushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.show2ProducePushButton.setObjectName("show2ProducePushButton")
        self.g1_layout.addWidget(self.show2ProducePushButton, 1, 2, 1, 1)
        self.show2StoringPushButong = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.show2StoringPushButong.setObjectName("show2StoringPushButong")
        self.g1_layout.addWidget(self.show2StoringPushButong, 2, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "需求处理选择"))
        self.show2BuyPushButton.setText(_translate("Dialog", "清单"))
        self.toBuyPushButton.setText(_translate("Dialog", "投料"))
        self.toStoragePushButton.setText(_translate("Dialog", "入库"))
        self.toPickPushButton.setText(_translate("Dialog", "退库"))
        self.toProducePushButton.setText(_translate("Dialog", "派工"))
        self.show2ProducePushButton.setText(_translate("Dialog", "清单"))
        self.show2StoringPushButong.setText(_translate("Dialog", "清单"))
