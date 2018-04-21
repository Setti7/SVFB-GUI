import json, datetime
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
            last_info = output["Version Control"][-1]

            version = last_info['Version']
            changes = last_info['Changes']
            date = datetime.datetime.strptime(last_info['Date'], '%Y-%m-%d')

            if Widget.date < date:
                self.update_text.emit([Widget.version, version, changes])
                self.finished.emit()

        except URLError:
            print("Update timeout")

        finally:
            self.finished.emit()


class ChangeKey(QDialog):

    key_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('logo\\logo.png'))

        self.save_btn.clicked.connect(self.save)
        self.close_btn.clicked.connect(self.close)

    def initUI(self):
        loadUi('key_used_dialog.ui', self)
        self.show()

    def save(self):
        with open("config.txt", "r") as f:
            output = json.loads(f.read())
            new_key = str(self.change_key.text()).upper()
            output['Used key'] = new_key

        with open("config.txt", "w") as f:
            json.dump(output, f)

        self.key_changed.emit()
        self.close()


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

        self.update_check()

        # Try finding score file
        self.score_file = "Data\\frames.npy"
        if os.path.exists(self.score_file):
            score = sum(list(np.load(self.score_file)))
            self.label.setText("Score: {}".format(str(score)))

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
        updateBox = QMessageBox()
        updateBox.setIcon(QMessageBox.Information)
        updateBox.setText("There is a new version available!")
        updateBox.setInformativeText(
            """Please click "Ok" to be redirected to the download page. You can also see the changelog details below!"""
        )
        updateBox.setWindowTitle("Update required")
        updateBox.setWindowIcon(QtGui.QIcon('logo\\logo.png'))

        current_version, new_version, changes = update_info

        text = """Your version: {0}\t|\tNew version: {1}\n\nv{1} changes:\n{2}""".format(current_version, new_version,
                                                                                         changes)
        updateBox.setDetailedText(text)

        updateBox.setEscapeButton(QMessageBox.Close)
        updateBox.addButton(QMessageBox.Close)
        self.v_label.setText("v{} (v{} available)".format(self.version, new_version))

        ok = updateBox.addButton(QMessageBox.Ok)
        ok.clicked.connect(self.go_to_update_page)
        updateBox.exec_()

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
            self.label.setText("Score: {}".format(str(score)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Widget()
    sys.exit(app.exec_())
