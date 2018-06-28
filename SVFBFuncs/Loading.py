from PyQt5.QtWidgets import QDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

class Loading(QDialog):

    def __init__(self):
        super().__init__()
        self.initUI()

        self.show()

    def initUI(self):
        loadUi('designs\\loading_dialog.ui', self)
        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))

        self.loading_animation = QtGui.QMovie("media\\animations\\loading.gif")
        self.loading_label.setMovie(self.loading_animation)
        self.loading_animation.start()
        self.setWindowFlags(Qt.FramelessWindowHint)
