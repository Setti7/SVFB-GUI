import json, datetime, requests
from urllib.request import urlopen
from urllib.error import URLError
import sys, numpy as np, os, webbrowser
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QDialog, QMenuBar
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt5 import QtGui
from PyQt5.uic import loadUi
from GUI_functions import send_files
from GUI_functions.save_data import SaveData

BASE_URL = 'http://127.0.0.1'
# TODO: programa crash quando faz login dps de logout. Aconteceu na viagem com servidor 127.0.0.1. Acho que foi consertado. Erro era em CheckForOnlineScore (usando method QThread.sleep(15000), porém não era um QThread e por isso dava erro

class Worker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal
    updated_score = pyqtSignal(int)
    auto_send_response = pyqtSignal(int)

    def __init__(self, key, res, zoom, autosend, username=None, password=None, parent=None):
        QObject.__init__(self, parent=parent)

        self.res = res
        self.zoom = zoom
        self.autosend = autosend
        self.key = key
        self.username = username
        self.password = password

        resolution = [int(x_or_y) for x_or_y in self.res.split('x')]

        self.work = SaveData(res=resolution, key=self.key, autosend=self.autosend, zoom=self.zoom)
        self.work.data_response_code.connect(self.response_code_control)
        self.work.score.connect(self.score_control)

    def response_code_control(self, code):
        self.auto_send_response.emit(code)

    def score_control(self, score):
        self.updated_score.emit(score)

    def do_work(self):
        self.work.main()

        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.work.stop()


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


class CheckForOnlineScore(QObject):
    online_score = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, session, parent=None):
        QObject.__init__(self, parent=parent)
        self.client = session
        self.continue_run = True

    def timer_for_checker(self):

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_online_score)
        self.timer.start(15000)

    @pyqtSlot()
    def check_online_score(self):
        score_url = BASE_URL + '/score'

        try:

            if self.continue_run:
                response = self.client.get(score_url)
                output = json.loads(response.text)['score']
                self.online_score.emit(output)
                print("ONLINE SCORE: {}".format(output))

                self.timer_for_checker()
            else:
                self.finished.emit()
                print("finish emitted")

        except Exception as e:
            print(e)
            print("#004")


    def stop(self):
        self.continue_run = False


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
        with open("config.txt", "r") as f:
            output = json.loads(f.read())
            new_key = str(self.change_key.text()).upper()
            output['Used key'] = new_key

        with open("config.txt", "w") as f:
            json.dump(output, f)

        self.new_key.emit(new_key)
        self.close()


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
            print("#010")

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


class Widget(QWidget):
    stop_signal = pyqtSignal()

    with open("config.txt", "r") as f:
        output = json.loads(f.read())
        version = output['Version']
        date = datetime.datetime.strptime(output['Date'], '%Y-%m-%d')
        used_key = output["Used key"]
        res = output["Resolution"]
        username = output['User']
        password = output['Password']
        auto_send = output['Auto-send']
        zoom = int(output["Zoom"])

    def __init__(self):
        super().__init__()
        self.initUI()

        if self.res == '1280x600': res_index = 0
        elif self.res == '1280x720': res_index = 1
        elif self.res == '1280x760': res_index = 2
        elif self.res == '1280x800': res_index = 3
        elif self.res == '1280x960': res_index = 4
        elif self.res == '1280x1024': res_index = 5
        elif self.res == '1980x1080': res_index = 6
        else:
            self.res = '1280x720'
            res_index = 1
            with open("config.txt", 'w') as f:
                self.output['Resolution'] = self.res
                json.dump(self.output, f)

        print("Zoom -5: aparenta ok\n"
              "Zoom -4: ok\n"
              "Zoom -3: apresentou rompimento\n"
              "Zoom -2: apresentou rompimento\n"
              "Zoom -1: não lembro\n"
              "Zoom 0: parece ok\n"
              "outros: não testei\t"
              "#003\n")

        # Starting threads for startup verification
        self.startup_update_check()
        self.startup_authorize_user()

        # Icons:
        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.png'))
        self.dog_getting_up = QtGui.QMovie('media\\animations\\Dog Getting Up4.gif')
        self.dog_running = QtGui.QMovie('media\\animations\\Dog Running4.gif')
        self.dog_idle = QtGui.QMovie('media\\animations\\Dog Idle2.gif')
        self.dog_sitting_down = QtGui.QMovie("media\\animations\\Dog Sitting Down4.gif")
        self.icons_label.setMovie(self.dog_idle)
        self.dog_idle.start()


        # Setting default labels and texts:
        self.v_label.setText("v{}".format(self.version))
        self.used_key_label.setText('Using "{}" key to fish'.format(self.used_key))
        self.zoom_levelSpinBox.setValue(self.zoom)
        self.res_selection.setCurrentIndex(res_index)
        self.score_file = "Data\\frames.npy"
        if os.path.exists(self.score_file):
            score = sum(list(np.load(self.score_file)))
            self.update_score(score)

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
        self.zoom_levelSpinBox.valueChanged.connect(self.zoom_value_changed)
        self.res_selection.currentIndexChanged.connect(self.res_selection_changed)


    def initUI(self):
        loadUi('designs\\GUI_design_with_res.ui', self)

        # Menu
        self.menu = QMenuBar(self)
        self.menu_options = self.menu.addMenu('Options')

        self.delete_last_data_btn = self.menu_options.addAction("Delete last data")
        self.delete_last_data_btn.triggered.connect(self.delete_last_data)

        self.menu_options.addSeparator()

        self.logout_btn = self.menu_options.addAction("Logout")
        self.logout_btn.triggered.connect(self.logout)

        self.login_btn = self.menu_options.addAction("Login")
        self.login_btn.triggered.connect(lambda: self.login_control({'Logged': False}))

        visit_ranking = self.menu.addAction('Ranking')
        visit_ranking.triggered.connect(lambda: webbrowser.open(BASE_URL + "/ranking"))

        website = self.menu.addAction('Github [ICON]')
        website.triggered.connect(lambda: webbrowser.open("https://www.github.com/Setti7/Stardew-Valley-Fishing-Bot"))

        self.menu.setFixedSize(self.width(), 25)

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

    def zoom_value_changed(self):
        self.zoom = self.zoom_levelSpinBox.text()

        with open ("config.txt", 'r') as f:
            output = json.loads(f.read())
            output["Zoom"] = self.zoom

        with open("config.txt", "w") as f:
            json.dump(output, f)

    def res_selection_changed(self):
        self.res = self.res_selection.currentText()

        with open ("config.txt", 'r') as f:
            output = json.loads(f.read())
            output["Resolution"] = self.res

        with open("config.txt", "w") as f:
            json.dump(output, f)


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

        # Thread:
        self.login_thread = QThread()
        self.login_worker = LoginWorker(self.username, self.password)
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


    # Update Widget elements
    def update_key(self, key): # Updating used key for fishing after ChangeKey dialog:
        self.used_key_label.setText('Using "{}" key'.format(key))
        self.used_key = key

    def update_score(self, score, **kwargs):
        self.score = score
        self.score_label.setText("Score: {}".format(int(score)))

        if 'online_score' in kwargs.keys():
            online_score = kwargs['online_score']
            if kwargs['online_score'] != self.score:
                self.send_btn.setText("Send Data ({} not sent yet)".format(int(self.score - online_score)))

    def dog_go_idle(self):
        self.icons_label.setMovie(self.dog_idle)
        self.dog_idle.start()
        self.dog_timer2.stop()

    def dog_run(self):
        self.icons_label.setMovie(self.dog_running)
        self.dog_running.start()
        self.dog_timer.stop()


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
            updateBox.setWindowIcon(QtGui.QIcon('media\\logo\\logo.png'))

            text = """Version available: {1}\n\n{2}""".format(current_version, new_version,
                                                              changes)
            updateBox.setDetailedText(text)

            updateBox.setEscapeButton(QMessageBox.Close)
            updateBox.addButton(QMessageBox.Close)
            self.v_label.setText("v{} (v{} available)".format(self.version, new_version))

            ok = updateBox.addButton(QMessageBox.Ok)
            ok.clicked.connect(lambda: webbrowser.open(BASE_URL + "/home"))
            updateBox.exec_()

        else:
            updateBox = QMessageBox()
            updateBox.setIcon(QMessageBox.Warning)
            updateBox.setText("<strong>Your version is super outdated and is not useful anymore!</strong>")
            updateBox.setInformativeText(
                """Please click <i>Ok</i> to download the newer one. You can also see the changelog details below! <small>(The critical change is highlighted)</small>"""
            )
            updateBox.setWindowTitle("Unsupported Software")
            updateBox.setWindowIcon(QtGui.QIcon('media\\logo\\logo.png'))

            text = """Version available: {1}\n\n{2}""".format(current_version, new_version,
                                                              changes)
            updateBox.setDetailedText(text)

            updateBox.setEscapeButton(QMessageBox.Close)
            updateBox.addButton(QMessageBox.Close)
            self.v_label.setText("v{} (v{} REQUIRED)".format(self.version, new_version))

            ok = updateBox.addButton(QMessageBox.Ok)
            ok.clicked.connect(lambda: webbrowser.open(BASE_URL + "/home"))
            updateBox.exec_()
            self.close()


    # Data processes:
    def data_start_action(self):
        self.data_start.setEnabled(False)
        self.data_stop.setEnabled(True)
        self.res_selection.setEnabled(False)
        self.zoom_levelSpinBox.setEnabled(False)
        self.change_key_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.auto_send_checkbox.setEnabled(False)
        self.logout_btn.setEnabled(False)
        self.login_btn.setEnabled(False)
        self.delete_last_data_btn.setEnabled(False)

        # Icon
        self.icons_label.setMovie(self.dog_getting_up)
        self.dog_getting_up.start()
        self.dog_timer = QTimer()
        self.dog_timer.timeout.connect(self.dog_run)
        self.dog_timer.start(370)

        try: # This is necessary to make the dog don't go idle if the user clicks start>stop too fast.
            self.dog_timer2.deleteLater()
        except:
            pass # fight me

        # Thread: __init__
        self.thread = QThread()
        self.worker = Worker(self.used_key, self.res, self.zoom, self.auto_send)
        self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.do_work)
        self.thread.finished.connect(self.worker.stop)

        self.worker.auto_send_response.connect(self.auto_send_response_code_controller)
        self.worker.updated_score.connect(self.update_score)

        self.thread.start()

    def data_stop_action(self):
        self.data_start.setEnabled(True)
        self.data_stop.setEnabled(False)
        self.res_selection.setEnabled(True)
        self.zoom_levelSpinBox.setEnabled(True)
        self.change_key_btn.setEnabled(True)
        self.logout_btn.setEnabled(True)
        self.login_btn.setEnabled(True)
        self.delete_last_data_btn.setEnabled(True)

        if self.send_btn.text() != "Can't send data while offline":
            self.send_btn.setEnabled(True)
            self.auto_send_checkbox.setEnabled(True)

        self.stop_signal.emit()  # emit the finished signal on stop

        # Icon
        self.dog_timer.deleteLater()
        self.icons_label.setMovie(self.dog_sitting_down)
        self.dog_sitting_down.start()

        self.dog_timer2 = QTimer()
        self.dog_timer2.timeout.connect(self.dog_go_idle)
        self.dog_timer2.start(370)

        if os.path.exists(self.score_file):
            score = sum(list(np.load(self.score_file)))
            self.update_score(score)

    def send_data(self):
        response = send_files.send_data(BASE_URL, self.username, self.password)

        if response == 200:
            self.send_status_label.setText("Success! Thank you for helping!")
            self.send_status_label.setStyleSheet("color: #28a745;")
            self.send_btn.setText("Send Data")

        else:
            pass
            self.send_status_label.setText('Error! Verify your connection')
            self.send_status_label.setStyleSheet("color: #dc3545;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.send_status_label.clear)
        self.timer.start(5000)

    def auto_send_response_code_controller(self, code):

        if code == 200:
            self.send_status_label.setText("Success! Thank you for helping!")
            self.send_status_label.setStyleSheet("color: #28a745;")
            self.send_btn.setText("Send Data")

        else:
            pass
            self.send_status_label.setText('Error! Verify your connection')
            self.send_status_label.setStyleSheet("color: #dc3545;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.send_status_label.clear)
        self.timer.start(5000)

    def delete_last_data(self):

        choice = QMessageBox.question(self, "Warning!", "Are you sure you want to delete the data from your last fishing session?", QMessageBox.Yes | QMessageBox.No)

        if choice == QMessageBox.Yes:

            try:

                file_name = 'Data\\training_data.npy'
                frame_file = 'Data\\frames.npy'

                if os.path.isfile(file_name):
                    print("Training file exists, loading previos data!")
                    training_data = list(np.load(file_name))

                else:
                    print("Training file does not exist, starting fresh!")
                    training_data = []

                if os.path.isfile(frame_file):
                    print("Frames file exists, loading previos data!")
                    frames = list(np.load(frame_file))

                else:
                    print("Frames file does not exist, starting fresh!")
                    frames = []

                training_data = list(np.load(file_name))
                frames = list(np.load(frame_file))

                before_score = sum(frames)

                print(len(frames))
                print(frames)
                print(len(training_data))

                del training_data[-frames[-1]:] # TODO: acho que poderia ser 'del training_data[frames[0]:]'
                del frames[-1]

                np.save(file_name, training_data)
                np.save(frame_file, frames)

                after_score = sum(frames)

                string = 'Last data was removed successfully!\n\nScore before deletion:\t' + str(before_score) + '\nYour score now:\t\t' + str(after_score)
                print(string)
                QMessageBox.information(self, "Success", string)

                self.update_score(after_score)
                if self.auto_send and self.username: # TODO: Devo deixar isso aqui ou fazer upload automático da Data, mesmo sem autorizar?
                    self.send_data()

                elif not self.auto_send and self.username:
                    self.send_status_label.setStyleSheet('')
                    self.send_status_label.setText("Don't forget to upload your data!")

                    self.timer = QTimer()
                    self.timer.timeout.connect(self.send_status_label.clear)
                    self.timer.start(5000)

            except Exception as e:
                print(e)
                QMessageBox.information(self, "Oops!", "Could not delete the Data")


    # Account functions:
    def login_control(self, results):
        print(results)

        if results['Logged']:
            self.username = results['Username']
            self.password = results['Password']

            self.user_has_logged({"Username": self.username, "Password": self.password, "Session": results['Session']})
            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(True)

        else:
            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(True)
            self.accnt_manager = AccountManager()
            self.accnt_manager.user_logged.connect(self.user_has_logged)
            self.accnt_manager.rejected.connect(self.login_rejected)
            self.accnt_manager.exec_()

    def login_rejected(self):

        self.username_label.setText("Not logged")
        self.logout_btn.setVisible(False)
        self.login_btn.setVisible(True)

    def call_update_score(self, online_score):
        self.update_score(self.score, online_score=online_score)

    def user_has_logged(self, user_info):
        print("USER HAS LOGGED #008")
        self.username = user_info['Username']
        self.password = user_info['Password']
        client = user_info['Session']

        self.username_label.setText(self.username)

        try:
            self.thread.isRunning() # If data is being collected:

        except:
            self.send_btn.setEnabled(True)
            self.auto_send_checkbox.setEnabled(True)

        self.send_btn.setText("Send data")

        try:

            self.score_thread = QThread()
            self.score_worker = CheckForOnlineScore(client)
            self.score_worker.moveToThread(self.score_thread)

            self.score_worker.finished.connect(self.score_thread.quit)  # connect the workers finished signal to stop thread
            self.score_worker.finished.connect(self.score_worker.deleteLater)  # connect the workers finished signal to clean up worker
            self.score_thread.finished.connect(self.score_thread.deleteLater)  # connect threads finished signal to clean up thread

            self.score_thread.started.connect(self.score_worker.check_online_score)
            self.score_thread.finished.connect(self.score_worker.stop)
            self.score_worker.online_score.connect(self.call_update_score)

            self.score_thread.start()
            print('Thread starting')

        except Exception as e:
            print(e)
            print("#005")

    def logout(self):
        self.username = ''
        self.password = ''

        self.username_label.setText("Not logged")
        self.send_btn.setText("Can't send data while offline")
        self.send_btn.setEnabled(False)
        self.auto_send_checkbox.setEnabled(False)

        try:
            self.score_worker.stop()
        except Exception as e:
            print(e)
            print("#006")

        with open('config.txt', 'r') as f:
            output = json.loads(f.read())
            output['Password'] = ''
            output['User'] = ''

        with open('config.txt', 'w') as f:
            json.dump(output, f)

        self.login_control({"Logged": False})


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
                    self.result.emit({"Logged": True, "Username": self.username, "Password": self.password, "Session": client})

                else:
                    self.result.emit({"Logged": False})
                    self.finished.emit()
                    self.continue_run = False

            except:
                print("Offline")
                QThread.sleep(30)

    def stop(self):
        self.continue_run = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Widget()
    sys.exit(app.exec_())
