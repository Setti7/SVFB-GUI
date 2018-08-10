import json

from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class WelcomeDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))

        self.ok_btn.clicked.connect(self.save)

    def initUI(self):
        loadUi('designs\\WelcomeDialog.ui', self)

    def save(self):
        with open("config.json", 'r') as f:
            output = json.loads(f.read())
            output["First Time Running"] = False

        with open("config.json", "w") as f:
            json.dump(output, f, indent=2)

        self.accept()
