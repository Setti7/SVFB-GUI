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
            file_data = {'csrfmiddlewaretoken': file_csrftoken}
            logger.info("Sending file")

            with open('Data\\training_data.npy', 'rb') as file:
                response = self.client.post(upload_url, files={'file': file}, data=file_data)

                logger.info("Response status code: %s" % response.status_code)

                if response.status_code == 200:
                    print("File should be sent.")
                    # os.remove('Data\\training_data.npy')
                    # logger.info("training_data.npy file removed")

                if self.send_return:
                    return response.status_code
                else:
                    self.status_code.emit(response.status_code)


        except Exception as e:
            print(e)
            print("Error SendData #228")
            self.status_code.emit(404)


def send_data(BASE_URL, username, password):

    login_url = BASE_URL + "/accounts/login/"
    upload_url = BASE_URL + "/ranking/"
    MAX_RETRIES = 2

    client = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
    client.mount('http://', adapter)  # I know that I should use https, but the server doesn't have it yet

    client.get(login_url)  # Goes to login page
    csrftoken = client.cookies['csrftoken']  # get csrf token
    login_data = {'username': username, 'password': password, 'csrfmiddlewaretoken': csrftoken, 'next': '/ranking/'}

    try:
        response = client.post(login_url, data=login_data)  # executes login

        if "Logout from {}".format(username) in str(response.content):  # this is to confirm the user logged in

            file_csrftoken = client.cookies['csrftoken']  # get ranking page crsf token
            file_data = {'csrfmiddlewaretoken': file_csrftoken}
            # headers = {"Referer": 'http://127.0.0.1:8000/ranking/'}

            # Header doesn't seems necessary
            with open('Data\\training_data.npy', 'rb') as file:
                response = client.post(upload_url, files={'file': file}, data=file_data) # headers=headers)
                print("File should be sent.")

                return response.status_code

        else:
            print("Not logged in.")
            return 404

    except Exception as e:
        print(e)  # No errors raised

#def auto_send(BASE_URL, username, password): #Starts a thread to send data, the closes the thread
#
# if __name__ == "__main__":
#     send_data('test1', 'senha123')
