import json, requests
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtGui
from PyQt5.uic import loadUi

BASE_URL = 'http://127.0.0.1'

class AccountManager(QDialog):
    user_logged = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()

        # Start session:
        self.client = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter(max_retries=2)
        self.client.mount('http://', self.adapter)  # client.mount('https://', adapter)

    def initUI(self):
        loadUi('designs\\login_dialog.ui', self)

        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.png'))
        self.login_btn.clicked.connect(self.login)
        self.create_account_btn.clicked.connect(self.create_account)
        self.login_error.hide()
        self.create_account_error.hide()
        self.create_account_frame.hide()
        self.resize(287, 160)
        self.login_resized = False
        self.clicked_first = True

    def create_account(self):
        if self.clicked_first:
            width = self.width()
            height = self.height()
            self.resize(width, height + 175)
            self.create_account_error.setText("""Complete the spaces below to \ncreate a new account.""")
            self.create_account_error.show()
            self.create_account_btn.clicked.connect(self.create_account_online)
            self.create_account_frame.show()
            self.clicked_first = False

        else:
            self.create_account_btn.clicked.connect(self.create_account_online)
            self.clicked_first = False

    def create_account_online(self):
        create_account_url = BASE_URL + "/accounts/create/?next=/home/"

        username = self.create_username.text()
        password1 = self.create_password.text()
        password2 = self.create_password_confirm.text()
        email = self.create_email.text()
        self.create_resized = False

        try:
            self.client.get(create_account_url)
            csrftoken = self.client.cookies['csrftoken']
            login_data = {'username': username, 'password1': password1, 'password2': password2, 'email': email,
                          'csrfmiddlewaretoken': csrftoken}

            response = self.client.post(create_account_url, data=login_data)
            success_text = "Logout from {}".format(username)

            if success_text in str(response.content):

                with open("config.txt", "r") as f:
                    output = json.loads(f.read())
                    output['User'] = username
                    output['Password'] = password1

                with open("config.txt", "w") as f:
                    json.dump(output, f)

                self.user_logged.emit({"Username": username, "Password": password1, "Session": self.client})
                self.accept()

            else:

                self.create_password.clear()
                self.create_password_confirm.clear()
                self.create_account_error.setText(
                    """An error ocurred. Please try again.<br>If the error persists, create the account <a href="http://127.0.0.1:8000/accounts/create/?next=/home/"><span style=" text-decoration: underline; color:#0000ff;">here</span></a>""")

        except Exception as e:
            print(e)
            print("Error accnt creation #010")

    def login(self):
        login_url = BASE_URL + "/accounts/login/?next=/home/"

        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()

        try:  # Change this to use the LOGINWORKER, so it is less code

            self.client.get(login_url)
            csrftoken = self.client.cookies['csrftoken']
            login_data = {'username': username, 'password': password, 'csrfmiddlewaretoken': csrftoken}

            response = self.client.post(login_url, data=login_data)
            success_text = "Logout from {}".format(username)

            print("{} #721".format(response))

            if success_text in str(response.content):

                with open("config.txt", "r") as f:
                    output = json.loads(f.read())
                    output['User'] = username
                    output['Password'] = password

                with open("config.txt", "w") as f:
                    json.dump(output, f)

                self.user_logged.emit({"Username": username, "Password": password, "Session": self.client})
                self.accept()


            else:

                print(self.width(), self.height())

                if not self.login_resized:
                    width = self.width()
                    height = self.height()
                    self.resize(width, height + 20)
                    self.login_resized = True

                self.login_error.show()
                self.passwordLineEdit.clear()

        except Exception as e:
            print(e)