import json

from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

iconpath = "media\\Images\\use-tool-key.png"

class ChangeKey(QDialog):

    def __init__(self, key):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))
        self.help_label.setToolTip('<img src="%s">' % (iconpath))
        self.change_key.setText(key.upper())

        # Variable that holds the new key:
        self.new_key = ''

        self.save_btn.clicked.connect(self.save)
        self.close_btn.clicked.connect(self.close)
        self.change_key.setFocus(True)

    def initUI(self):
        loadUi('designs\\key_used_dialog.ui', self)

    def save(self):
        self.new_key = str(self.change_key.text()).upper()

        with open("config.json", "r") as f:
            output = json.loads(f.read())
            output['Used key'] = self.new_key

        with open("config.json", "w") as f:
            json.dump(output, f, indent=2)

        self.accept()
