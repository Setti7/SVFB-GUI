import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')


import numpy as np
import cv2, datetime
from PyQt5.QtCore import QObject, pyqtSignal
from GUI_functions.getkeys import key_check
import os
from GUI_functions import grabscreen
from GUI_functions.SendFiles import SendData


x = 105  # If I need to translate the areas of interest easily and equally
y = 75


def fishing_region(img, region_template_gray, w, h):
    # the image format is actually BGR because of Opencv, but I didn't bother changing all the names

    region_detected = False

    #green_bar_region = img[y - 5:470 + y, 347 + x:488 + x]

    res = cv2.matchTemplate(img, region_template_gray, cv2.TM_CCOEFF_NORMED) #cv.TM_CCORR_NORMED tava usando cv2.TM_CCOEFF_NORMED

    threshold = 0.65

    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        x1, y1 = pt[0], pt[1]  # + y_adjustment
        x2, y2 = pt[0] + w, pt[1] + h  # + y_adjustment


        # TODO: Fix this constants so the image can be resized to 0.3*size
        coords_list = [y1 - 10, y2 + 10, x1 - 25, x2 + 25] # these number are added to give a little margin for the TM
        green_bar_region = img[y1: y2, x1 + 55: x2 - 35]

        green_bar_region = cv2.resize(green_bar_region, None, fx=0.3, fy=0.3) # TODO: optimize this resizing

        return {"Detected": True, "Region": green_bar_region, "Coords": coords_list}

    if not region_detected:
        # print("No region")
        return {"Detected": False}


class SaveData(QObject):
    finished = pyqtSignal()
    score = pyqtSignal(int)
    data_response_code = pyqtSignal(int)

    def __init__(self, key, res, zoom, autosend, session=None, parent=None):
        QObject.__init__(self, parent=parent)
        self.res = [int(x_or_y) for x_or_y in res.split('x')]
        self.zoom = zoom
        self.autosend = autosend
        self.key = key

        if self.autosend:
            self.session = session

        self.run = True

    def main(self):

        file_name = 'Data\\training_data.npy'
        frame_file = 'Data\\frames.npy'

        # region Checking if data files already exists
        if os.path.isfile(file_name):
            logger.info("Loading training data file")
            training_data = np.load(file_name)

        else:
            logger.warning("Training data file does not exist")
            training_data = np.empty(shape=[0, 2])

        if os.path.isfile(frame_file):
            logger.info("Loading frames file")
            frames =  np.load(frame_file)

        else:
            logger.warning("Frames file does not exist")
            frames = np.empty(shape=[0, 1])
        # endregion

        # Loading template:
        logger.info("Loading template image")
        fishing_region_file = 'media\\Images\\fr {}.png'.format(self.zoom)
        region_template = cv2.imread(fishing_region_file)
        # region_template = cv2.resize(region_template, None, fx=0.3, fy=0.3) # TODO: using smaller img for less space used
        region_template = cv2.cvtColor(region_template, cv2.COLOR_BGR2GRAY)
        wr, hr = region_template.shape[::-1] # 121, 474

        was_fishing = False
        coords = None
        # counter = []
        logger.info("Data started")

        while self.run:

            res_x, res_y = self.res
            screen = grabscreen.grab_screen(region=(0, 40, res_x, res_y+40 )) # Return gray screen

            # screen = cv2.resize(screen, None, fx=0.3, fy=0.3) # TODO: using smaller img for less space used

            # Finds the thin area the fish stays at
            if coords:
                # If there was found coords, cut the screen size to look again for the template, so it uses less resources
                region = fishing_region(screen[coords[0]:coords[1], coords[2]:coords[3]], region_template, wr, hr) #[y1, y2, x1 + 55, x2 - 35]
                # counter.append(1)
                # if len(counter) > 29:
                #     print("Finding template in limited space")
                #     counter.clear()
            else:
                region = fishing_region(screen, region_template, wr, hr)
                # counter.append(1)
                # if len(counter) > 49:
                #     print("Finding template on full resolution")
                #     counter.clear()

            if region["Detected"]:

                window = region["Region"]

                key_pressed = key_check(self.key) # return 1 or 0

                data = [window, key_pressed] # or data = np.array([key_pressed, window], dtype=object)
                # print(data)

                # training_data.append(data)
                training_data = np.vstack((training_data, data))
                method = 'np.vstack'

                was_fishing = True

                # For the first frame of the detected region, get its coordinates to reduce the area to look for it again
                if not coords:
                    coords = region["Coords"]
                    logger.info("Coordinates found: %s" % coords)
                    initial_time = datetime.datetime.now()

            # If area not detected this frame, but was on the last one
            if not region["Detected"] and was_fishing:
                logger.info("Fishing finished")
                final_time = datetime.datetime.now()
                was_fishing = False

                if len(frames) == 0:
                    # print('list of frames is new')
                    new_frames = np.float64(len(training_data))

                else:
                    new_frames = len(training_data) - sum(frames)

                print("Frames analysed: %s" % new_frames)

                if new_frames >= 75:
                    frames = np.append(frames, new_frames)

                    np.save(frame_file, frames)

                    print("Saving...")
                    np.save(file_name, training_data)

                    if self.autosend:
                        send = SendData(self.session, send_return=True)
                        result = send.send_data() # TODO: site está recebendo varios arquivos agora, então tem que deixar o autosend sempre ligado e fazer com que, caso seja enviado com sucesso, apague o arquivo. Assim, o training_data do computador será apenas uma sessão de pescamento.
                        print("Result code: ", result)
                        self.data_response_code.emit(result)

                    self.score.emit(sum(frames))

                else:
                    print("Not saving!")
                    logger.debug("Data too small")

                # Necessary to reset the region coordinates after every fishing session.
                coords = None

                # Measurements:
                time_delta = (final_time - initial_time).total_seconds()
                median_fps = new_frames/time_delta
                print("Median FPS: {}".format(median_fps))
                print("ΔTime: {}".format(time_delta))

                with open("Data\\log.txt", 'a') as f:
                    f.write("Method: {}\nMedian FPS: {}\ndTime: {}s\nFrames: {}\n\n".format(
                        method,
                        round(median_fps, 2),
                        time_delta, new_frames))

        self.finished.emit()

    def stop(self):
        self.run = False

if __name__ == "__main__":
    test = SaveData(key='C', res="1280x720", zoom=-4, autosend=False)
    test.main()

