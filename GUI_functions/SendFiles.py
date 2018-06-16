import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

from PyQt5.QtCore import QObject, pyqtSignal
import requests, os

BASE_URL = "http://127.0.0.1"

class SendData(QObject):
    status_code = pyqtSignal(int)

    def __init__(self, session, send_return=False, parent=None):
        QObject.__init__(self, parent=parent)
        self.client = session
        self.send_return = send_return

    def send_data(self):
        upload_url = BASE_URL + "/ranking/"

        try:
            self.client.get(upload_url)
            file_csrftoken = self.client.cookies['csrftoken']  # get ranking page crsf token
            file_data = {'csrfmiddlewaretoken': file_csrftoken, 'PROGRAM': "ui mama mia"}
            logger.info("Sending file")

            with open('Data\\training_data.npy', 'rb') as file:
                response = self.client.post(upload_url, files={'file': file}, data=file_data)

            if response.status_code == 200:
                logger.info("Data submitted successfully. Deleting files")
                os.remove('Data\\training_data.npy')
                os.remove('Data\\frames.npy')
                logger.info("Files deleted")

            else:
                logger.error("Error while sending data. Response code: %s" % response.status_code)
                logger.info("Files NOT deleted")

            if self.send_return:
                return response.status_code
            else:
                self.status_code.emit(response.status_code)


        except Exception as e:
            logger.error(e)
            self.status_code.emit(404)
