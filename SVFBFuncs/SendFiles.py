import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

from PyQt5.QtCore import QObject, pyqtSignal
import os, json
from SVFBFuncs.Globals import BASE_URL


class SendData(QObject):
    status_code = pyqtSignal(int)

    def __init__(self, session, send_return=False, parent=None):
        QObject.__init__(self, parent=parent)
        self.client = session
        self.send_return = send_return

    def send_data(self):
        upload_url = BASE_URL + "/api/data-upload"

        # if file was already sent
        if not os.path.isfile('Data\\training_data.npy'):
            logger.warning("File does not exist, data already sent.")
            self.status_code.emit(-1)

        else:
            try:
                self.client.get(upload_url)
                file_csrftoken = self.client.cookies['csrftoken']  # get ranking page crsf token
                file_data = {'csrfmiddlewaretoken': file_csrftoken}
                logger.info("Sending file")

                with open('Data\\training_data.npy', 'rb') as file:
                    response = self.client.post(upload_url, files={'file': file}, data=file_data)

                result = json.loads(response.text)
                print("RESULT SEND DATA: ", result)

                if result['success']:
                    logger.info("Data submitted successfully. Deleting files")
                    os.remove('Data\\training_data.npy')
                    os.remove('Data\\frames.npy')
                    logger.info("Files deleted")
                    response.status_code = 200

                else:
                    logger.error("Error while sending data. Files NOT deleted. Response code: %s" % response.status_code)
                    response.status_code = 201

                if self.send_return:
                    return response.status_code
                else:
                    self.status_code.emit(response.status_code)

            except Exception as e:
                logger.error("Error while sending data: %s" % e)
                self.status_code.emit(-2)
