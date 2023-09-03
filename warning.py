from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import *

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(435, 118)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.information = QtWidgets.QLabel(Dialog)
        self.information.setScaledContents(False)
        self.information.setWordWrap(False)
        self.information.setObjectName("information")
        self.verticalLayout.addWidget(self.information, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(178, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.confirm = QtWidgets.QPushButton(Dialog)
        self.confirm.setObjectName("confirm")
        self.horizontalLayout.addWidget(self.confirm)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 2)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Warning"))
        self.information.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:20pt;\">Please correct the face information!</span></p></body></html>"))
        self.confirm.setText(_translate("Dialog", "确定"))

class myDialog(Ui_Dialog,QWidget):
    def __init__(self, parent=None):
        super(myDialog, self).__init__(parent)
        self.setupUi(self)
        self.confirm.clicked.connect(QCoreApplication.instance().quit)
