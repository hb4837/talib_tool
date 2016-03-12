# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(974, 702)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.shellWidget = QtGui.QWidget(self.centralwidget)
        self.shellWidget.setGeometry(QtCore.QRect(9, 391, 841, 261))
        self.shellWidget.setObjectName(_fromUtf8("shellWidget"))
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(209, 0, 641, 381))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.plotLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.plotLayout.setObjectName(_fromUtf8("plotLayout"))
        self.marketsCombo = QtGui.QComboBox(self.centralwidget)
        self.marketsCombo.setGeometry(QtCore.QRect(11, 11, 171, 20))
        self.marketsCombo.setMaximumSize(QtCore.QSize(175, 25))
        self.marketsCombo.setObjectName(_fromUtf8("marketsCombo"))
        self.symbolsList = QtGui.QListWidget(self.centralwidget)
        self.symbolsList.setGeometry(QtCore.QRect(11, 37, 175, 341))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.symbolsList.sizePolicy().hasHeightForWidth())
        self.symbolsList.setSizePolicy(sizePolicy)
        self.symbolsList.setMaximumSize(QtCore.QSize(175, 16777215))
        self.symbolsList.setObjectName(_fromUtf8("symbolsList"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 974, 21))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuIndicator = QtGui.QMenu(self.menuBar)
        self.menuIndicator.setObjectName(_fromUtf8("menuIndicator"))
        self.menuSMA = QtGui.QMenu(self.menuIndicator)
        self.menuSMA.setObjectName(_fromUtf8("menuSMA"))
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionRSI = QtGui.QAction(MainWindow)
        self.actionRSI.setCheckable(True)
        self.actionRSI.setObjectName(_fromUtf8("actionRSI"))
        self.actionBollinger = QtGui.QAction(MainWindow)
        self.actionBollinger.setCheckable(True)
        self.actionBollinger.setObjectName(_fromUtf8("actionBollinger"))
        self.actionSma30 = QtGui.QAction(MainWindow)
        self.actionSma30.setCheckable(True)
        self.actionSma30.setObjectName(_fromUtf8("actionSma30"))
        self.actionSma90 = QtGui.QAction(MainWindow)
        self.actionSma90.setCheckable(True)
        self.actionSma90.setObjectName(_fromUtf8("actionSma90"))
        self.actionSma200 = QtGui.QAction(MainWindow)
        self.actionSma200.setCheckable(True)
        self.actionSma200.setObjectName(_fromUtf8("actionSma200"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionQuit)
        self.menuSMA.addAction(self.actionSma30)
        self.menuSMA.addAction(self.actionSma90)
        self.menuSMA.addAction(self.actionSma200)
        self.menuIndicator.addAction(self.menuSMA.menuAction())
        self.menuIndicator.addAction(self.actionRSI)
        self.menuIndicator.addAction(self.actionBollinger)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuIndicator.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuIndicator.setTitle(_translate("MainWindow", "Indicator", None))
        self.menuSMA.setTitle(_translate("MainWindow", "SMA", None))
        self.actionOpen.setText(_translate("MainWindow", "Open ...", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionRSI.setText(_translate("MainWindow", "RSI", None))
        self.actionBollinger.setText(_translate("MainWindow", "Bollinger", None))
        self.actionSma30.setText(_translate("MainWindow", "30 days", None))
        self.actionSma90.setText(_translate("MainWindow", "90 days", None))
        self.actionSma200.setText(_translate("MainWindow", "200 days", None))

