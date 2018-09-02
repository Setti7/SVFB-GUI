import os

import cv2
import numpy as np
import pandas as pd

upperBound_s1 = np.array([200, 150, 255])
lowerBound_s1 = np.array([100, 0, 85])
# [130, 0, 85]

upperBound_fish = np.array([50, 255, 197])
lowerBound_fish = np.array([20, 215, 147])

upperBound_chest = np.array([58, 86, 215])
lowerBound_chest = np.array([8, 36, 165])

# Makes the x coordinate of the center of the fish and of the rectangle to be in the right place
x_center_calibration_value = 10


def find_green_rectangle(green_bar_win) -> dict:
    """
    Image parameter needs to be in BGR
    """

    # Chose this color scheme because it seemed to be one of the few who worked. BGR2Lab also seems to work.
    img_YCrCb = cv2.cvtColor(green_bar_win, cv2.COLOR_RGB2YCrCb)

    # Lower and upper bounds were manually found to always detect the green rectangle
    img_green = cv2.inRange(img_YCrCb, lowerBound_s1, upperBound_s1)

    # TODO: maybe remove this
    # Eroding to reduce the noise formed by the green algaes at the bottom of the mini game
    kernel = np.ones((2, 2), np.uint8)
    img_green = cv2.erode(img_green, kernel, iterations=2)

    # Finding contours of the green rectangle (always finds it + some noise):
    _, conts, hierarchy = cv2.findContours(img_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnt_list = []
    for cnt in conts:
        area = cv2.contourArea(cnt)

        # filter noise of those damn algaes
        if area > 100:  # 200
            # x1, y1, w, h = cv2.boundingRect(cnt)
            # x2 = x1 + w  # (x1, y1) = top-left vertex
            # y2 = y1 + h  # (x2, y2) = bottom-right vertex
            # rect = cv2.rectangle(green_bar_win, (x1, y1), (x2, y2), (255,255,255), 2) # really useful to uncomment this to debug
            cnt_list.append(cnt)

    # Finding bottom-most/top-most points, then calculate center point:
    # if it find only 1 rectangle. This means that the fish is not at the bar.
    if len(cnt_list) == 1:

        cnt1 = cnt_list[0]

        topmost = tuple(cnt1[cnt1[:, :, 1].argmin()][0])
        bottommost = tuple(cnt1[cnt1[:, :, 1].argmax()][0])

        lowest_point = int(bottommost[1])
        highest_point = int(topmost[1])

        rect_center_heigth = int(np.round((lowest_point + highest_point) / 2, 0))
        rect_size = lowest_point - highest_point

        # bot_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, lowest_point), 1, (255, 255, 0), 4) # very useful to know where the bottom point is being found
        # top_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, highest_point), 1, (255, 255, 0), 4) # very useful to know where the top point is being found
        # center_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, rect_center_heigth), 1, (255, 0, 255), 2) # Draws magenta point aroud center

        return {"Found": True, "Center Height": rect_center_heigth, "Lowest point": lowest_point,
                "Highest Point": highest_point, "Rect Size": rect_size, "Fish Inside": False}

    # if it find 2 rectangles (which happens when the fish is in the middle of the bar)
    elif len(cnt_list) == 2:

        # bottom rect
        cnt1 = cnt_list[0]
        # top rect
        cnt2 = cnt_list[1]

        # the top-most point of the top rect
        topmost = tuple(cnt2[cnt2[:, :, 1].argmin()][0])
        # the bottom-most point of the bottom rect
        bottommost = tuple(cnt1[cnt1[:, :, 1].argmax()][0])

        lowest_point = int(bottommost[1])
        highest_point = int(topmost[1])

        rect_center_heigth = int(np.round((lowest_point + highest_point) / 2, 0))
        rect_size = lowest_point - highest_point
        # bot_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, lowest_point), 1, (255, 255, 0), 4) # very useful to know where the bottom point is being found
        # top_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, highest_point), 1, (255, 255, 0), 4) # very useful to know where the top point is being found
        # center_point = cv2.circle(green_bar_win, (topmost[0] + x_center_calibration_value, rect_center_heigth), 1, (255, 0, 255), 2) # Draws magenta point aroud center

        return {"Found": True, "Center Height": rect_center_heigth, "Lowest point": lowest_point,
                "Highest Point": highest_point, "Rect Size": rect_size, "Fish Inside": True}

    # return 'img_green' to see what the script is seeing when finding contours
    return {"Found": False}


def find_fish(green_bar_win) -> dict:
    """
    Image parameter needs to ne in BGR
    """

    # If there is no fish found in the image sets this as the height. 400 hundred is at the bottom of the mini-game because point (0, 0) is the top-left corner
    # fish_center_height = 400
    # fish_x_calibration = 0  # 58

    img_HSV = cv2.cvtColor(green_bar_win, cv2.COLOR_RGB2HSV)
    img_fish = cv2.inRange(img_HSV, lowerBound_fish, upperBound_fish)

    _, conts, hierarchy = cv2.findContours(img_fish, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in conts:

        area = cv2.contourArea(cnt)

        if area > 25:
            # (x, y), radius = cv2.minEnclosingCircle(cnt)
            # fish_center_point = (int(x), int(y))
            # fish_center_height = fish_center_point[1]
            # radius = int(radius)
            # fish_center_point = cv2.circle(green_bar_win, fish_center_point, 15, (100, 0, 255), 2)

            # x1, y1, w, h = cv2.boundingRect(cnt)
            # x2 = x1 + w
            # y2 = y1 + h
            # cv2.rectangle(green_bar_win, (x1, y1), (x2, y2), (255, 255, 255), 2)

            topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
            bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])

            lowest_point = int(bottommost[1])
            highest_point = int(topmost[1])

            fish_center_height = int(np.round((lowest_point + highest_point) / 2, 0))
            # cv2.circle(green_bar_win, (10, fish_center_height), 2, (100, 0, 255), 2)

            return {"Found": True, "Center Height": fish_center_height, "Lowest Point": lowest_point,
                    "Highest Point": highest_point}

    return {"Found": False}


def find_chest(green_bar_win) -> dict:
    img_chest = cv2.cvtColor(green_bar_win, cv2.COLOR_BGRA2BGR)

    img_chest = cv2.inRange(img_chest, lowerBound_chest, upperBound_chest)

    _, conts, hierarchy = cv2.findContours(img_chest, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not conts:
        return {"Found": False}

    else:
        return {"Found": True}


def verify_too_similar_frames(training_data) -> bool:
    """
    Verifies if the button was clicked at least once and verifies if the captured frames are too similar too one another
    """
    # region ONLY FOR TESTING TODO: Remove
    final_result = []
    # endregion

    # Stripping clicks from frames
    session_imgs = [data[0] for data in training_data]
    session_clicks = [data[1] for data in training_data]

    # Checking if the session was active enough:
    n_clicks = 0
    for click in session_clicks:
        if click == 1:
            n_clicks += 1

    active_ratio = round(100 * n_clicks / len(session_clicks), 2)

    # TODO: Decide which percent should be minimum
    if active_ratio <= 10:
        print("Session not active enough. Deleting save.")
        # region ONLY FOR TEST. TODO: Replace with "return False"
        final_result.append(False)
        # endregion

    # Checking if there are enough different frames
    # Making a list of 1 and 0, with 1 meaning this frame and the next one are equal and 0 meaning that this frame and the next one
    # are different.
    result = []
    for i, frame in enumerate(session_imgs):

        try:
            next_frame = session_imgs[i + 1]
            equal = int(np.array_equal(frame, next_frame))
            result.append(equal)

        except IndexError:
            break

    # Counting the number of equal frames (ones) and different frames (zeros)
    equals = result.count(1)
    diffs = result.count(0)

    try:
        equality_ratio = round(100 * equals / (equals + diffs), 2)

    except ZeroDivisionError:
        equality_ratio = 100

    # TODO: test this constant (same as above?)
    if equality_ratio > 25:
        print("There are too many similar frames in this session. Deleting.")
        # region ONLY FOR TEST. TODO: Replace with "return False"
        final_result.append(False)
        # endregion

    # region ONLY FOR TEST. TODO: Replace with "return True"
    if os.path.isfile('Data\\constant_control.pkl'):
        df = pd.read_pickle('Data\\constant_control.pkl')
        new_df = pd.DataFrame([[equality_ratio, active_ratio]], columns=['Equality Ratio', 'Activeness Ratio'])
        df = pd.concat([df, new_df], ignore_index=True)

    else:
        df = pd.DataFrame([[equality_ratio, active_ratio]], columns=['Equality Ratio', 'Activeness Ratio'])

    print(df.tail())
    df.to_pickle('Data\\constant_control.pkl')

    if any(elem == False for elem in final_result):
        return False
    else:
        return True
    # endregion


if __name__ == '__main__':
    result = verify_too_similar_frames(None)
