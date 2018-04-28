import json, datetime, requests
from urllib.request import urlopen
from urllib.error import URLError
import sys, numpy as np, os, webbrowser
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QDialog
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt5 import QtGui
from PyQt5.uic import loadUi
import save_data, send_files

BASE_URL = 'http://192.168.1.102'


class Worker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, key, res, autosend, username=None, password=None, parent=None):
        QObject.__init__(self, parent=parent)

        self.res = res
        self.autosend = autosend
        self.key = key
        self.username = username
        self.password = password

    def do_work(self):
        res = [int(x_or_y) for x_or_y in self.res.split('x')]
        save_data.main(res=res, key=self.key, autosend=self.autosend)
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
            data = urlopen(BASE_URL + "/version-control").read()
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
    new_key = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('logo\\logo.png'))

        self.save_btn.clicked.connect(self.save)
        self.close_btn.clicked.connect(self.close)
        self.change_key.setFocus(True)

    def initUI(self):
        loadUi('designs\\key_used_dialog.ui', self)

    def save(self):
        with open("config.txt", "r") as f:
            output = json.loads(f.read())
            new_key = str(self.change_key.text()).upper()
            output['Used key'] = new_key

        with open("config.txt", "w") as f:
            json.dump(output, f)

        self.new_key.emit(new_key)
        self.close()


class AccountManager(QDialog):
    user_logged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

        # Start session:
        self.client = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter(max_retries=2)
        self.client.mount('http://', self.adapter)  # client.mount('https://', adapter)

    def initUI(self):
        loadUi('designs\\login_dialog.ui', self)

        self.setWindowIcon(QtGui.QIcon('logo\\logo.png'))
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

                self.user_logged.emit(username)
                self.close()


            else:

                self.create_password.clear()
                self.create_password_confirm.clear()
                self.create_account_error.setText(
                    """An error ocurred. Please try again.<br>If the error persists, create the account <a href="http://127.0.0.1:8000/accounts/create/?next=/home/"><span style=" text-decoration: underline; color:#0000ff;">here</span></a>""")

        except Exception as e:
            print(e)

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

            print(response)

            if success_text in str(response.content):

                with open("config.txt", "r") as f:
                    output = json.loads(f.read())
                    output['User'] = username
                    output['Password'] = password

                with open("config.txt", "w") as f:
                    json.dump(output, f)

                self.user_logged.emit(username)
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
        username = output['User']
        auto_send = output['Auto-send']

    def __init__(self):
        super().__init__()
        self.initUI()

        # Starting threads for startup verification
        self.startup_update_check()
        self.startup_authorize_user()

        # Icons:
        self.setWindowIcon(QtGui.QIcon('logo\\logo.png'))
        self.loading_icon = QtGui.QMovie('animations\\loading_icon.gif')
        self.fish_animation = QtGui.QMovie('animations\\loading_icon.gif')

        # Setting default labels and texts:
        self.v_label.setText("v{}".format(self.version))
        self.used_key_label.setText('Using "{}" key to fish'.format(self.used_key))
        self.score_file = "Data\\frames.npy"
        if os.path.exists(self.score_file):
            self.score = sum(list(np.load(self.score_file)))
            self.score_label.setText("Score: {}".format(str(self.score)))

        # If auto_send config is not checked, let it be unchecked
        if not self.auto_send:
            self.auto_send_checkbox.setChecked(False)

        # Configuring Signals:
        self.dialog = ChangeKey()
        self.dialog.new_key.connect(self.update_key)

        # Defining button/checkbox actions
        self.data_start.clicked.connect(self.data_start_action)
        self.data_stop.clicked.connect(self.data_stop_action)
        self.send_btn.clicked.connect(self.send_data)
        self.change_key_btn.clicked.connect(self.dialog.exec_)
        self.auto_send_checkbox.stateChanged.connect(self.auto_send_state_changed)

    def initUI(self):
        loadUi('designs\\GUI_design_with_res.ui', self)
        self.show()


    # Checking if auto_send checkbox is True/False
    def auto_send_state_changed(self):
        if self.auto_send_checkbox.isChecked():
            result = True
        else:
            result = False

        self.auto_send = result
        with open("config.txt", "r") as f:
            output = json.loads(f.read())
            output['Auto-send'] = result

        with open("config.txt", "w") as f:
            json.dump(output, f)


    # Webpage redirects (add one to ranking page)
    def go_to_update_page(self):
        webbrowser.open(BASE_URL + "/home")  # Change to download page


    # Startup Processes:
    def startup_update_check(self):
        self.check_thread = QThread()
        self.checker = CheckForUpdates()
        self.checker.moveToThread(self.check_thread)

        self.checker.finished.connect(self.check_thread.quit)  # connect the workers finished signal to stop thread

        self.checker.finished.connect(
            self.checker.deleteLater)  # connect the workers finished signal to clean up worker
        self.checker.update_text.connect(self.update_message_box)

        self.check_thread.finished.connect(
            self.check_thread.deleteLater)  # connect threads finished signal to clean up thread

        self.check_thread.started.connect(self.checker.do_work)

        self.check_thread.start()

    def startup_authorize_user(self):

        with open('config.txt', 'r') as f:
            output = json.loads(f.read())
            username = output['User']
            password = output['Password']

        # Thread:
        self.login_thread = QThread()
        self.login_worker = LoginWorker(username, password)
        self.login_worker.moveToThread(self.login_thread)

        self.login_worker.finished.connect(self.login_thread.quit)  # connect the workers finished signal to stop thread
        self.login_worker.finished.connect(
            self.login_worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.login_thread.finished.connect(
            self.login_thread.deleteLater)  # connect threads finished signal to clean up thread

        self.login_thread.started.connect(self.login_worker.do_work)
        self.login_thread.finished.connect(self.login_worker.stop)

        self.login_worker.result.connect(self.login_control)  # connect the workers finished signal to stop thread

        self.login_thread.start()


    # Notification of new version:
    def update_message_box(self, update_info):

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
            self.v_label.setText("v{} (v{} REQUIRED)".format(self.version, new_version))

            ok = updateBox.addButton(QMessageBox.Ok)
            ok.clicked.connect(self.go_to_update_page)
            updateBox.exec_()
            self.close()


    # Updating used key for fishing after ChangeKey dialog:
    def update_key(self, key):
        self.used_key_label.setText('Using "{}" key'.format(key))
        self.used_key = key


    # Data processes:
    def data_start_action(self):
        self.data_start.setEnabled(False)
        self.data_stop.setEnabled(True)
        self.res_selection.setEnabled(False)
        self.zoom_levelSpinBox.setEnabled(False)
        self.change_key_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.auto_send_checkbox.setEnabled(False)

        # Icon
        self.icons_label.setMovie(self.fish_animation)
        self.fish_animation.start()

        print("Zoom: {}".format(self.zoom_levelSpinBox.text()))

        save_data.run = True

        # Thread: __init__
        res = str(self.res_selection.currentText())

        self.thread = QThread()
        self.worker = Worker(self.used_key, res, self.auto_send)
        self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.do_work)
        self.thread.finished.connect(self.worker.stop)

        self.thread.start()

    def data_stop_action(self):
        self.data_start.setEnabled(True)
        self.data_stop.setEnabled(False)
        self.res_selection.setEnabled(True)
        self.zoom_levelSpinBox.setEnabled(True)
        self.change_key_btn.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.auto_send_checkbox.setEnabled(True)

        # Icon
        self.icons_label.clear()

        self.stop_signal.emit()  # emit the finished signal on stop

        if os.path.exists(self.score_file):
            score = sum(list(np.load(self.score_file)))
            self.score_label.setText("Score: {}".format(str(score)))

    def send_data(self):
        with open("config.txt", 'r') as f:
            output = json.loads(f.read())

        response = send_files.send_data(BASE_URL, output['User'], output['Password'])

        if response == 200:
            self.send_status_label.setText("Success! Thank you for helping!")
            self.send_status_label.setStyleSheet("color: #28a745;")

        else:
            pass
            self.send_status_label.setText('Error! Verify your connection')
            self.send_status_label.setStyleSheet("color: #dc3545;")

        print(self.send_status_label.width(), self.send_status_label.height())
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_status_label.clear)
        self.timer.start(5000)


    # Account functions:
    def login_control(self, results):
        print(results)
        if results['Logged']:
            self.username = results['Username']

            self.accnt_manager = AccountManager()
            self.accnt_manager.user_logged.connect(self.user_has_logged)

            self.accnt_manager.user_logged.emit(results['Username'])

        else:
            self.accnt_manager = AccountManager()
            self.accnt_manager.user_logged.connect(self.user_has_logged)

            self.accnt_manager.exec_()

    def user_has_logged(self, username):
        self.username = username
        self.username_label.setText(username)

        try:
            self.thread.isRunning()
            self.send_btn.setText("Send data")

        except:
            self.send_btn.setEnabled(True)
            self.auto_send_checkbox.setEnabled(True)
            self.send_btn.setText("Send data")


class LoginWorker(QObject):
    result = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, username, password, parent=None):
        QObject.__init__(self, parent=parent)
        self.password = password
        self.username = username
        self.continue_run = True

    @pyqtSlot()
    def do_work(self):

        max_retries = 2
        login_url = BASE_URL + "/accounts/login/?next=/home/"

        while self.continue_run:

            try:
                client = requests.Session()
                adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
                client.mount('http://', adapter)  # client.mount('https://', adapter)

                client.get(login_url)
                csrftoken = client.cookies['csrftoken']
                login_data = {'username': self.username, 'password': self.password, 'csrfmiddlewaretoken': csrftoken}

                response = client.post(login_url, data=login_data)
                success_text = "Logout from {}".format(self.username)

                if success_text in str(response.content):
                    self.finished.emit()
                    self.continue_run = False
                    self.result.emit({"Logged": True, "Username": self.username})

                else:
                    self.result.emit({"Logged": False})
                    self.finished.emit()
                    self.continue_run = False

            except Exception as e:
                print(e)
                QThread.sleep(30)

    def stop(self):
        self.continue_run = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Widget()
    sys.exit(app.exec_())
