import json
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtGui
from PyQt5.uic import loadUi

class Settings(QDialog):
    finished = pyqtSignal(dict)

    def __init__(self, used_key, zoom, res_index):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))
        self.invalid_settings_label.setStyleSheet("color: #dc3545;")

        self.save_btn.clicked.connect(self.save)
        self.close_btn.clicked.connect(self.close)

        self.change_key.setText(used_key.upper())
        self.zoom_levelSpinBox_2.setValue(zoom)
        self.res_selection_2.setCurrentIndex(res_index)


    def initUI(self):
        loadUi('designs\\settings_dialog.ui', self)

    def save(self):
        if not self.change_key.text():
            self.invalid_settings_label.setText("Invalid Key")

        else:
            self.finished.emit({"resolution": self.res_selection_2.currentText(), "key": self.change_key.text(), "zoom": self.zoom_levelSpinBox_2.text()})
            self.change_key.setText(self.change_key.text().upper())
            self.invalid_settings_label.setText("")
            self.close()