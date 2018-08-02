import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import json, requests
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtGui
from PyQt5.uic import loadUi
from SVFBFuncs.Globals import BASE_URL, GET_TOKEN_URL, CREATE_ACCOUNT_URL


class AccountManager(QDialog):
    user_logged = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        loadUi('designs\\login_dialog.ui', self)

        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))
        self.login_error.setStyleSheet("color: #dc3545;")
        self.setFixedSize(290, 160)

        self.login_btn.clicked.connect(self.login)
        self.create_account_btn.clicked.connect(self.create_account)

        # Hiding error labels
        self.login_error.hide()
        self.create_account_error.hide()
        self.create_account_frame.hide()
        self.username_error_label.hide()
        self.email_error_label.hide()
        self.password_error_label.hide()

        # Control variables
        self.login_resized = False
        self.email_error = False
        self.password_error = False
        self.username_error = False


    def create_account(self):
        # When clicking on create account for the first time, the window expand, showing the create-account form
        width = self.width()
        height = self.height()
        self.setFixedSize(width, height + 175)
        self.create_account_error.setText("""Complete the spaces below to \ncreate a new account.""")
        self.create_account_error.show()
        self.create_account_frame.show()

        # Reroute the create account button to the next function, as the window is already expanded
        self.create_account_btn.clicked.disconnect()
        self.create_account_btn.clicked.connect(self.create_account_online)


    def create_account_online(self):

        # Get info from form
        username = self.create_username.text()
        password1 = self.create_password.text()
        password2 = self.create_password_confirm.text()
        email = self.create_email.text()

        # Control variable
        self.create_resized = False

        # If there is a previous form error raised by the end of this function, clear it before re-sending the form
        # on the next-click. This allows the user to see only the most recent errors in the form.
        if self.email_error:
            width = self.width()
            height = self.height()
            self.setFixedSize(width, height - 18)
            self.email_error_label.hide()
            self.email_error = False

        if self.username_error:
            width = self.width()
            height = self.height()
            self.setFixedSize(width, height - 18)
            self.username_error_label.hide()
            self.username_error = False

        if self.password_error:
            width = self.width()
            height = self.height()
            self.setFixedSize(width, height - 18)
            self.password_error_label.hide()
            self.password_error = False


        try:
            login_data = {'username': username, 'password1': password1, 'password2': password2, 'email': email}

            response = requests.post(CREATE_ACCOUNT_URL, data=login_data)
            result = json.loads(response.text)

            if result['success']:

                token = result['token']

                with open("config.json", "r") as f:
                    output = json.loads(f.read())
                    output['User'] = username
                    output['Ignore Login Popup'] = False
                    output['Token'] = token

                with open("config.json", "w") as f:
                    json.dump(output, f, indent=2)

                self.user_logged.emit({"Username": username, "Token": token})
                self.accept()

            else:

                self.create_password.clear()
                self.create_password_confirm.clear()
                self.create_account_error.setStyleSheet("color: #dc3545;")
                self.create_account_error.setText(
                    'An error ocurred. Please try again.<br>If the error persists, create the account <a href="{base_url}/accounts/create"><span style=" text-decoration: underline; color:#0000ff;">here</span></a>'.format(
                        base_url=BASE_URL
                    ))

                errors = json.loads(result['errors'])

                # Email errors:
                if 'email' in errors:
                    self.email_error_label.setText(f"{errors['email'][0]['message']}")
                    self.email_error_label.setVisible(True)

                    # If there was no previous error, expand the window so the error can be seen.
                    if not self.email_error:
                        width = self.width()
                        height = self.height()
                        self.setFixedSize(width, height + 18)
                        self.email_error = True

                # Username errors
                if 'username' in errors:
                    self.username_error_label.setText(f"{errors['username'][0]['message']}")
                    self.username_error_label.setVisible(True)

                    if not self.username_error:
                        width = self.width()
                        height = self.height()
                        self.setFixedSize(width, height + 18)
                        self.username_error = True

                # Password errors
                if 'password1' in errors or 'password2' in errors:

                    # If server sent only password1 errors, set it as the error message
                    if 'password1' in errors and not 'password2' in errors:
                        password_error = f"{errors['password1'][0]['message']}"

                    # If server sent only password2 errors, set it as the error message
                    elif not 'password1' in errors and 'password2' in errors:
                        password_error = f"{errors['password2'][0]['message']}"

                    # If server sent password1 AND password2 errors, set it as the error message only if they are not
                    # the same message
                    else:

                        if not errors['password1'][0]['message'] == errors['password2'][0]['message']:
                            password_error = f"{errors['password1'][0]['message']}, {errors['password2'][0]['message']}"

                        else:
                            password_error = f"{errors['password1'][0]['message']}"

                    self.password_error_label.setText(password_error)
                    self.password_error_label.setVisible(True)

                    if not self.password_error:
                        width = self.width()
                        height = self.height()
                        self.setFixedSize(width, height + 18)
                        self.password_error = True


        except Exception as e:
            logger.error(f"Error while creating account: {e}")

    def login(self):

        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()

        try:

            login_data = {'username': username, 'password': password}

            response = requests.post(GET_TOKEN_URL, data=login_data)
            result = json.loads(response.text)

            if 'token' in result.keys():

                token = result['token']

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

                # print(self.width(), self.height())

                if not self.login_resized:
                    width = self.width()
                    height = self.height()
                    self.setFixedSize(width, height + 20)
                    self.login_resized = True

                self.login_error.show()
                self.passwordLineEdit.clear()

        except Exception as e:
            print(e)