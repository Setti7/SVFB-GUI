import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import json, datetime, random
import sys, numpy as np, os, webbrowser
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QMessageBox, QDialog, QMenuBar
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer, Qt
from PyQt5 import QtGui
from PyQt5.uic import loadUi
from GUI_functions.SaveData import SaveData
from GUI_functions.AccountManager import AccountManager
from GUI_functions.CheckForOnlineScore import QuickCheck
from GUI_functions.ChangeKey import ChangeKey
from GUI_functions.LoginWorker import LoginWorker
from GUI_functions.SendFiles import SendData
from GUI_functions.Loading import Loading
from GUI_functions.CheckForUpdates import CheckForUpdates

BASE_URL = 'http://127.0.0.1'
DEV = False

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Widget(QMainWindow):
    logger.info("---------- STARTED ----------")
    stop_signal = pyqtSignal()
    logout_signal = pyqtSignal()

    with open("config.json", "r") as f:
        logger.info('Loading config file')
        output = json.loads(f.read())
        version = output['Version']
        date = datetime.datetime.strptime(output['Date'], '%Y-%m-%d')
        used_key = output["Used key"]
        res = output["Resolution"]
        username = output['User']
        password = output['Password']
        auto_send = output['Auto-send']
        zoom = int(output["Zoom"])
        logger.info('Config file loaded')

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
            with open("config.json", 'w') as f:
                self.output['Resolution'] = self.res
                json.dump(self.output, f)
            logger.warning("Config file resolution invalid.")

        print("Zoom -5: aparenta ok\n"
              "Zoom -4: ok\n"
              "Zoom -3: apresentou rompimento\n"
              "Zoom -2: apresentou rompimento\n"
              "Zoom -1: não lembro\n"
              "Zoom 0: parece ok\n"
              "outros: não testei\t"
              "#003\n")

        # Starting threads for startup verification
        self.loading_dialog = Loading()

        if DEV:
            wait_time = 100
        else:
            wait_time = random.randint(3550, 4500)

        self.auth_done = False
        self.update_check_done = False
        self.call_update_box = False
        self.call_accnt_box = False
        self.startup_authorize_user()
        self.startup_update_check()

        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.loading)
        self.loading_timer.start(wait_time)


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
        logger.info("Initializing UI")

        loadUi('designs\\MainWindow.ui', self)

        # Toolbar
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        # Bot Tab
        self.contact_email.setVisible(False)
        self.send_message_btn.clicked.connect(self.send_message)

        # Menu
        self.menu_options.setEnabled(False)

        self.delete_last_data_btn.triggered.connect(self.delete_last_data)

        self.logout_btn.triggered.connect(self.logout)
        self.logout_btn.setVisible(False)

        self.login_btn.triggered.connect(lambda: self.login_control({'Logged': False}))
        self.login_btn.setVisible(False)

        visit_ranking = self.menu.addAction('Ranking')
        visit_ranking.triggered.connect(lambda: webbrowser.open(BASE_URL + "/ranking"))

        website = self.menu.addAction('Github [ICON]')
        website.triggered.connect(lambda: webbrowser.open("https://www.github.com/Setti7/Stardew-Valley-Fishing-Bot"))

        logger.info("UI Initialized")

    def loading(self):

        if self.auth_done and self.update_check_done:
            logger.info("Loading main aplication finished")
            self.loading_timer.stop()
            self.loading_timer.deleteLater()

            self.call_accnt_box = True
            self.call_update_box = True
            self.loading_dialog.close()
            self.show()

    # Checking if auto_send checkbox is True/False
    def auto_send_state_changed(self):
        if self.auto_send_checkbox.isChecked():
            result = True
        else:
            result = False

        self.auto_send = result

        with open("config.json", "r") as f:
            output = json.loads(f.read())
            output['Auto-send'] = result

        with open("config.json", "w") as f:
            json.dump(output, f)

    def zoom_value_changed(self):
        self.zoom = self.zoom_levelSpinBox.text()

        with open ("config.json", 'r') as f:
            output = json.loads(f.read())
            output["Zoom"] = self.zoom

        with open("config.json", "w") as f:
            json.dump(output, f)

    def res_selection_changed(self):
        self.res = self.res_selection.currentText()

        with open ("config.json", 'r') as f:
            output = json.loads(f.read())
            output["Resolution"] = self.res

        with open("config.json", "w") as f:
            json.dump(output, f)


    # Send message
    def send_message(self):
        txt = self.message_text.toPlainText()
        self.message_text.clear()

        if self.contact_me.isChecked():
            email = self.contact_email.text()
            # send message with email and user

        else:
            print("{}".format(txt))
            # send only message with user


    # Startup Processes:
    def startup_update_check(self):
        logger.info("Searching for updates")
        self.check_thread = QThread()
        self.checker = CheckForUpdates()
        self.checker.moveToThread(self.check_thread)

        self.checker.update_text.connect(self.update_check_over)

        self.check_thread.started.connect(self.checker.do_work)
        self.check_thread.start()

    def update_check_over(self, update_info):
        self.checker.deleteLater()
        self.check_thread.quit()
        self.check_thread.deleteLater()
        self.check_thread.wait()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(lambda: self.update_message_box(update_info))
        self.update_timer.start(200)

        self.update_check_done = True


    def startup_authorize_user(self):
        logger.info("Trying to login user")

        # Thread:
        self.login_thread = QThread()
        self.login_worker = LoginWorker(self.username, self.password)
        self.login_worker.moveToThread(self.login_thread)

        self.login_worker.result.connect(self.login_control)

        self.login_worker.result.connect(self.login_worker.deleteLater)
        self.login_worker.result.connect(self.login_thread.quit)

        self.login_thread.finished.connect(self.login_thread.deleteLater)
        self.login_thread.finished.connect(self.login_thread.wait)

        self.login_thread.started.connect(self.login_worker.do_work)
        self.login_thread.start()


    def retry_connection(self, *args):
        # *args are necessary so it can be called from the mousePressEvent

        # Label
        self.username_label.setText("Connecting")
        self.username_label.mousePressEvent = lambda x: print("Wait motherfucker")

        # Thread:
        self.login_thread = QThread()
        self.login_worker = LoginWorker(self.username, self.password)
        self.login_worker.moveToThread(self.login_thread)

        # Finished proccess
        self.login_worker.result.connect(self.login_worker.deleteLater)
        self.login_worker.result.connect(self.login_thread.quit)
        self.login_thread.finished.connect(self.login_thread.deleteLater)

        # Response from thread
        self.login_worker.result.connect(self.login_control)

        # Thread starting
        self.login_thread.started.connect(self.login_worker.do_work)
        self.login_thread.start()


        # Verifying new versions:
        self.check_thread = QThread()
        self.checker = CheckForUpdates()
        self.checker.moveToThread(self.check_thread)

        self.checker.update_text.connect(self.update_check_over)

        self.check_thread.started.connect(self.checker.do_work)
        self.check_thread.start()

        # As gui has already loaded, we jump through the code made to stop the message box from appearing while loading
        self.call_update_box = True

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

        if self.call_update_box:
            self.update_timer.stop()
            self.update_timer.deleteLater()

            update = update_info['Update']
            logger.info("Update available: %s" % update)

        else:
            update = False

        if update:
            current_version = update_info['Current Version']
            new_version = update_info['New Version']
            changes = update_info['Changes']
            critical = update_info['Critical']
            logger.info("Update critical: %s" % critical)

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

        try: # this is necessary to make the dog don't go idle if the user clicks start>stop too fast.
            self.dog_timer2.deleteLater()
        except:
            pass # fight me

        # Thread: __init__
        logger.info("Creating data thread")
        self.thread = QThread()

        if hasattr(self, "session"):
            if self.session:
                logger.info("Starting data with: {}, {}, {}, {}, {}".format(self.used_key, self.res, self.zoom, self.auto_send, self.session))
                self.worker = SaveData(self.used_key, self.res, self.zoom, self.auto_send, session=self.session)
        else:
            logger.info("Starting data with: {}, {}, {}, {}".format(self.used_key, self.res, self.zoom, False))
            self.worker = SaveData(self.used_key, self.res, self.zoom, autosend=False)

        self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.main)
        self.thread.finished.connect(self.worker.stop)

        self.worker.score.connect(self.update_score)

        if hasattr(self, 'score_worker'):
            self.worker.score.connect(self.score_worker.single_check_online_score)

        self.worker.data_response_code.connect(self.auto_send_response_code_controller)

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

        logger.info("Data stopped")
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
            logger.info("Updating score")
            self.update_score(score)

    def send_data(self):
        """
        Creates thread to send data and don't stop the execution of the program while it is uploading.
        Every time the button is clicked, it is created a new thread, that is deleted after the upload.
        """
        try:
            logger.info("Starting send data thread")
            self.send_data_thread = QThread()  # Thread criado
            self.send_data_worker = SendData(session=self.session)  # TODO: não está realmente em outro thread pq trava
            self.send_data_worker.moveToThread(self.send_data_thread)

            self.send_data_worker.status_code.connect(self.auto_send_response_code_controller)

            self.send_data_worker.status_code.connect(self.send_data_worker.deleteLater) # Finished then deletes thread and worker
            self.send_data_worker.status_code.connect(self.send_data_thread.quit)
            self.send_data_thread.finished.connect(self.send_data_thread.deleteLater)

            self.send_data_thread.started.connect(self.send_data_worker.send_data)

            self.send_data_thread.start()
            logger.info('Send data thread started')


        except Exception as e:
            logger.error("Could not start thread to send data: %s" % e)
            QMessageBox.information(self, "Oops!", "Could not start thread to send data: %s" % e)

    def auto_send_response_code_controller(self, code):
        if code == 200:
            logger.info("Data sent successfully")
            self.send_status_label.setText("Success! Thank you for helping!")
            self.send_status_label.setStyleSheet("color: #28a745;")
            self.send_btn.setText("Send Data")

        else:
            logger.error("Error while sending data. Response code: %s" % code)
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
                    logger.info("Loading training data file to delete last data")
                    training_data = list(np.load(file_name))

                else:
                    logger.warning("Training data file does not exist")
                    training_data = np.empty(shape=[0, 1])
                    logger.info("Training data file created")


                if os.path.isfile(frame_file):
                    logger.info("Loading frames file to delete last data")
                    frames = list(np.load(frame_file))

                else:
                    logger.warning("Frames file does not exist")
                    frames = list(np.empty(shape=[0, 1]))
                    logger.info("Frames file created")

                before_score = sum(frames)

                # print("len frames {}".format(len(frames)))
                # print("frames {}".format(frames))
                # print("len training_data: {}".format(len(training_data)))
                # print("this: {}".format(int(-frames[-1])))

                del training_data[int(-frames[-1]):] # TODO: acho que poderia ser 'del training_data[frames[0]:]'
                del frames[-1]

                np.save(file_name, training_data)
                np.save(frame_file, frames)

                after_score = sum(frames)

                string = 'Last data was removed successfully!\n\nScore before deletion:\t' + str(int(before_score)) + '\nYour score now:\t\t' + str(int(after_score))
                print(string)
                QMessageBox.information(self, "Success", string)

                self.update_score(after_score)
                if self.auto_send and self.username:
                    self.send_data()

                elif not self.auto_send and self.username:
                    self.send_status_label.setStyleSheet('')
                    self.send_status_label.setText("Don't forget to upload your data!")

                    self.timer = QTimer()
                    self.timer.timeout.connect(self.send_status_label.clear)
                    self.timer.start(5000)

                if hasattr(self, 'score_worker'):
                    self.score_worker.single_check_online_score()

            except Exception as e:
                logger.error("Could not delete data: %s" % e)
                QMessageBox.information(self, "Oops!", "Could not delete data: %s" % e)

    # Account functions:
    def login_control(self, results):
        self.auth_done = True

        if "Logged" in results.keys():
            if results['Logged']:
                logger.info("User successfully logged in")

                self.user_has_logged({"Username": results['Username'], "Password": results['Password'], "Session": results['Session']})
                self.login_btn.setVisible(False)
                self.logout_btn.setVisible(True)

            else:

                self.accnt_timer = QTimer()
                self.accnt_timer.timeout.connect(self.login_error)
                self.accnt_timer.start(200)

        if "Offline" in results.keys():
            logger.warning("Offline")

            self.logout_btn.setVisible(True)
            self.username_label.mousePressEvent = self.retry_connection
            self.username_label.setText(
                '<a href="#"><span style=" text-decoration: underline; color:#0000ff;">Retry Connection</span></a>'
            )

        # region If the thread is not running, set btn as enabled, if thread is undefined, raise error and enable btn
        try:
            if not self.thread.isRunning():
                self.data_start.setEnabled(True)
        except:
            self.data_start.setEnabled(True)
            self.data_start.setText("Start collecting")
        # endregion

        self.menu_options.setEnabled(True)


    def login_error(self):

        if self.call_accnt_box:
            logger.warning("Login error")
            self.accnt_timer.stop()
            self.accnt_timer.deleteLater()

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

    # def call_update_score(self, online_score):
    #     self.update_score(self.score, online_score=online_score)

    def user_has_logged(self, user_info):
        print("User has logged #008")
        self.username = user_info['Username']
        self.password = user_info['Password']
        self.session = user_info['Session']

        self.send_btn.setText("Send data")
        self.username_label.setText(self.username)
        self.send_message_btn.setEnabled(True)
        self.send_message_btn.setText("Send message that will be redirected to your\nparents")

        try:
            self.thread.isRunning() # If data is being collected:

        except:
            self.send_btn.setEnabled(True)
            self.auto_send_checkbox.setEnabled(True)

        # Score Thread initialization
        try:
            self.score_thread = QThread() # Thread criado
            self.score_worker = QuickCheck(session=self.session) #
            self.score_worker.moveToThread(self.score_thread)

            # If logout signal is emmitted, delete the worker and quit then delete the thread too
            self.logout_signal.connect(self.score_worker.deleteLater)
            self.logout_signal.connect(self.score_thread.quit)
            self.score_thread.finished.connect(self.score_thread.deleteLater)

            self.score_worker.online_score.connect(lambda ol_score: self.update_score(self.score, online_score=ol_score))

            self.score_thread.start()
            logger.info("Score thread started")
            self.score_worker.single_check_online_score()

        except Exception as e:
            logger.error("Could not start score thread: %s" % e)
            QMessageBox.information(self, "Oops!", "Could not start score thread: %s" % e)

    def logout(self):
        self.logout_signal.emit()
        logger.info("User logged out")

        self.username = ''
        self.password = ''
        self.session = None

        self.username_label.setText("Not logged")
        self.send_btn.setText("Can't send data while offline")
        self.send_btn.setEnabled(False)
        self.auto_send_checkbox.setEnabled(False)

        with open('config.json', 'r') as f:
            output = json.loads(f.read())
            output['Password'] = ''
            output['User'] = ''

        with open('config.json', 'w') as f:
            json.dump(output, f)

        self.login_control({"Logged": False})

    def closeEvent(self, event):
        stop_time = datetime.datetime.now()
        runtime = (stop_time-start_time).total_seconds()
        logger.info('---------- CLOSED. Runtime: %ss ----------' % runtime)
        event.accept() #.ignore

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    app = QApplication(sys.argv)
    gui = Widget()
    sys.exit(app.exec_())
