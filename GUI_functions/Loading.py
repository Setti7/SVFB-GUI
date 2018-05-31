from PyQt5.QtWidgets import QDialog
from PyQt5 import QtGui
from PyQt5.uic import loadUi

class Loading(QDialog):

    def __init__(self):
        super().__init__()
        self.initUI()

        self.show()

    def initUI(self):
        loadUi('designs\\loading_dialog.ui', self)
        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.png'))