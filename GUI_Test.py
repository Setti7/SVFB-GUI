import json, datetime
import multiprocessing as mp
from urllib.request import urlopen
from urllib.error import URLError
import sys, numpy as np, os, webbrowser
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5 import QtGui
from PyQt5.uic import loadUi
import save_data
# import simulating_save_data

class Worker(QObject):

    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    def do_work(self):

        print('do_work')
        save_data.main()
        print("stopped_work")
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        save_data.run = False  # set the run condition to false on stop


class CheckForUpdates(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)


    def do_work(self):
        try:
            data = urlopen("http://127.0.0.1:8000/version-control").read()
            output = json.loads(data)
            last_info = output["Version Control"][-1]

            version = last_info['Version']
            changes = last_info['Changes']
            date = datetime.datetime.strptime(last_info['Date'], '%Y-%m-%d')
            if Widget.date < date:
                print("You should update!\nYour version: {}\nNew version: {}\nChanges:\n{}".format(Widget.version, version,
                                                                                                   changes))
        except URLError:
            print("Update timeout")

        finally:
            self.finished.emit()


class Widget(QWidget):
    stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread

    force_close = False

    version = '1.0'
    date = datetime.datetime.strptime("2018-04-19", '%Y-%m-%d')

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('logo\\logo.png'))
        self.v_label.setText("v{}".format(self.version))
        self.update_check()

        self.data_stop.setEnabled(False)

        # Try finding score file
        self.score_file = "Data\\frames.npy"
        if os.path.exists(self.score_file):
            score = sum(list(np.load(self.score_file)))
            self.label.setText("Score: {}".format(str(score)))

        self.data_start.clicked.connect(self.data_start_action)
        self.data_stop.clicked.connect(self.data_stop_action)
        self.send_btn.clicked.connect(self.go_to_website)

    def initUI(self):
        loadUi('GUI_design.ui', self)
        self.show()

    def go_to_website(self):
        webbrowser.open("http://127.0.0.1:8000/ranking")

    def update_check(self):
        self.check_thread = QThread()
        self.checker = CheckForUpdates()
        self.checker.moveToThread(self.check_thread)

        self.checker.finished.connect(self.check_thread.quit)  # connect the workers finished signal to stop thread
        self.checker.finished.connect(
            self.checker.deleteLater)  # connect the workers finished signal to clean up worker
        self.check_thread.finished.connect(
            self.check_thread.deleteLater)  # connect threads finished signal to clean up thread

        self.check_thread.started.connect(self.checker.do_work)

        self.check_thread.start()

    def data_start_action(self):
        self.data_start.setEnabled(False)
        self.data_stop.setEnabled(True)
        save_data.run = True

        # Thread: __init__
        self.thread = QThread()
        self.worker = Worker()
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
        self.stop_signal.emit()  # emit the finished signal on stop
        print('Data stopped')

        if os.path.exists(self.score_file):
            score = sum(list(np.load(self.score_file)))
            self.label.setText("Score: {}".format(str(score)))

    # When stop_btn is clicked this runs. Terminates the worker and the thread.
    # def stop_thread(self):
    #     self.stop_signal.emit()  # emit the finished signal on stop
    #     print("Stop signal emmitted.")
    #
    # def start_thread(self):
    #
    #     # Thread: __init__
    #     self.thread = QThread()
    #     self.worker = Worker()
    #     self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
    #     self.worker.moveToThread(self.thread)
    #
    #     self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
    #     self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
    #     self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread
    #
    #     self.thread.started.connect(self.worker.do_work)
    #     self.thread.finished.connect(self.worker.stop)
    #
    #     self.thread.start()
    #     print("Thread started.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Widget()
    sys.exit(app.exec_())
