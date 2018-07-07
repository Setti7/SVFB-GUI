import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

from PyQt5.QtCore import QObject, pyqtSignal
import os, json
from SVFBFuncs.Globals import BASE_URL


class SendData(QObject):
    status_code = pyqtSignal(int)

    def __init__(self, session, parent=None):
        QObject.__init__(self, parent=parent)
        self.client = session


    def send_data(self):
        upload_url = BASE_URL + "/api/data-upload"

        # if file was already sent
        if not os.listdir('Data\\Training Data'):
            logger.warning("Files does not exist, data already sent.")
            self.status_code.emit(-1)

        elif self.client == None:
            logger.warning("Cannot upload files while offline.")
            self.status_code.emit(-2)


        else:
            try:
                self.client.get(upload_url)
                file_csrftoken = self.client.cookies['csrftoken']  # get ranking page crsf token
                file_data = {'csrfmiddlewaretoken': file_csrftoken}
                logger.info("Sending file")

                for file in os.listdir('Data\\Training Data'):
                    file_path = os.path.join('Data\\Training Data', file)
                    os.rename(file_path, 'Data\\Training Data\\training_data.npy')

                    file_path = 'Data\\Training Data\\training_data.npy'

                    with open(file_path, 'rb') as file:
                        response = self.client.post(upload_url, files={'file': file}, data=file_data)

                    result = json.loads(response.text)
                    print("RESULT SEND DATA: ", result)

                    if result['success']:
                        logger.info("Data submitted successfully.")
                        response.status_code = 200

                    else:
                        logger.error("Error while sending data.")
                        response.status_code = 201

                    os.remove(file_path)
                    logger.info("Files deleted")

                    self.status_code.emit(response.status_code)

            except Exception as e:
                logger.error("Error while sending data: %s" % e)
                print('ERROR $212')
                self.status_code.emit(-2)
