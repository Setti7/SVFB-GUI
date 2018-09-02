import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import requests, json
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from utils.Globals import VALIDATE_TOKEN_URL, HOME_PAGE_URL


class LoginWorker(QObject):
    result = pyqtSignal(dict)

    def __init__(self, username, token, parent=None):
        QObject.__init__(self, parent=parent)
        self.username = username
        self.token = token

    @pyqtSlot()
    def do_work(self):

        if self.username != None and self.token != None:
            try:
                logger.info("Validating user")

                response = requests.post(VALIDATE_TOKEN_URL,
                                         headers={"Authorization": f"Token {self.token}"},
                                         data={'username': f'{self.username}'})

                result = json.loads(response.content)

                if result['valid-token']:
                    self.result.emit({"Logged": True, "Username": self.username, "Token": self.token, "Session": None})

                else:
                    self.result.emit({"Logged": False})

            except:
                self.result.emit({"Offline": True})

        else:
            # Checking internet connection to server

            try:
                response = requests.get(HOME_PAGE_URL)

                if response.status_code == 200:
                    self.result.emit({"Logged": False})

            except requests.ConnectionError:
                self.result.emit({"Offline": False})

