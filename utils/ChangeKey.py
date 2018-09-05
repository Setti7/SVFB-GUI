import json

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator, QIcon

iconpath = "media\\Images\\use-tool-key.png"

class ChangeKey(QDialog):

    def __init__(self, key):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QIcon('media\\logo\\logo.ico'))
        self.help_label.setToolTip('<img src="%s">' % (iconpath))

        if key.upper() == "LEFT-CLICK":
            self.change_key.setEnabled(False)
            self.check_box.setChecked(True)
            self.change_key.setMaxLength(10)

            self.change_key.setText("left-click")

        else:
            self.change_key.setEnabled(True)
            self.check_box.setChecked(False)
            self.change_key.setMaxLength(1)

            self.change_key.setText(key.upper())

        # Variable that holds the new key:
        self.new_key = ''

        self.save_btn.clicked.connect(self.save)
        self.close_btn.clicked.connect(self.close)
        self.change_key.setFocus(True)
        self.check_box.stateChanged.connect(self.check_box_clicked)

    def initUI(self):
        loadUi('designs\\key_used_dialog.ui', self)

        txt_validator = QRegExpValidator(QRegExp(r'[a-z-A-Z]'), self.change_key)
        self.change_key.setValidator(txt_validator)

    def check_box_clicked(self):
        if self.check_box.isChecked():

            self.change_key.setEnabled(False)
            self.change_key.setMaxLength(10)

            self.change_key.setText("left-click")

        else:

            if self.change_key.text() == "left-click":
                self.change_key.setText("C")

            else:
                with open("config.json", "r") as f:
                    output = json.loads(f.read())
                    self.change_key.setText(output['Used key'])

            self.change_key.setEnabled(True)
            self.change_key.setMaxLength(1)

    def save(self):
        self.new_key = str(self.change_key.text()).upper()

        with open("config.json", "r") as f:
            output = json.loads(f.read())
            output['Used key'] = self.new_key

        with open("config.json", "w") as f:
            json.dump(output, f, indent=2)

        self.accept()
