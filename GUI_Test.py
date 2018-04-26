import json, datetime, requests, re
from urllib.request import urlopen
from urllib.error import URLError
import sys, numpy as np, os, webbrowser
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QDialog
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtGui
from PyQt5.uic import loadUi
import save_data


class Worker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, res, parent=None):
        QObject.__init__(self, parent=parent)
        self.res = res

        with open("config.txt", "r") as f:
            output = json.loads(f.read())
            self.key = output["Used key"]

    def do_work(self):
        res = [int(x_or_y) for x_or_y in self.res.split('x')]
        save_data.main(res, self.key)
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        save_data.run = False  # set the run condition to false on stop


class CheckForUpdates(QObject):
    finished = pyqtSignal()
    update_text = pyqtSignal(list)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    @pyqtSlot()
    def do_work(self):
        try:
            data = urlopen("http://127.0.0.1:8000/version-control").read()
            output = json.loads(data)

            changes = []
            versions = []
            critical = False
            for data in output['Version Control']:
                if datetime.datetime.strptime(data['Date'], '%Y-%m-%d') > Widget.date:
                    changes.append(data['Changes'])
                    versions.append(float(data['Version']))
                if data['Critical']:
                    critical = True

            changes = "Changes since v{} (your current version):\n".format(Widget.version) + "\n".join(changes)

            last_info = output["Version Control"][0]
            version = last_info['Version']
            date = datetime.datetime.strptime(last_info['Date'], '%Y-%m-%d')

            if Widget.date < date:
                self.update_text.emit([Widget.version, version, changes, critical])
                self.finished.emit()

        except URLError:
            print("Update timeout")

        finally:
            self.finished.emit()


class ChangeKey(QDialog):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('logo\\logo.png'))

        self.save_btn.clicked.connect(self.save)
        self.close_btn.clicked.connect(self.close)

    def initUI(self):
        loadUi('key_used_dialog.ui', self)
        #self.exec_()

    def save(self):
        with open("config.txt", "r") as f:
            output = json.loads(f.read())
            new_key = str(self.change_key.text()).upper()
            output['Used key'] = new_key

        with open("config.txt", "w") as f:
            json.dump(output, f)

        self.close()


class Login(QDialog):
    logged_user = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('logo\\logo.png'))

        self.login_btn.clicked.connect(self.login)
        self.create_account_btn.clicked.connect(self.create_account)
        self.login_error.hide()
        self.create_account_error.hide()
        self.create_account_frame.hide()
        self.resize(287, 160)
        self.login_resized = False
        self.clicked_first = True

        # Hide layout2

        # not_resize = self.errorLabel.sizePolicy()
        # not_resize.setRetainSizeWhenHidden(True)
        # self.login_error.setSizePolicy(not_resize)

    def initUI(self):
        loadUi('login_dialog.ui', self)

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
            #self.create_account_btn.setFocus(True)

        else:
            self.create_account_btn.clicked.connect(self.create_account_online)
            self.clicked_first = False


    def create_account_online(self):
        max_retries = 2
        create_account_url = "http://127.0.0.1:8000/accounts/create/?next=/home/"

        username = self.create_username.text()
        password1 = self.create_password.text()
        password2 = self.create_password_confirm.text()
        email = self.create_email.text()
        self.create_resized = False

        try:
            client = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
            # client.mount('https://', adapter)
            client.mount('http://', adapter)

            client.get(create_account_url)
            csrftoken = client.cookies['csrftoken']
            login_data = {'username': username, 'password1': password1, 'password2': password2, 'email': email, 'csrfmiddlewaretoken': csrftoken}

            response = client.post(create_account_url, data=login_data)
            success_text = "Logout from {}".format(username)

            print(response)

            if success_text in str(response.content):

                with open("config.txt", "r") as f:
                    output = json.loads(f.read())
                    output['User'] = username
                    output['Password'] = password1

                with open("config.txt", "w") as f:
                    json.dump(output, f)

                print("Logged in")
                self.close()

            else:

                self.create_password.clear()
                self.create_password_confirm.clear()
                self.create_account_error.setText("""An error ocurred. Please try again.<br>If the error persists, create the account <a href="http://127.0.0.1:8000/accounts/create/?next=/home/"><span style=" text-decoration: underline; color:#0000ff;">here</span></a>""")

        except Exception as e:
            print(e)

    def login(self):
        max_retries = 2
        login_url = "http://127.0.0.1:8000/accounts/login/?next=/home/"

        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()

        try:
            client = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
            # client.mount('https://', adapter)
            client.mount('http://', adapter)

            client.get(login_url)
            csrftoken = client.cookies['csrftoken']
            login_data = {'username': username, 'password': password, 'csrfmiddlewaretoken': csrftoken}

            response = client.post(login_url, data=login_data)
            success_text = "Logout from {}".format(username)

            print(response)

            if success_text in str(response.content):

                with open("config.txt", "r") as f:
                    output = json.loads(f.read())
                    output['User'] = username
                    output['Password'] = password

                with open("config.txt", "w") as f:
                    json.dump(output, f)

                print("Logged in")
                self.close()

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


class Widget(QWidget):
    stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread

    with open("config.txt", "r") as f:
        output = json.loads(f.read())
        version = output['Version']
        date = datetime.datetime.strptime(output['Date'], '%Y-%m-%d')
        used_key = output["Used key"]

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('logo\\logo.png'))
        self.v_label.setText("v{}".format(self.version))
        self.used_key_label.setText('Using "{}" key to fish'.format(self.used_key))
        self.data_stop.setEnabled(False)

        if not self.authorize_user():
            login = Login()
            login.exec_()

            with open("config.txt", "r") as f:
                output = json.loads(f.read())
                self.username = output["User"]

        self.update_check()

        # Try finding score file
        self.score_file = "Data\\frames.npy"
        if os.path.exists(self.score_file):
            score = sum(list(np.load(self.score_file)))
            self.label.setText("Score: {} ({})".format(str(score), self.username))

        self.data_start.clicked.connect(self.data_start_action)
        self.data_stop.clicked.connect(self.data_stop_action)
        self.send_btn.clicked.connect(self.go_to_website)
        self.change_key_btn.clicked.connect(self.change_key)

    def initUI(self):
        loadUi('GUI_design_with_res.ui', self)
        self.show()

    def go_to_website(self):
        webbrowser.open("http://127.0.0.1:8000/ranking")

    def go_to_update_page(self):
        webbrowser.open("http://127.0.0.1:8000/home")  # Change to download page

    def update_check(self):
        self.check_thread = QThread()
        self.checker = CheckForUpdates()
        self.checker.moveToThread(self.check_thread)

        self.checker.finished.connect(self.check_thread.quit)  # connect the workers finished signal to stop thread

        self.checker.finished.connect(
            self.checker.deleteLater)  # connect the workers finished signal to clean up worker
        self.checker.update_text.connect(self.update_box)

        self.check_thread.finished.connect(
            self.check_thread.deleteLater)  # connect threads finished signal to clean up thread

        self.check_thread.started.connect(self.checker.do_work)

        self.check_thread.start()

    def update_box(self, update_info):

        current_version, new_version, changes, critical = update_info

        if not critical:
            updateBox = QMessageBox()
            updateBox.setIcon(QMessageBox.Information)
            updateBox.setText("There is a new version available!")
            updateBox.setInformativeText(
                """Please click "Ok" to be redirected to the download page. You can also see the changelog details below!"""
            )
            updateBox.setWindowTitle("Update required")
            updateBox.setWindowIcon(QtGui.QIcon('logo\\logo.png'))

            text = """Version available: {1}\n\n{2}""".format(current_version, new_version,
                                                                                             changes)
            updateBox.setDetailedText(text)

            updateBox.setEscapeButton(QMessageBox.Close)
            updateBox.addButton(QMessageBox.Close)
            self.v_label.setText("v{} (v{} available)".format(self.version, new_version))

            ok = updateBox.addButton(QMessageBox.Ok)
            ok.clicked.connect(self.go_to_update_page)
            updateBox.exec_()

        else:
            updateBox = QMessageBox()
            updateBox.setIcon(QMessageBox.Warning)
            updateBox.setText("<strong>Your version is super outdated and is not useful anymore!</strong>")
            updateBox.setInformativeText(
                """Please click <i>Ok</i> to download the newer one. You can also see the changelog details below! <small>(The critical change is highlighted)</small>"""
            )
            updateBox.setWindowTitle("Unsupported Software")
            updateBox.setWindowIcon(QtGui.QIcon('logo\\logo.png'))

            text = """Version available: {1}\n\n{2}""".format(current_version, new_version,
                                                              changes)
            updateBox.setDetailedText(text)

            updateBox.setEscapeButton(QMessageBox.Close)
            updateBox.addButton(QMessageBox.Close)
            self.v_label.setText("v{} REQUIRED".format(new_version))

            ok = updateBox.addButton(QMessageBox.Ok)
            ok.clicked.connect(self.go_to_update_page)
            updateBox.exec_()
            self.close()

    def change_key(self):
        self.dialog = ChangeKey()
        self.dialog.exec_()

        with open("config.txt", "r") as f:
            output = json.loads(f.read())
            key = output['Used key']

        self.used_key_label.setText('Using "{}" key to fish'.format(key))

    def data_start_action(self):
        self.data_start.setEnabled(False)
        self.data_stop.setEnabled(True)
        self.res_selection.setEnabled(False)
        self.zoom_levelSpinBox.setEnabled(False)
        self.change_key_btn.setEnabled(False)

        print("Zoom: {}".format(self.zoom_levelSpinBox.text()))

        save_data.run = True

        # Thread: __init__
        res = str(self.res_selection.currentText())
        self.thread = QThread()
        self.worker = Worker(res)
        self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.do_work)
        self.thread.finished.connect(self.worker.stop)

        self.thread.start()
        print('Data started')

    def data_stop_action(self):
        self.data_start.setEnabled(True)
        self.data_stop.setEnabled(False)
        self.res_selection.setEnabled(True)
        self.zoom_levelSpinBox.setEnabled(True)
        self.change_key_btn.setEnabled(True)

        self.stop_signal.emit()  # emit the finished signal on stop
        print('Data stopped')

        if os.path.exists(self.score_file):
            score = sum(list(np.load(self.score_file)))
            self.label.setText("Score: {} ({})".format(str(score), self.username))

    def authorize_user(self):
        max_retries = 2
        login_url = "http://127.0.0.1:8000/accounts/login/?next=/home/"

        with open("config.txt", 'r') as f:
            output = json.loads(f.read())
            self.username = output['User']
            password = output['Password']

        try:
            client = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
            # client.mount('https://', adapter)
            client.mount('http://', adapter)

            client.get(login_url)
            csrftoken = client.cookies['csrftoken']
            login_data = {'username': self.username, 'password': password, 'csrfmiddlewaretoken': csrftoken}

            response = client.post(login_url, data=login_data)
            success_text = "Logout from {}".format(self.username)

            if success_text in str(response.content):
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Widget()
    sys.exit(app.exec_())
