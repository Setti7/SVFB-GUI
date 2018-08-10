from utils.Globals import logger
from PyQt5.QtCore import QObject, pyqtSignal
import os, json, requests
from uuid import uuid4
from utils.Globals import UPLOAD_DATA_URL


class SendData(QObject):
    # Código padrão de envio de POST requests
    # Tenta enviar ao servidor todos os arquivos que estão na pasta "Data/Training Data", para isso renomeia o arquivo
    # antes de envia-lo para "training_data.npy" (o servidor só aceita arquivos assim, como forma de precaução)
    status_code = pyqtSignal(int)

    def __init__(self, version, token, username, parent=None):
        QObject.__init__(self, parent=parent)
        self.version = version
        self.token = token
        self.username = username

    def send_data(self):

        # Caso não tenha arquivos na pasta
        if not os.listdir('Data\\Training Data'):
            logger.warning("Files does not exist, data already sent.")
            self.status_code.emit(-1)

        else:
            try:

                # Pra fazer POST precisa do csrftoken cookie antes (não é necessário um para cada envio):
                file_data = {'username': self.username, 'version': self.version}
                headers = {'Authorization': f'Token {self.token}'}

                logger.info("Sending file")

                if "training_data.npy" in os.listdir('Data\\Training Data'):
                    os.rename('Data\\Training Data\\training_data.npy', 'Data\\Training Data\\%s.npy' % uuid4())

                for file in os.listdir('Data\\Training Data'):

                    file_path = os.path.join('Data\\Training Data', file)
                    file_to_send = 'Data\\Training Data\\training_data.npy'

                    os.rename(file_path, file_to_send)

                    with open(file_to_send, 'rb') as f:
                        response = requests.post(UPLOAD_DATA_URL, files={'file': f}, data=file_data, headers=headers)

                    result = json.loads(response.text)
                    print("RESULT SEND DATA: ", result)

                    if result['success']:
                        logger.info("Data submitted successfully.")
                        response.status_code = 200

                    else:
                        logger.error("Error while sending data.")
                        response.status_code = 201

                    os.remove(file_to_send)
                    logger.info("Files deleted")

                    # Sinaliza ao main_thread qual a situação do envio dos dados, para que ele exiba aquelas notificações
                    # acima do botão "Send", informando o usuário se foi realmente enviado.
                    self.status_code.emit(response.status_code)

            except Exception as e:
                logger.error("Error while sending data: %s" % e)
                self.status_code.emit(-2)
