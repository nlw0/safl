# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'objseg_ui.ui'
#
# Created: Wed Sep  5 22:24:55 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

# from PyQt4 import QtCore, QtGui
# from PyQt5 import QtCore, QtGui
from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(524, 354)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_6.addWidget(self.label)
        self.img1IndexBox = QtWidgets.QSpinBox(self.centralwidget)
        self.img1IndexBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.img1IndexBox.setObjectName(_fromUtf8("img1IndexBox"))
        self.horizontalLayout_6.addWidget(self.img1IndexBox)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_6.addWidget(self.label_3)
        self.setIndexBox = QtWidgets.QSpinBox(self.centralwidget)
        self.setIndexBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.setIndexBox.setObjectName(_fromUtf8("setIndexBox"))
        self.horizontalLayout_6.addWidget(self.setIndexBox)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.horizontalLayout_3.addLayout(self.horizontalLayout_7)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.im1 = MplWidget(self.centralwidget)
        self.im1.setObjectName(_fromUtf8("im1"))
        self.horizontalLayout.addWidget(self.im1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 524, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuSAFL_Point = QtWidgets.QMenu(self.menubar)
        self.menuSAFL_Point.setObjectName(_fromUtf8("menuSAFL_Point"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionClear_matches = QtWidgets.QAction(MainWindow)
        self.actionClear_matches.setObjectName(_fromUtf8("actionClear_matches"))
        self.menuSAFL_Point.addAction(self.actionOpen)
        self.menuSAFL_Point.addAction(self.actionSave)
        self.menuSAFL_Point.addAction(self.actionQuit)
        self.menuSAFL_Point.addSeparator()
        self.menuSAFL_Point.addAction(self.actionClear_matches)
        self.menubar.addAction(self.menuSAFL_Point.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "SAFL Point", None))
        self.label.setText(QtWidgets.QApplication.translate("MainWindow", "Image:", None))
        self.label_3.setText(QtWidgets.QApplication.translate("MainWindow", "Object:", None))
        self.menuSAFL_Point.setTitle(QtWidgets.QApplication.translate("MainWindow", "&SAFL Object", None))
        self.actionQuit.setText(QtWidgets.QApplication.translate("MainWindow", "&Quit", None))
        self.actionSave.setText(QtWidgets.QApplication.translate("MainWindow", "&Save", None))
        self.actionOpen.setText(QtWidgets.QApplication.translate("MainWindow", "&Open", None))
        self.actionClear_matches.setText(QtWidgets.QApplication.translate("MainWindow", "Clear matches", None))

from mplwidget import MplWidget
