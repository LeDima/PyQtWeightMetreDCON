# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\PyProg\PyQtWeightMetreDCON\GUI2.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TabWidget(object):
    def setupUi(self, TabWidget):
        TabWidget.setObjectName("TabWidget")
        TabWidget.resize(1285, 784)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TabWidget.sizePolicy().hasHeightForWidth())
        TabWidget.setSizePolicy(sizePolicy)
        TabWidget.setMinimumSize(QtCore.QSize(700, 500))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        TabWidget.setFont(font)
        TabWidget.setIconSize(QtCore.QSize(16, 16))
        self.VacTab = QtWidgets.QWidget()
        self.VacTab.setObjectName("VacTab")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.VacTab)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(170, 20, 901, 571))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mplwindow = QtWidgets.QWidget(self.verticalLayoutWidget)
        self.mplwindow.setAcceptDrops(False)
        self.mplwindow.setObjectName("mplwindow")
        self.verticalLayout.addWidget(self.mplwindow)
        TabWidget.addTab(self.VacTab, "")

        self.retranslateUi(TabWidget)
        TabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TabWidget)

    def retranslateUi(self, TabWidget):
        _translate = QtCore.QCoreApplication.translate
        TabWidget.setWindowTitle(_translate("TabWidget", "TabWidget"))
        TabWidget.setTabText(TabWidget.indexOf(self.VacTab), _translate("TabWidget", "Общие настройки"))

