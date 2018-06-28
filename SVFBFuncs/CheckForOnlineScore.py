import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import json
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from SVFBFuncs.Globals import BASE_URL


# class CheckForOnlineScore(QObject):
#     online_score = pyqtSignal(int)
#     finished = pyqtSignal()
#
#     def __init__(self, session, parent=None):
#         QObject.__init__(self, parent=parent)
#         self.client = session
#         self.continue_run = True
#
#     def timer_for_checker(self):
#
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.check_online_score)
#         self.timer.start(15000)
#
#     @pyqtSlot()
#     def check_online_score(self):
#         score_url = BASE_URL + '/home?score'
#
#         try:
#
#             if self.continue_run:
#                 response = self.client.get(score_url)
#                 output = json.loads(response.text)['score']
#                 self.online_score.emit(output)
#                 print("ONLINE SCORE: {}".format(output))
#
#                 self.timer_for_checker()
#             else:
#                 self.finished.emit()
#                 print("finish emitted")
#
#         except Exception as e:
#             print(e)
#             self.finished.emit()
#             print("#004")
#
#
#     def stop(self):
#         self.continue_run = False


class QuickCheck(QObject):
    online_score = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, session, parent=None):
        QObject.__init__(self, parent=parent)
        self.client = session

    @pyqtSlot()
    def single_check_online_score(self):
        score_url = BASE_URL + '/api/score'

        try:
            logger.info("Checking online score")
            response = self.client.get(score_url)
            output = json.loads(response.text)['score']
            self.online_score.emit(output)
            logger.info("Online score checked")
            self.finished.emit()

        except Exception as e:
            logger.error("Error with QuickCheck: %s" % e)
            self.finished.emit()