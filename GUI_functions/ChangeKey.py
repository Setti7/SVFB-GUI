import json
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtGui
from PyQt5.uic import loadUi

class ChangeKey(QDialog):
    new_key = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.png'))

        self.save_btn.clicked.connect(self.save)
        self.close_btn.clicked.connect(self.close)
        self.change_key.setFocus(True)

    def initUI(self):
        loadUi('designs\\key_used_dialog.ui', self)

    def save(self):
        with open("config.json", "r") as f:
            output = json.loads(f.read())
            new_key = str(self.change_key.text()).upper()
            output['Used key'] = new_key

        with open("config.json", "w") as f:
            json.dump(output, f)

        self.new_key.emit(new_key)
        self.close()