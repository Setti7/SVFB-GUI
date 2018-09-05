import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import datetime
from uuid import uuid4

import cv2
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from utils import grabscreen
from utils.AfterProcessing import find_fish, find_green_rectangle, find_chest, verify_too_similar_frames
from utils.getkeys import key_check


def fishing_region_opencl(img_bgr, region_template_gray, w, h):
    e1 = cv2.getTickCount()
    imgGpu = cv2.UMat(img_bgr)  # GPU
    e2 = cv2.getTickCount()
    print((e2 - e1) / cv2.getTickFrequency())
    imgGpu = cv2.cvtColor(imgGpu, cv2.COLOR_BGRA2GRAY)  # GPU

    # region_template_grayGpu = cv2.UMat(region_template_gray)
    try:
        res = cv2.matchTemplate(imgGpu, region_template_gray, cv2.TM_CCOEFF_NORMED)

    except Exception as e:
        print(e)

    threshold = 0.65
    # img = imgGpu.get()
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if (max_val > threshold):
        x1, y1 = max_loc
        x2, y2 = x1 + w, y1 + h

        coords_list = [y1 - 10, y2 + 10, x1 - 25, x2 + 25]  # these number are added to give a little margin for the TM

        x1_cut = round(x1 + 0.4 * w)
        x2_cut = round(x1 + 0.6 * w)

        # Pra pegar exatamente a parte em que o peixe sobe e desce. Números calculados pelo photoshop.
        # green_bar_region = img[y1: y2, x1_cut: x2_cut]
        # green_bar_region_bgr = img_bgr[y1: y2, x1_cut: x2_cut]
        green_bar_region = np.zeros([20, 20])
        green_bar_region_bgr = None
        # green_bar_region = img[y1: y2, x1 + 55: x2 - 35]

        # Antes de retornar o frame, faz um resize dele pra um tamanho menor, a fim de não ocupar muito espaço em disco
        # Como uma convnet precisa que todas as imagens tenha o mesmo tamanho, é preciso estabelecer um tamanho fixo
        # para as imagens. Como no nível -5 de zoom, há a menor área de pesca, fazer o resizing de todos os níveis de
        # zoom para o tamanho do zoom -5, assim não necessita esticar nenhuma imagem e todos ficam com o mesmo tamanho.
        # green_bar_region = cv2.resize(green_bar_region, (6, 134))

        return {"Detected": True, "Region": green_bar_region, "Coords": coords_list, "BGR Region": green_bar_region_bgr}

    # Só roda caso não seja achado a região
    return {"Detected": False}
    # return fishing_region(img_bgr, region_template_gray, w, h)


def fishing_region(img_bgr, region_template_gray, w, h):
    # Função usada para encontrar a área de pesca nos frames. Adaptado do tutorial no site oficial do Opencv
    # img: imagem fonte
    # region_template_gray: template em preto e branco
    # w e h: width e height do template

    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGRA2GRAY)

    try:
        res = cv2.matchTemplate(img, region_template_gray, cv2.TM_CCOEFF_NORMED)
        threshold = 0.60

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if (max_val > threshold):
            x1, y1 = max_loc
            x2, y2 = x1 + w, y1 + h

            coords_list = [y1 - 10, y2 + 10, x1 - 25,
                           x2 + 25]  # these number are added to give a little margin for the TM

            x1_cut = round(x1 + 0.4 * w)
            x2_cut = round(x1 + 0.6 * w)

            # Pra pegar exatamente a parte em que o peixe sobe e desce. Números calculados pelo photoshop.
            green_bar_region = img[y1: y2, x1_cut: x2_cut]
            green_bar_region_bgr = img_bgr[y1: y2, x1_cut: x2_cut]
            # green_bar_region = img[y1: y2, x1 + 55: x2 - 35]

            # Antes de retornar o frame, faz um resize dele pra um tamanho menor, a fim de não ocupar muito espaço em disco
            # Como uma convnet precisa que todas as imagens tenha o mesmo tamanho, é preciso estabelecer um tamanho fixo
            # para as imagens. Como no nível -5 de zoom, há a menor área de pesca, fazer o resizing de todos os níveis de
            # zoom para o tamanho do zoom -5, assim não necessita esticar nenhuma imagem e todos ficam com o mesmo tamanho.
            green_bar_region = cv2.resize(green_bar_region, (6, 134))

            return {"Detected": True, "Region": green_bar_region, "Coords": coords_list,
                    "BGR Region": green_bar_region_bgr}

    except Exception as e:
        print(e)

    # Só roda caso não seja achado a região
    return {"Detected": False}


class SaveData(QObject):
    finished = pyqtSignal()
    send_data = pyqtSignal()

    def __init__(self, key, parent=None):
        QObject.__init__(self, parent=parent)

        self.key = key
        self.run = True

    def load_template(self, zoom_level) -> tuple:
        # Loading template according to zoom level:
        logger.info("Loading template image")

        fishing_region_file = f'media\\Images\\fr {zoom_level}g.png'
        region_template = cv2.imread(fishing_region_file, 0)

        wr, hr = region_template.shape[::-1]  # 121, 474

        return region_template, wr, hr

    def main(self):

        # Unique file name
        file_name = 'Data\\Training Data\\%s.npy' % uuid4()

        logger.info("Training data file created")
        training_data = np.empty(shape=[0, 2])

        region_template, wr, hr = self.load_template(
            zoom_level=-4)  # Default value is -4, but it cycles trough. could be from -5 to +5

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

            # res_x, res_y = self.res
            screen = grabscreen.grab_screen()  # Return BGR screen

            if screen is not None:
                # Finds the thin area the fish stays at
                if coords is not None:

                    region = fishing_region(
                        screen[coords[0]:coords[1],
                        coords[2]:coords[3]],
                        region_template, wr, hr
                    )

                else:
                    region = fishing_region(screen, region_template, wr, hr)
                    zoom_dict = self.find_zoom(screen)

                    if zoom_dict['Found']:
                        # In subsequent fishing sessions, it will start by trying this zoom level

                        logger.info(f"Zoom used: {zoom_dict['Zoom']}")
                        region_template, wr, hr = self.load_template(zoom_dict['Zoom'])

                if region["Detected"]:
                    # Se a área for detectada, salvar na np.array o frame e a o key-press do jogador.

                    window = region["Region"]

                    key_pressed = key_check(self.key)  # return 1 or 0

                    data = [window, key_pressed]  # or data = np.array([key_pressed, window], dtype=object)

                    training_data = np.vstack((training_data, data))

                    # Contants for the next loop
                    was_fishing = True
                    bgr_screen_last = region["BGR Region"]

                    # For the first frame of the detected region, get its coordinates to reduce the area to look for it again
                    if coords is None:
                        print("Found")
                        bgr_screen_first = region["BGR Region"]
                        coords = region["Coords"]
                        logger.info("Coordinates found: %s" % coords)
                        initial_time = datetime.datetime.now()

                # If area not detected this frame, but was on the last one, this means fishing is over.
                if not region["Detected"] and was_fishing:
                    logger.info("Fishing finished")
                    final_time = datetime.datetime.now()

                    new_frames = np.float64(len(training_data))

                    print("Frames analysed: %s" % new_frames)

                    # Apenas salva caso houver mais de 75 frames
                    if new_frames >= 75:

                        validated = self.validate(bgr_screen_first, bgr_screen_last)
                        verified = verify_too_similar_frames(training_data)

                        if validated and verified:
                            np.save(file_name, training_data)

                            # Sinaliza ao main_thread que deve enviar os dados coletados
                            self.send_data.emit()
                            print("Session saved!")

                    # Necessary to reset the region coordinates after every fishing session.
                    training_data = np.empty(shape=[0, 2])
                    file_name = 'Data\\Training Data\\%s.npy' % uuid4()
                    coords = None
                    was_fishing = False

                    # Measurements (debug):
                    time_delta = (final_time - initial_time).total_seconds()
                    median_fps = round(new_frames / time_delta, 2)
                    print(f"FPS: {median_fps}\n")
                    method = 'np.vstack'
                    w_img, h_img = window.shape[::-1]

                    with open("Data\\log.txt", 'a') as f:
                        f.write(
                            f"Method: {method}\nMedian FPS: {median_fps}\ndTime: {time_delta}s\n"
                            f"Frames: {new_frames}\nSize: ({w_img}, {h_img})\n\n"
                        )

        # Caso o usuário clique em "Stop" na GUI
        self.finished.emit()

    def find_zoom(self, screen) -> dict:
        """
        Zoom level -5 to -2 are working correctly. Others are not tested.
        """

        for zoom_level in range(-5, 6):  # looping trough every template

            fishing_region_file = 'media\\Images\\fr {}g.png'.format(zoom_level)
            region_template = cv2.imread(fishing_region_file, 0)

            wr, hr = region_template.shape[::-1]

            region = fishing_region(screen, region_template, wr, hr)

            if region['Detected']:
                print(f"Zoom: {zoom_level}")
                return {"Found": True, "Zoom": zoom_level}

        return {"Found": False}

    def validate(self, first_frame, last_frame) -> bool:
        """
        Validates the training data, verifying if the fishing session does not have many sequential repeating frames
        and checks its final result (success/failure).

        Returns False when session failed and True when session is successful
        """
        result = find_green_rectangle(last_frame)
        result_initial = find_green_rectangle(first_frame)

        # # To check last frame:
        # cv2.imshow('LASTFRAME', last_frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # # cv2.imwrite("fishing_chest_blocking.png", last_frame)

        # Finding the size of the green bar at the start
        if result_initial['Found']:
            initial_rect_size = result_initial["Rect Size"]
        else:
            print("Initial size not found. Quitting...")
            return False

        # Checking if there is a chest on the last frame. If there is, just discard this session, as it is too hard to
        # do the validation.
        result_chest = find_chest(last_frame)
        if result_chest['Found']:
            print("Chest detected. Not saving.")
            return False

        # Finding if the fish is inside the rectangle when the session ends
        if result['Found']:

            # If there are 2 rectangles found, the fish is obviously inside the area if there is no chest
            if result['Fish Inside']:
                print("Fish is inside rectangle. This session was a success")
                return True

            else:
                # Checking if something is in front of the green bar, making it smaller. If it is the same size as the
                # first frame, nothing is in front of it, so the fishing failed.
                if initial_rect_size * 1.1 > result['Rect Size'] and initial_rect_size * 0.9 < result['Rect Size']:
                    print("Fish is not blocking. Session failed")

                else:
                    print("Fish or chest is blocking. Finding fish and chest in relation to the green bar height.")
                    result_fish = find_fish(last_frame)

                    fish_height = result_fish["Center Height"]
                    rect_height = result['Center Height']

                    # If the fish center high is above the rectangle center height, the fish is above the rectangle.
                    if fish_height < rect_height:
                        print("Fish is above")

                        rect_lowest_point = result['Lowest point']
                        rect_highest_point = rect_lowest_point - initial_rect_size

                        fish_low_point = result_fish["Lowest Point"]

                        # cv2.circle(last_frame, (10, rect_highest_point), 2, (255, 255, 255), 2)
                        # cv2.circle(last_frame, (10, fish_low_point), 2, (0, 0, 0), 2)

                        # If the fish is above the rectangle, its lowest point should be lower than the rectangle's
                        # highest point so the fish can be inside it
                        if fish_low_point >= rect_highest_point:
                            print("Fish inside")
                            return True

                        else:
                            print("Fish outside")
                            return False

                    else:
                        print("Fish is bellow")

                        rect_highest_point = result['Highest Point']
                        rect_lowest_point = rect_highest_point + initial_rect_size

                        fish_low_point = result_fish["Lowest Point"]

                        # cv2.circle(last_frame, (10, rect_lowest_point), 2, (255, 255, 255), 2)
                        # cv2.circle(last_frame, (10, fish_low_point), 2, (0, 0, 0), 2)

                        # If the fish is bellow the rectangle, its lowest point should be higher than the rectangle's
                        # lowest point so the fish can be inside it
                        if fish_low_point <= rect_lowest_point:
                            print("Fish inside")
                            return True

                        else:
                            print("Fish outside")
                            return False

        else:
            print("Error finding the green rectangle. This session should be deleted.")
            return False

    def stop(self):
        self.run = False
