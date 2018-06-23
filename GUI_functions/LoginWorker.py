import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import requests, json
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

BASE_URL = "http://127.0.0.1"

class LoginWorker(QObject):
    result = pyqtSignal(dict)

    def __init__(self, username, password, parent=None):
        QObject.__init__(self, parent=parent)
        self.password = password
        self.username = username

    @pyqtSlot()
    def do_work(self):

        max_retries = 1  #TODO: change all max_retries to 1
        login_url = BASE_URL + "/api/login"

        try:
            logger.info("Logging user")
            client = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
            client.mount('http://', adapter)  # client.mount('https://', adapter)

            client.get(login_url)
            csrftoken = client.cookies['csrftoken']
            login_data = {'username': self.username, 'password': self.password, 'csrfmiddlewaretoken': csrftoken}

            response = client.post(login_url, data=login_data)
            result = json.loads(response.content)

            print(result)
            if result['success']:
                self.result.emit({"Logged": True, "Username": self.username, "Password": self.password, "Session": client})

            else:
                self.result.emit({"Logged": False})

        except:
            self.result.emit({"Offline": True})
