import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

from uuid import uuid4
import numpy as np
import cv2, datetime
from PyQt5.QtCore import QObject, pyqtSignal
from SVFBFuncs.getkeys import key_check
from SVFBFuncs import grabscreen


def fishing_region(img, region_template_gray, w, h):
    # Função usada para encontrar a área de pesca nos frames. Adaptado do tutorial no site oficial do Opencv
    # img: imagem fonte
    # region_template_gray: template em preto e branco
    # w e h: width e height do template

    res = cv2.matchTemplate(img, region_template_gray, cv2.TM_CCOEFF_NORMED)

    threshold = 0.65

    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        # Caso seja encontrado o template matching, será retornado apenas um valor, que é o primeiro ponto aonde houve
        # o match. Seria melhor mudar isso para retornar o valor daonde teve o melhor match.
        x1, y1 = pt[0], pt[1]
        x2, y2 = pt[0] + w, pt[1] + h


        # TODO: Fix this constants so the image can be resized to 0.3*size
        coords_list = [y1 - 10, y2 + 10, x1 - 25, x2 + 25] # these number are added to give a little margin for the TM
        green_bar_region = img[y1: y2, x1 + 55: x2 - 35]

        # Antes de retornar o frame, faz um resize dele pra um tamanho menor, a fim de não ocupar muito espaço em disco
        # Como uma convnet precisa que todas as imagens tenha o mesmo tamanho, talvez seja melhor estabelecer um tamanho
        # fixo aqui, e não um razão de diminuição, como está sendo feito.
        green_bar_region = cv2.resize(green_bar_region, None, fx=0.3, fy=0.3) # TODO: optimize this resizing

        return {"Detected": True, "Region": green_bar_region, "Coords": coords_list}


    # Só roda caso não seja achado a região
    return {"Detected": False}


class SaveData(QObject):
    finished = pyqtSignal()
    send_data = pyqtSignal()

    def __init__(self, key, res, zoom, parent=None):
        QObject.__init__(self, parent=parent)

        if res == "Auto":
            self.region = False

        else:
            res_x, res_y = [int(x_or_y) for x_or_y in res.split('x')]
            self.region = (0, 40, res_x, res_y + 40)

        self.zoom = zoom
        self.key = key

        self.run = True

    def main(self):

        # Unique file name
        file_name = 'Data\\Training Data\\%s.npy' % uuid4()

        logger.info("Training data file created")
        training_data = np.empty(shape=[0, 2])

        # Loading template according to zoom level:
        logger.info("Loading template image")
        fishing_region_file = 'media\\Images\\fr {}.png'.format(self.zoom)
        region_template = cv2.imread(fishing_region_file)
        # region_template = cv2.resize(region_template, None, fx=0.3, fy=0.3) # TODO: using smaller img for less space used
        region_template = cv2.cvtColor(region_template, cv2.COLOR_BGR2GRAY)
        wr, hr = region_template.shape[::-1] # 121, 474

        # Variáveis de controle:
        # was_fishing: sinaliza se o frame anterior foi ou não um frame da sessão de pescaria. Caso o mini-game seja
        # detectado, isso é setado para True no final do loop. Assim, no frame seguinte, caso não tenha sido detectado a
        # região e was_fishing for True, isso signifca que a pescaria acabou, e deve ser feito o processo de finalização
        # da captura de dados.
        # coords: coordenadas da região reduzida encontrada do mini-game.
        was_fishing = False
        coords = None

        logger.info("Data started")

        while self.run:

            #res_x, res_y = self.res
            screen = grabscreen.grab_screen(region=self.region) # Return gray screen

            # screen = cv2.resize(screen, None, fx=0.3, fy=0.3) # TODO: using smaller img for less space used

            # Finds the thin area the fish stays at
            if coords:
                # If there was found coords, cut the screen size to look again for the template, so it uses less resources
                region = fishing_region(screen[coords[0]:coords[1], coords[2]:coords[3]], region_template, wr, hr) #[y1, y2, x1 + 55, x2 - 35]

            else:
                region = fishing_region(screen, region_template, wr, hr)


            if region["Detected"]:
                # Se a área for detectada, salvar na np.array o frame e a o key-press do jogador.

                window = region["Region"]

                key_pressed = key_check(self.key) # return 1 or 0

                data = [window, key_pressed] # or data = np.array([key_pressed, window], dtype=object)

                training_data = np.vstack((training_data, data))
                method = 'np.vstack'

                was_fishing = True

                # For the first frame of the detected region, get its coordinates to reduce the area to look for it again
                if not coords:
                    coords = region["Coords"]
                    logger.info("Coordinates found: %s" % coords)
                    initial_time = datetime.datetime.now()

            # If area not detected this frame, but was on the last one, this means fishing is over.
            if not region["Detected"] and was_fishing:
                logger.info("Fishing finished")
                final_time = datetime.datetime.now()
                was_fishing = False

                new_frames = np.float64(len(training_data))

                print("Frames analysed: %s" % new_frames)

                if new_frames >= 75:
                    # Apenas salva caso houver mais de 75 frames
                    print("Saving...")
                    np.save(file_name, training_data)

                    # Sinaliza ao main_thread que deve enviar os dados coletados
                    self.send_data.emit()

                else:
                    print("Not saving!")
                    logger.debug("Data too small")

                # Necessary to reset the region coordinates after every fishing session.
                training_data = np.empty(shape=[0, 2])
                file_name = 'Data\\Training Data\\%s.npy' % uuid4()
                coords = None

                # Measurements (debug):
                time_delta = (final_time - initial_time).total_seconds()
                median_fps = new_frames/time_delta
                print("Median FPS: {}".format(median_fps))
                print("ΔTime: {}".format(time_delta))

                with open("Data\\log.txt", 'a') as f:
                    f.write("Method: {}\nMedian FPS: {}\ndTime: {}s\nFrames: {}\n\n".format(
                        method,
                        round(median_fps, 2),
                        time_delta, new_frames))

        # Caso o usuário clique em "Stop" na GUI
        self.finished.emit()

    def stop(self):
        self.run = False