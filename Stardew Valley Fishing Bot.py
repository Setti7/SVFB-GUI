import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import json, datetime, random
import sys, numpy as np, os, webbrowser, requests
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QMessageBox, QDialog, QMenuBar, QAction
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer, Qt
from PyQt5 import QtGui, QtCore
from PyQt5.uic import loadUi
from utils.WelcomeDialog import WelcomeDialog
from utils.SaveData import SaveData
from utils.AccountManager import AccountManager
from utils.CheckForOnlineScore import QuickCheck
from utils.LoginWorker import LoginWorker
from utils.SendFiles import SendData
from utils.Loading import Loading
from utils.CheckForUpdates import CheckForUpdates
from utils.ChangeKey import ChangeKey
from utils.Globals import DEV, VERSION, RELEASE_DATE, RANKING_URL, BUG_REPORT_URL, HOME_PAGE_URL

import traceback, sys

# https://stackoverflow.com/questions/44447674/traceback-missing-when-exception-encountered-in-pyqt5-code-in-eclipsepydev
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
    sys.excepthook = excepthook


class Widget(QMainWindow):
    logger.info("---------- STARTED ----------")
    stop_signal = pyqtSignal() # sinaliza que o usuário clicou em "Stop Data Colleting"
    logout_signal = pyqtSignal()

    date = datetime.datetime.strptime(RELEASE_DATE, '%Y-%m-%d')
    version = VERSION

    # Check if all files/folders are present.
    if not os.path.exists("Data"):
        os.mkdir("Data")

    if not os.path.exists("Data\\Training Data"):
        os.mkdir("Data\\Training Data")

    try:
        with open("config.json", "r") as f:
            logger.info('Loading config file')
            output = json.loads(f.read())
            used_key = output["Used key"]
            username = output['User']
            ignore_login = output['Ignore Login Popup']
            first_time_running =  output['First Time Running']
            token = output['Token']

    except Exception as e:
        logger.error(e)

        output = {"Used key": "C",
                  "User": "",
                  "Ignore Login Popup": False,
                  "First Time Running": True,
                  "Token": ""
        }

        used_key = output["Used key"]
        username = output['User']
        ignore_login = output['Ignore Login Popup']
        first_time_running = output['First Time Running']
        token = output['Token']

        with open("config.json", 'w') as f:
            json.dump(output, f, indent=2)

        logger.info("Fixed config file")


    logger.info('Config file loaded')

    def __init__(self):
        super().__init__()

        self.initUI()

        # Starting threads for startup verification
        self.loading_dialog = Loading()

        if DEV:
            wait_time = 100
        else:
            wait_time = random.randint(3550, 4500)

        # Defining control variables:
        self.auth_done = False
        self.update_check_done = False
        self.call_update_box = False
        self.call_accnt_box = False
        self.update_available = False
        self.wait_counter = 0
        self.online = False
        self.bot_btn_clicks = 0

        # Startup processes:
        self.startup_authorize_user()
        self.startup_update_check()

        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.loading)
        self.loading_timer.start(wait_time)


        # Icons:
        self.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))
        self.dog_getting_up = QtGui.QMovie('media\\animations\\Dog Getting Up4.gif')
        self.dog_running = QtGui.QMovie('media\\animations\\Dog Running4.gif')
        self.dog_idle = QtGui.QMovie('media\\animations\\Dog Idle2.gif')
        self.dog_sitting_down = QtGui.QMovie("media\\animations\\Dog Sitting Down4.gif")

        self.icons_label.setMovie(self.dog_idle)
        self.icons_label_2.setMovie(self.dog_idle)
        self.dog_idle.start()


        # Setting default labels and texts:
        self.v_label.setText("v{}".format(self.version))
        self.v_label_2.setText("v{}".format(self.version))

        # Defining button/checkbox actions
        self.data_start.clicked.connect(self.data_start_action)
        self.data_stop.clicked.connect(self.data_stop_action)
        self.send_btn.clicked.connect(self.send_data)
        self.bot_btn.clicked.connect(self.bot_controller)

    def initUI(self):
        logger.info("Initializing UI")

        loadUi('designs\\MainWindow.ui', self)

        # Main Window
        self.setFixedSize(333, 493)

        # Toolbar
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        # Bug Report Tab
        self.send_message_btn.clicked.connect(self.send_message)

        # Menu
        self.logout_btn = self.menu.addAction('Logout')
        self.logout_btn.triggered.connect(self.logout)
        self.logout_btn.setVisible(False)

        self.login_btn = self.menu.addAction('Login')
        self.login_btn.triggered.connect(self.runtime_login)
        self.login_btn.setVisible(False)

        visit_ranking = self.menu.addAction('Ranking')
        visit_ranking.triggered.connect(lambda: webbrowser.open(RANKING_URL))

        website = self.menu.addAction('GitHub')
        website.triggered.connect(lambda: webbrowser.open("https://github.com/Setti7/SVFB-GUI"))

        self.config = self.menu.addAction('Fast Config')
        self.config.triggered.connect(self.fast_config)

        logger.info("UI Initialized")

    # Loading screen controller
    def loading(self):

        if self.auth_done and self.update_check_done:
            logger.info("Loading main aplication finished")
            self.loading_timer.stop()
            self.loading_timer.deleteLater()

            self.call_accnt_box = True
            self.call_update_box = True
            self.loading_dialog.close()
            self.show()


    def fast_config(self):

        config_dialog = ChangeKey(self.used_key)
        if config_dialog.exec_():
            self.used_key = config_dialog.new_key

    # Send message
    def send_message(self):

        msg = self.message_text.toPlainText()

        if self.update_available:

            bug_box = QMessageBox()
            bug_box.setIcon(QMessageBox.Warning)
            bug_box.setText("<strong>You can't send bug reports while using an outdated version!</strong>")
            bug_box.setInformativeText(
                """Please click <i>Ok</i> to download the newer one. Maybe your bug is already fixed."""
            )
            bug_box.setWindowTitle("Please update before sending bug reports")
            bug_box.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))

            bug_box.setEscapeButton(QMessageBox.Close)
            bug_box.addButton(QMessageBox.Close)

            ok = bug_box.addButton(QMessageBox.Ok)
            ok.clicked.connect(lambda: webbrowser.open("https://github.com/Setti7/SVFB-GUI/releases"))
            bug_box.exec_()

        elif len(msg) > 1000:

            self.message_status_label.clear()
            self.message_status_label.setStyleSheet("color: #dc3545;")

            self.timer_msg0 = QTimer()
            self.timer_msg0.timeout.connect(lambda: self.message_status_label.setText("Your message is to big!\nThe maximum is 1000 chars."))
            self.timer_msg0.timeout.connect(self.timer_msg0.stop)
            self.timer_msg0.timeout.connect(self.timer_msg0.deleteLater)
            self.timer_msg0.start(200)

        else:

            self.message_text.clear()

            try:

                data = {
                    'message': msg,
                    'user': self.username,
                    'version': self.version,
                }

                headers = {'Authorization': f'Token {self.token}'}

                response = requests.post(BUG_REPORT_URL, data=data, headers=headers)

                result = json.loads(response.text)


                if result['success']:

                    self.message_status_label.setText("Message successfully sent!")
                    self.message_status_label.setStyleSheet("color: #28a745;")

                else:
                    logger.error(f"Error while sending message: {result['error']}")
                    self.message_status_label.setText("There was an error while sending!")
                    self.message_status_label.setStyleSheet("color: #dc3545;")

                self.timer_msg = QTimer()
                self.timer_msg.timeout.connect(self.message_status_label.clear)
                self.timer_msg.timeout.connect(self.timer_msg.stop)
                self.timer_msg.timeout.connect(self.timer_msg.deleteLater)
                self.timer_msg.start(5000)

            except Exception as e:
                print(e)
                logger.error(e)


    # Startup Processes and connection functions:
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
        self.login_worker = LoginWorker(self.username, self.token)
        self.login_worker.moveToThread(self.login_thread)

        self.login_worker.result.connect(self.login_control)

        self.login_worker.result.connect(self.login_worker.deleteLater)
        self.login_worker.result.connect(self.login_thread.quit)

        self.login_thread.finished.connect(self.login_thread.deleteLater)
        self.login_thread.finished.connect(self.login_thread.wait)

        self.login_thread.started.connect(self.login_worker.do_work)
        self.login_thread.start()

    # If the user clicks the retry connection button too much:
    def wait_motherfucker(self, *args):
        self.wait_counter += 1

        if self.wait_counter >= 5:
            self.wait_counter = 0
            wait = QMessageBox()
            wait.setIcon(QMessageBox.Warning)
            wait.setText("<strong>I AM TRYING TO CONNECT ALREADY. STOP MASHING THAT DAMN BUTTON")
            wait.setInformativeText(
                """I'm doing my best ok? Just have a little patience please."""
            )
            wait.setWindowTitle("FOR GOD'S SAKE, WAIT!")
            wait.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))

            close = wait.addButton(QMessageBox.Close)
            close.setText("Ok... I will stop")
            wait.setEscapeButton(QMessageBox.Close)
            wait.exec_()

    def retry_connection(self, *args):
        # *args are necessary so it can be called from the mousePressEvent

        # Label
        self.username_label.setText("Connecting")
        self.username_label.mousePressEvent = lambda x: self.wait_motherfucker()

        self.username_label_2.setText("Connecting")
        self.username_label_2.mousePressEvent = lambda x: self.wait_motherfucker()

        # Thread:
        self.login_thread = QThread()
        self.login_worker = LoginWorker(self.username, self.token)
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


    def update_score(self, **kwargs):

        # if 'offline' in kwargs.keys():
        #     self.score_label.setText("")
        #     # self.score_label.setText("Score: Offline")
        #
        # if 'waiting' in kwargs.keys():
        #     self.score_label.setText("")
        #     # self.score_label.setText("Score: Waiting Connection")
        #
        # if 'not_logged' in kwargs.keys():
        #     self.score_label.setText("")
        #     # self.score_label.setText("Score: Not Logged")

        if 'online_score' in kwargs.keys():
            self.score_label.setVisible(True)
            self.line.setVisible(True)
            self.score_label.setText("Online Score: {}".format(kwargs['online_score']))

        else:
            self.score_label.setVisible(False)
            self.line.setVisible(False)

    def dog_go_idle(self):
        self.icons_label.setMovie(self.dog_idle)
        self.dog_idle.start()
        self.dog_timer2.stop()

    def dog_run(self):
        self.icons_label.setMovie(self.dog_running)
        self.dog_running.start()
        self.dog_timer.stop()


    # Notification of new version:
    def call_not_critical_update_message_box(self, *args, **kwargs):
        current_version = kwargs['current_version']
        new_version = kwargs['new_version']
        changes = kwargs['changes']

        updateBox = QMessageBox()
        updateBox.setIcon(QMessageBox.Information)
        updateBox.setText(
            """This new version has no critical changes, so you can choose to download it or not. Check the changelog below!"""
        )
        updateBox.setWindowTitle("New Update Available")
        updateBox.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))

        text = """Version available: {1}\n\n{2}""".format(current_version, new_version,
                                                          changes)
        updateBox.setDetailedText(text)

        updateBox.setEscapeButton(QMessageBox.Close)
        updateBox.addButton(QMessageBox.Close)

        ok = updateBox.addButton(QMessageBox.Ok)
        ok.setText('Update')
        ok.clicked.connect(lambda: webbrowser.open(HOME_PAGE_URL))
        updateBox.exec_()

    def update_message_box(self, update_info):

        if self.call_update_box:
            self.update_timer.stop()
            self.update_timer.deleteLater()

            update = update_info['Update']
            logger.info("Update available: %s" % update)

        else:
            update = False

        if update:
            self.update_available = True

            current_version = update_info['Current Version']
            new_version = update_info['New Version']
            changes = update_info['Changes']
            critical = update_info['Critical']
            logger.info("Update critical: %s" % critical)

            if not critical:

                self.v_label.setText("v{} (<a href='#'>update to v{}</a>)".format(self.version, new_version))
                self.v_label.mousePressEvent = lambda args: self.call_not_critical_update_message_box(
                    current_version=current_version,
                    new_version=new_version,
                    changes=changes,
                )

                self.v_label_2.setText("v{} (<a href='#'>update to v{}</a>)".format(self.version, new_version))
                self.v_label_2.mousePressEvent = lambda args: self.call_not_critical_update_message_box(
                    current_version=current_version,
                    new_version=new_version,
                    changes=changes,
                )

            if critical:
                updateBox = QMessageBox()
                updateBox.setIcon(QMessageBox.Warning)
                updateBox.setText("<strong>Your version is super outdated and is not useful anymore!</strong>")
                updateBox.setInformativeText(
                    """Please click <i>Ok</i> to download the newer one. You can also see the changelog details below! <small>(The critical change is highlighted)</small>"""
                )
                updateBox.setWindowTitle("Unsupported Version")
                updateBox.setWindowIcon(QtGui.QIcon('media\\logo\\logo.ico'))

                text = """Version available: {1}\n\n{2}""".format(current_version, new_version,
                                                                  changes)
                updateBox.setDetailedText(text)

                updateBox.setEscapeButton(QMessageBox.Close)
                updateBox.addButton(QMessageBox.Close)
                self.v_label.setText("v{} (v{} REQUIRED)".format(self.version, new_version))
                self.v_label_2.setText("v{} (v{} REQUIRED)".format(self.version, new_version))

                ok = updateBox.addButton(QMessageBox.Ok)
                ok.clicked.connect(lambda: webbrowser.open(HOME_PAGE_URL))
                updateBox.exec_()
                self.close()


    # Data processes:
    def data_start_action(self):
        # Flag to indicate data collection is running
        self.data_running = True

        self.data_start.setEnabled(False)
        self.data_stop.setEnabled(True)
        self.send_btn.setEnabled(False)
        self.logout_btn.setEnabled(False)
        self.login_btn.setEnabled(False)

        # Indicating user about the key being used:
        self.send_status_label.setText(f'Using "{self.used_key}" key. Change it in "Fast Config".')
        self.send_status_label.setStyleSheet("color: #007bff;")
        QTimer.singleShot(3000, self.send_status_label.clear)

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

        logger.info(f"Using: {self.used_key}")

        if self.used_key.upper() == "LEFT-CLICK":
            self.worker = SaveData(0x01)
        else:
            self.worker = SaveData(self.used_key)

        self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.main)
        self.thread.finished.connect(self.worker.stop)

        self.worker.send_data.connect(self.send_data)

        self.thread.start()

    def data_stop_action(self):
        # Flag to indicate data collection is not running
        self.data_running = False

        if hasattr(self, 'bot_running'):
            if not self.bot_running:
                self.logout_btn.setEnabled(True)
                self.login_btn.setEnabled(True)
        else:
            self.logout_btn.setEnabled(True)
            self.login_btn.setEnabled(True)

        self.data_start.setEnabled(True)
        self.data_stop.setEnabled(False)

        if self.online:
            self.send_btn.setEnabled(True)

        logger.info("Data stopped")
        self.stop_signal.emit()  # emit the finished signal on stop

        # Icon
        self.dog_timer.deleteLater()
        self.icons_label.setMovie(self.dog_sitting_down)
        self.dog_sitting_down.start()

        self.dog_timer2 = QTimer()
        self.dog_timer2.timeout.connect(self.dog_go_idle)
        self.dog_timer2.start(370)

    def send_data(self):
        """
        Creates thread to send data and don't stop the execution of the program while it is uploading.
        Every time the button is clicked, it is created a new thread, that is deleted after the upload.
        """

        self.send_btn.setEnabled(False)
        if self.online:
            try:
                logger.info("Starting send data thread")
                self.send_data_thread = QThread()  # Thread criado
                self.send_data_worker = SendData(version=self.version, token=self.token, username=self.username)
                self.send_data_worker.moveToThread(self.send_data_thread)

                self.send_data_worker.status_code.connect(self.auto_send_response_code_controller)
                self.send_data_worker.status_code.connect(self.score_worker.single_check_online_score)

                self.send_data_worker.status_code.connect(self.send_data_worker.deleteLater) # Finished then deletes thread and worker
                self.send_data_worker.status_code.connect(self.send_data_thread.quit)
                self.send_data_thread.finished.connect(self.send_data_thread.deleteLater)

                self.send_data_thread.started.connect(self.send_data_worker.send_data)

                self.send_data_thread.start()
                logger.info('Send data thread started')


            except Exception as e:
                logger.error("Could not start thread to send data: %s" % e)
                QMessageBox.information(self, "Oops!", "Could not start thread to send data: %s" % e)

        else:
            # Raises the little offline message
            self.auto_send_response_code_controller(-2)

    def auto_send_response_code_controller(self, code):
        if code == 200:
            self.send_status_label.setText("Success! Thank you for helping!")
            self.send_status_label.setStyleSheet("color: #28a745;")
            self.send_btn.setText("Send Data")

        elif code == -1:
            self.send_status_label.setText('Everything was already sent!')
            self.send_status_label.setStyleSheet("color: #dc3545;")
            self.send_btn.setText("Send Data")

        elif code == -2:
            self.send_status_label.setText('Could not connect to server. Session is saved.')
            self.send_status_label.setStyleSheet("color: #ffaf00;")
            self.update_score(waiting=True)
            self.send_btn.setText("Send Data (upload pending)")

        else:
            self.send_status_label.setText("Verify your connection")
            self.send_status_label.setStyleSheet("color: #dc3545;")
            self.update_score(offline=True)

        QTimer.singleShot(5000, self.send_status_label.clear)

        if hasattr(self, 'data_running'):
            if not self.data_running:
                self.send_btn.setEnabled(True)
        else:
            self.send_btn.setEnabled(True)


    # Bot Functions
    def bot_controller(self):
        self.bot_btn_clicks += 1

        if self.bot_btn_clicks == 1:

            # Configuring control variables
            self.bot_running = True

            # Changing labels
            self.bot_btn.setText("Stop")

            # Disabling buttons that could cause problems
            self.logout_btn.setEnabled(False)
            self.login_btn.setEnabled(False)
            self.change_dataset_btn.setEnabled(False)


        else:

            # Configuring control variables
            self.bot_btn_clicks = 0
            self.bot_running = False

            # Changing labels
            self.bot_btn.setText("Start")

            # Enabling buttons
            self.change_dataset_btn.setEnabled(True)

            if hasattr(self, 'data_running'):
                if not self.data_running:
                    self.logout_btn.setEnabled(True)
                    self.login_btn.setEnabled(True)
            else:
                self.logout_btn.setEnabled(True)
                self.login_btn.setEnabled(True)


    # Account functions:
    def login_control(self, results):
        self.auth_done = True

        if "Logged" in results.keys():
            if results['Logged']:
                logger.info("User successfully logged in")

                self.user_has_logged({"Username": results['Username'], "Token": results['Token'], "Session": results['Session']})

            else:
                # If user has failed to login, keep calling the function until loading stops, so it does not pop up
                # with the loading screen still on.
                self.accnt_timer = QTimer()
                self.accnt_timer.timeout.connect(self.login_error)
                self.accnt_timer.start(200)

        if "Offline" in results.keys():
            self.online = False
            self.update_score(offline=True)
            logger.warning("Offline")

            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(False)

            self.username_label.mousePressEvent = self.retry_connection
            self.username_label.setText(
                '<a href="#"><span style=" text-decoration: underline; color:#0000ff;">Retry Connection</span></a>'
            )

            self.username_label_2.mousePressEvent = self.retry_connection
            self.username_label_2.setText(
                '<a href="#"><span style=" text-decoration: underline; color:#0000ff;">Retry Connection</span></a>'
            )
            self.wait_counter = 0

            if self.first_time_running:
                welcome_dialog = WelcomeDialog()
                if welcome_dialog.exec_():
                    self.first_time_running = False

    def login_error(self):
        # when the loading has finished, call the accnt manager pop up if the login failed
        if self.call_accnt_box:
            logger.info("Opening account manager")
            self.accnt_timer.stop()
            self.accnt_timer.deleteLater()

            self.login_btn.setVisible(True)
            self.logout_btn.setVisible(False)

            if not self.ignore_login:
                self.accnt_manager = AccountManager()
                self.accnt_manager.user_logged.connect(self.user_has_logged)
                self.accnt_manager.rejected.connect(self.login_rejected)

                self.accnt_manager.exec_()

            else:
                self.username_label.setText("Not logged")
                self.username_label_2.setText("Not logged")
                self.username_label.mousePressEvent = None
                self.username_label_2.mousePressEvent = None

                self.update_score(not_logged=True)

            if self.first_time_running:
                welcome_dialog = WelcomeDialog()
                if welcome_dialog.exec_():
                    self.first_time_running = False



    def login_rejected(self):

        self.username_label.setText("Not logged")
        self.username_label_2.setText("Not logged")
        self.username_label.mousePressEvent = None
        self.username_label_2.mousePressEvent = None

        self.logout_btn.setVisible(False)
        self.login_btn.setVisible(True)
        self.update_score(not_logged=True)

        with open ("config.json", 'r') as f:
            output = json.loads(f.read())
            output["Ignore Login Popup"] = True

        with open("config.json", "w") as f:
            json.dump(output, f, indent=2)

    def user_has_logged(self, user_info):
        # When the user has logged in, create a score thread with its user/password to get the online score.
        # Check the online score as soon as possible.
        logger.info("User logged")
        self.username = user_info['Username']
        self.token = user_info['Token']

        # Checking if there is data to be sent
        if os.listdir('Data\\Training Data'):
            self.send_btn.setText("Send data (upload pending)")
        else:
            self.send_btn.setText("Send data")

        self.online = True
        self.username_label.setText(self.username)
        self.username_label_2.setText(self.username)

        self.send_message_btn.setEnabled(True)
        self.send_message_btn.setText("Send cool message")

        self.login_btn.setVisible(False)
        self.logout_btn.setVisible(True)

        # Fixes bug where offline user collecting data could retry connecting to the server, re-enabling the buttons.
        if hasattr(self, 'data_running'):
            if not self.data_running:
                self.send_btn.setEnabled(True)
                self.data_start.setEnabled(True)
        else:
            self.send_btn.setEnabled(True)
            self.data_start.setEnabled(True)


        # Score Thread initialization
        try:
            self.score_thread = QThread() # Thread criado
            self.score_worker = QuickCheck(token=self.token, username=self.username) #
            self.score_worker.moveToThread(self.score_thread)

            # If logout signal is emmitted, delete the worker and quit then delete the thread too
            self.logout_signal.connect(self.score_worker.deleteLater)
            self.logout_signal.connect(self.score_thread.quit)
            self.score_thread.finished.connect(self.score_thread.deleteLater)

            self.score_worker.online_score.connect(lambda ol_score: self.update_score(online_score=ol_score))

            self.score_thread.start()
            logger.info("Score thread started")
            self.score_worker.single_check_online_score()

        except Exception as e:
            logger.error("Could not start score thread: %s" % e)
            QMessageBox.information(self, "Oops!", "Could not start score thread: %s" % e)

    # When user tries to login with the login button at the menu
    def runtime_login(self):
        self.ignore_login = False
        self.login_control({'Logged': False})

    def logout(self):
        # When user logs out, emit a signal that kills the score_thread and score_worker, because the session will change
        # if the user logs in with another account.
        self.logout_signal.emit()
        logger.info("User logged out")

        self.username = None
        self.token = None

        self.username_label.setText("Not logged")
        self.username_label_2.setText("Not logged")

        self.send_btn.setText("Can't send data while offline")
        self.send_btn.setEnabled(False)
        self.send_message_btn.setEnabled(False)


        with open('config.json', 'r') as f:
            output = json.loads(f.read())
            output['User'] = self.username
            output['Token'] = self.token

        with open('config.json', 'w') as f:
            json.dump(output, f, indent=2)

        self.update_score(not_logged=True)
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
