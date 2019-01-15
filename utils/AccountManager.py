import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')
import json, requests, webbrowser
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtGui
from PyQt5.uic import loadUi
from utils.Globals import VALIDATE_TOKEN_URL, GET_TOKEN_URL


class AccountManager(QDialog):
    user_logged = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        loadUi('designs\\login_dialog_token.ui', self)

        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))
        self.login_error.setStyleSheet("color: #dc3545;")
        self.setFixedSize(287, 161)

        self.get_token_btn.sizeHint()
        self.login_btn.clicked.connect(self.login)
        self.create_account_btn.clicked.connect(lambda: print(f'w: {self.width()} h: {self.height()}'))#webbrowser.open(LOGIN_URL))
        self.get_token_btn.clicked.connect(lambda: webbrowser.open(GET_TOKEN_URL))

        # Hiding error labels
        self.login_error.hide()

        # Control variables
        self.login_resized = False

    def login(self):

        token = self.tokenLineEdit.text()

        try:

            response = requests.post(VALIDATE_TOKEN_URL, headers={"Authorization": f"Token {token}"})
            result = json.loads(response.content)

            if result['valid-token']:
                username = result['username']

                with open("config.json", "r") as f:
                    output = json.loads(f.read())
                    output['User'] = username
                    output['Token'] = token
                    output['Ignore Login Popup'] = False

                with open("config.json", "w") as f:
                    json.dump(output, f, indent=2)

                self.user_logged.emit({"Username": username, "Token": token})
                self.accept()

            else:

                if not self.login_resized:
                    width = self.width()
                    height = self.height()
                    self.setFixedSize(width, height + 20)
                    self.login_resized = True

                self.login_error.show()
                self.tokenLineEdit.clear()

        except Exception as e:
            print(e)
