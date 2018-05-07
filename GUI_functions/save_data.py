import numpy as np
from PIL import ImageGrab
import cv2, datetime
from PyQt5.QtCore import QObject, pyqtSignal
from GUI_functions.getkeys import key_check
import os, json
from GUI_functions import send_files, grabscreen


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

        coords_list = [y1 - 10, y2 + 10, x1 - 25, x2 + 25] # these number are added to give a little margin for the TM
        green_bar_region = img[y1: y2, x1 + 55: x2 - 35]

        return {"Detected": True, "Region": green_bar_region, "Coords": coords_list}

    if not region_detected:
        # print("No region")
        return {"Detected": False}


class SaveData(QObject):
    score = pyqtSignal(int)
    data_response_code = pyqtSignal(int)

    def __init__(self, key, res, zoom, autosend, parent=None):
        QObject.__init__(self, parent=parent)
        self.res = res
        self.zoom = zoom
        self.autosend = autosend
        self.key = key

        self.run = True

    def main(self):
        print("Running on: {}x{}".format(self.res[0], self.res[1]))
        print("Using {} key".format(self.key))
        print("Autosend: {}".format(self.autosend))
        print("Zoom: {}".format(self.zoom))

        # Checking for data files:
        file_name = 'Data\\training_data.npy'
        frame_file = 'Data\\frames.npy'

        if os.path.isfile(file_name):
            print("Training file exists, loading previos data!")
            # training_data = list(np.load(file_name))
            training_data = np.load(file_name)

        else:
            print("Training file does not exist, starting fresh!")
            training_data = np.empty(shape=[0, 2])

        if os.path.isfile(frame_file):
            print("Frames file exists, loading previos data!")
            # frames = list(np.load(frame_file))
            frames =  np.load(frame_file)

        else:
            print("Frames file does not exist, starting fresh!")
            frames = np.empty(shape=[0, 1])

        # Loading template:
        fishing_region_file = 'media\\Images\\fr {}.png'.format(self.zoom)
        region_template = cv2.imread(fishing_region_file)
        region_template = cv2.cvtColor(region_template, cv2.COLOR_BGR2GRAY)
        wr, hr = region_template.shape[::-1] # 121, 474

        print(fishing_region_file)

        was_fishing = False
        coords = None
        counter = []

        while self.run:

            res_x, res_y = self.res
            screen = grabscreen.grab_screen(region=(0, 40, res_x, res_y+40 )) # Return gray screen

            # Finds the thin area the fish stays at
            if coords:
                # If there was found coords, cut the screen size to look again for the template, so it uses less resources
                region = fishing_region(screen[coords[0]:coords[1], coords[2]:coords[3]], region_template, wr, hr) #[y1, y2, x1 + 55, x2 - 35]
                counter.append(1)
                if len(counter) > 29:
                    print("Finding template in limited space")
                    counter.clear()
            else:
                region = fishing_region(screen, region_template, wr, hr)
                counter.append(1)
                if len(counter) > 49:
                    print("Finding template on full resolution")
                    counter.clear()

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
                    print("Coordinates found")
                    initial_time = datetime.datetime.now()

            # If area not detected this frame, but was on the last one
            if not region["Detected"] and was_fishing:
                final_time = datetime.datetime.now()

                if len(frames) == 0:
                    # print('list of frames is new')
                    frames = np.append(frames, len(training_data))

                    print("Frames analysed:\t", len(training_data))

                    np.save(frame_file, frames)

                    print("Saving...")
                    np.save(file_name, training_data)

                    was_fishing = False
                    self.score.emit(sum(frames))

                else:
                    frame = len(training_data) - sum(frames)
                    frames = np.append(frames, frame)
                    print("Frames analysed:\t", frames[-1])

                    np.save(frame_file, frames)

                    print("Saving...")
                    np.save(file_name, training_data)

                    was_fishing = False
                    self.score.emit(sum(frames))

                if self.autosend:
                    with open("config.txt", 'r') as f:
                        output = json.loads(f.read())
                    BASE_URL = 'http://127.0.0.1'
                    response_code = send_files.send_data(BASE_URL, output['User'], output['Password'])
                    self.data_response_code.emit(int(response_code))
                    print('Response code emitted')

                # Necessary to reset the region coordinates after every fishing session.
                coords = None

                # Measurements:
                time_delta = final_time - initial_time
                frame_yield = 100*frames[-1]/(time_delta.total_seconds()*30)
                print("ΔTime: {}".format(time_delta.total_seconds()))
                print("Yield: {}%".format(frame_yield))

                with open("Data\\log.txt", 'a') as f:
                    f.write("Method: {}\nYield: {}%\ndTime: {}s\nFrames: {}\n\n".format(method, round(frame_yield, 2), time_delta.total_seconds(), frames[-1]))


            # cv2.imshow('Resized', region_template)
            # cv2.imshow('Normal', region_template)
            #
            # if cv2.waitKey(25) == 27:
            #     cv2.destroyAllWindows()
            #     self.run = False

    def stop(self):
        self.run = False


if __name__ == "__main__":
    test = SaveData(key='C', res=(1280, 720), zoom=-4, autosend=False)
    test.main()

