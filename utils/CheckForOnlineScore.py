import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import json
import requests

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from utils.Globals import SCORE_URL


class QuickCheck(QObject):
    online_score = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, token, username, parent=None):
        QObject.__init__(self, parent=parent)
        self.token = token
        self.username = username

    @pyqtSlot()
    def single_check_online_score(self):

        try:
            logger.info("Checking online score")

            response = requests.post(SCORE_URL, headers={"Authorization": f"Token {self.token}"},
                                     data={'username': f'{self.username}'})

            output = json.loads(response.text)['score']

            self.online_score.emit(output)
            logger.info("Online score checked")
            self.finished.emit()

        except Exception as e:
            logger.error("Error with QuickCheck: %s" % e)
            self.finished.emit()
