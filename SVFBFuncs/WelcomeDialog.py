
import json, datetime
from urllib.request import urlopen
from urllib.error import URLError
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtGui
from SVFBFuncs.Globals import BASE_URL, VERSION, RELEASE_DATE


class WelcomeDialog(QObject):

    def __init__(self, *_, parent=None):
        QObject.__init__(self, parent=parent)

        msg_box = QMessageBox()
        msg_box.setText("<strong>Thank you for helping the project!</strong>")
        msg_box.setInformativeText("Don't forget to configure your settings so the application can work correctly.")
        msg_box.setWindowTitle("Welcome!")
        msg_box.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))

        msg_box.setEscapeButton(QMessageBox.Close)
        ok = msg_box.addButton(QMessageBox.Ok)

        ok.clicked.connect(self.accept)

        msg_box.exec_()


    def accept(self):

        with open("config.json", 'r') as f:
            output = json.loads(f.read())
            output["First Time Running"] = False

        with open("config.json", "w") as f:
            json.dump(output, f, indent=2)
