import numpy as np
from PIL import ImageGrab
import cv2
import time
from getkeys import key_check
import os

upperBound_s1 = np.array([200, 150,
                          255])  # upper and lower bound for the color detection (the way I came up with to find the contour of the green rectangle)
lowerBound_s1 = np.array([130, 0, 85])

upperBound_fish = np.array([50, 255, 197])
lowerBound_fish = np.array([20, 215, 147])

x_center_calibration_value = 10  # Makes the x coordinate of the center of the fish and of the rectangle to be in the right place

x = 105  # If I need to translate the areas of interest easily and equally
y = 75


def fishing_region(img_rgb, region_template_gray, w,
                   h):  # the image format is actually BGR because of Opencv, but I didn't bother changing all the names

    region_detected = False
    floor_height = 460

    green_bar_region = img_rgb[y - 5:470 + y, 347 + x:488 + x]

    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(img_gray, region_template_gray, cv2.TM_CCOEFF_NORMED)

    threshold = 0.65

    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        x1, y1 = pt[0], pt[1]  # + y_adjustment
        x2, y2 = pt[0] + w, pt[1] + h  # + y_adjustment

        region_rect = cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 255, 255), 2)

        # coords_list = [y1, y2, x1 + 55, x2 - 35]
        green_bar_region = img_rgb[y1: y2, x1 + 55: x2 - 35]
        floor_height = y2

        # cv2.imshow("Green bar window", green_bar_region)
        region_detected = True
        # print("Region detected")
        break

    if not region_detected:
        # print("No region")
        pass

    return region_detected, green_bar_region, floor_height


def fish(green_bar_win):
    fish_center_height = 400  # If there is no fish found in the image sets this as the height. 400 hundred is at the bottom of the mini-game because point (0, 0) is the top-left corner
    fish_x_calibration = 0  # 58

    x = 105  # If I need to translate the areas of interest easily and equally
    y = 75

    fish_detected = False

    img_HSV = cv2.cvtColor(green_bar_win, cv2.COLOR_BGR2HSV)
    img_fish = cv2.inRange(img_HSV, lowerBound_fish, upperBound_fish)

    _, conts, hierarchy = cv2.findContours(img_fish, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in conts:

        area = cv2.contourArea(cnt)

        if area > 25:
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            fish_center_point = (int(x + fish_x_calibration), int(y))
            fish_center_height = fish_center_point[1]
            radius = int(radius)
            # fish_center_point = cv2.circle(green_bar_win, fish_center_point, 15, (100, 0, 255), 2)

            fish_detected = True

            # print('Fishy')
            break

    if not fish_detected:
        print("No fish was detected, not saving this frame.")

    return fish_detected, fish_center_height, img_fish


def process_img(img_rgb, green_bar_win):
    img_YCrCb = cv2.cvtColor(green_bar_win,
                             cv2.COLOR_BGR2YCrCb)  # chose this color scheme because ir seemed to be one of the few who worked. BGR2Lab also seemed to work.
    img_green = cv2.inRange(img_YCrCb, lowerBound_s1, upperBound_s1)

    kernel = np.ones((2, 2), np.uint8)
    img_green = cv2.erode(img_green, kernel,
                          iterations=2)  # reduces the noise formed by the green algaes at the bottom of the mini game

    # ================================================================================================================================================================================================

    # Finding contours of the green rectangle (always finds it + some noise):
    _, conts, hierarchy = cv2.findContours(img_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnt_list = []

    for cnt in conts:
        area = cv2.contourArea(cnt)

        # filter noise of those damn algaes
        if area > 200:
            x1, y1, w, h = cv2.boundingRect(cnt)
            x2 = x1 + w  # (x1, y1) = top-left vertex
            y2 = y1 + h  # (x2, y2) = bottom-right vertex
            # rect = cv2.rectangle(green_bar_win, (x1, y1), (x2, y2), (255,0,0), 2) # really useful to uncomment this to debug
            cnt_list.append(cnt)

    # ================================================================================================================================================================================================

    # Finding bottom-most/top-most points, then calculate center point:
    rect_center_heigth = 400  # Lowest point possible for the center of the rectangle if use. I think the number is wrong, needs measurement again.
    lowest_point = 550

    if len(cnt_list) == 2:  # if it find 2 rectangles (which happens when the fish is in the middle of the bar)

        cnt1 = cnt_list[0]  # bottom rect
        cnt2 = cnt_list[1]  # top rect

        topmost = tuple(cnt2[cnt2[:, :, 1].argmin()][0])  # the topm-ost point of the top rect
        bottommost = tuple(cnt1[cnt1[:, :, 1].argmax()][0])  # the bottom-most point of the bottom rect

        lowest_point = int(bottommost[1])
        highest_point = int(topmost[1])

        rect_center_heigth = int(np.round((lowest_point + highest_point) / 2, 0))

        # bot_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, lowest_point), 1, (255, 255, 0), 4) # very useful to know where the bottom point is being found
        # top_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, highest_point), 1, (255, 255, 0), 4) # very useful to know where the top point is being found
        # center_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, rect_center_heigth), 1, (255, 0, 255), 2) # Draws magenta point aroud center

    if len(cnt_list) == 1:  # if it find only 1 rectangle. This means that the fish is not at the bar.

        cnt1 = cnt_list[0]

        topmost = tuple(cnt1[cnt1[:, :, 1].argmin()][0])
        bottommost = tuple(cnt1[cnt1[:, :, 1].argmax()][0])

        lowest_point = int(bottommost[1])
        highest_point = int(topmost[1])

        rect_center_heigth = int(np.round((lowest_point + highest_point) / 2, 0))

        # bot_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, lowest_point), 1, (255, 255, 0), 4) # very useful to know where the bottom point is being found
        # top_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, highest_point), 1, (255, 255, 0), 4) # very useful to know where the top point is being found
        # center_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, rect_center_heigth), 1, (255, 0, 255), 2) # Draws magenta point aroud center

    # ================================================================================================================================================================================================

    # return 'img_green' to see what the script is seeing when finding contours obs: will give error because the window is too small for windows to display

    return img_rgb, rect_center_heigth, lowest_point

run = True
def main(res=[1280, 720], key="C"):
    print("Running on: {}x{}".format(res[0], res[1]))
    print("Using {} key".format(key))
    ###################################################################################################

    upperBound_s1 = np.array([200, 150,
                              255])  # upper and lower bound for the color detection (the way I came up with to find the contour of the green rectangle)
    lowerBound_s1 = np.array([130, 0, 85])

    upperBound_fish = np.array([50, 255, 197])
    lowerBound_fish = np.array([20, 215, 147])

    x_center_calibration_value = 10  # Makes the x coordinate of the center of the fish and of the rectangle to be in the right place

    x = 105  # If I need to translate the areas of interest easily and equally
    y = 75

    file_name = 'Data\\training_data.npy'

    if os.path.isfile(file_name):
        print("Training file exists, loading previos data!")
        training_data = list(np.load(file_name))

    else:
        print("Training file does not exist, starting fresh!")
        training_data = []

    frame_file = 'Data\\frames.npy'

    if os.path.isfile(frame_file):
        print("Frames file exists, loading previos data!")
        frames = list(np.load(frame_file))

    else:
        print("Frames file does not exist, starting fresh!")
        frames = []

    ###################################################################################################

    region_template = cv2.imread('Images\\fishing region 3.png')
    region_template_gray = cv2.cvtColor(region_template, cv2.COLOR_BGR2GRAY)
    wr, hr = region_template_gray.shape[::-1]

    was_fishing = False
    last_time = time.time()

    while run:

        res_x, res_y = res
        screen = np.array(ImageGrab.grab(bbox=(0, 40, res_x, res_y+40 )))  # x = 1280, y = 760

        # print('Frame took {} ms'.format(np.round((time.time()-last_time)*1000, 2)))
        # print('FPS: ', np.round(1/(time.time()-last_time), 1))

        last_time = time.time()

        fishing, green_bar_window, floor_height = fishing_region(screen, region_template_gray, wr, hr)

        if fishing:
            contour, green_bar_height, lowest_point = process_img(screen,
                                                                  green_bar_window)  # process every frame (would be nice if it could process every 5 or so frames, so the process becomes faster).

            fish_detected, fish_height, searching_nemo = fish(green_bar_window)

            d_rect_fish = fish_height - green_bar_height  # if result is + : fish is below the green bar, if result is - : fish is above the green bar
            d_rect_floor = floor_height - lowest_point  # always +

            # keys = key_check()

            key_pressed = key_check(key)

            data = [d_rect_fish, d_rect_floor,
                    key_pressed]  # example c pressed: [231, 456, 1]. c not pressed: [231, 456, 0]

            training_data.append(data)
            print(data)

            was_fishing = True

            # print("G-L:", lowest_point)
            # print("FLoor", floor_height)
            # print("R/Fish:\t", data[0], "R/Floor:\t", data[1], "C pressed:\t", data[2])

        if not fishing and was_fishing:

            if len(frames) == 0:
                # print('list of frames is new')
                frames.append(len(training_data))
                # print(len(training_data))
                print("Frames analysed:\t", len(training_data))

                np.save(frame_file, frames)

                # print(frames)
                print("Saving...")
                np.save(file_name, training_data)
                was_fishing = False

            else:
                frame = len(training_data) - sum(frames)
                frames.append(frame)
                print("Frames analysed:\t", frames[-1])

                np.save(frame_file, frames)

                # print(frames)
                # print(len(training_data))
                print("Saving...")
                np.save(file_name, training_data)
                was_fishing = False

        # cv2.imshow('RGB Region',cv2.cvtColor(green_bar_window, cv2.COLOR_BGR2RGB))

        # if 0xFF == ord('q'):  # cv2.waitKey(25) & : # To close the windows
        #     cv2.destroyAllWindows()
        #     break


if __name__ == "__main__":
    main(res=[1280, 720])
