import json
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

BASE_URL = "http://127.0.0.1"

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
            self.finished.emit()
            print("#004")


    def stop(self):
        self.continue_run = False


class QuickCheck(QObject):
    online_score = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, session, parent=None):
        QObject.__init__(self, parent=parent)
        self.client = session

    @pyqtSlot()
    def single_check_online_score(self):
        score_url = BASE_URL + '/score'

        try:

            response = self.client.get(score_url)
            output = json.loads(response.text)['score']
            self.online_score.emit(output)
            print("Online score: {} #050".format(output))
            self.finished.emit()

        except Exception as e:
            print(e)
            self.finished.emit()
            print("Error QuickCheck #018")