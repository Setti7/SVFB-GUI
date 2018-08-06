import numpy as np
import cv2

upperBound_s1 = np.array([200, 150, 255])
lowerBound_s1 = np.array([100, 0, 85])
                        #[130, 0, 85]

upperBound_fish = np.array([50, 255, 197])
lowerBound_fish = np.array([20, 215, 147])

# Makes the x coordinate of the center of the fish and of the rectangle to be in the right place
x_center_calibration_value = 10


def find_green_rectangle(green_bar_win):
    """
    Image parameter needs to be in BGR
    """

    # Chose this color scheme because it seemed to be one of the few who worked. BGR2Lab also seems to work.
    img_YCrCb = cv2.cvtColor(green_bar_win, cv2.COLOR_RGB2YCrCb)

    # Lower and upper bounds were manually found to always detect the green rectangle
    img_green = cv2.inRange(img_YCrCb, lowerBound_s1, upperBound_s1)

    # Eroding to reduce the noise formed by the green algaes at the bottom of the mini game
    kernel = np.ones((2, 2), np.uint8)
    img_green = cv2.erode(img_green, kernel,iterations=2)

    # Finding contours of the green rectangle (always finds it + some noise):
    _, conts, hierarchy = cv2.findContours(img_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnt_list = []
    for cnt in conts:
        area = cv2.contourArea(cnt)

        # filter noise of those damn algaes
        if area > 100: # 200
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


def find_fish(green_bar_win):
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
            #cv2.circle(green_bar_win, (10, fish_center_height), 2, (100, 0, 255), 2)

            return {"Found": True, "Center Height": fish_center_height, "Lowest Point": lowest_point,
                    "Highest Point": highest_point}

    return {"Found": False}


if __name__ == '__main__':

    # test images moved to "Other".
    # To test please move this script to the main folder with the test images too.
    fail_img = cv2.imread('fail.png', 1)
    success_img = cv2.imread('success.png', 1)
    #fail_img = cv2.imread('fish_close_inside.png', 1)
    initial_img = cv2.imread('initial.png', 1)

    result_fish_s = find_fish(success_img)
    result_fish_f = find_fish(fail_img)

    result_rect_s = find_green_rectangle(success_img)
    result_rect_f = find_green_rectangle(fail_img)
    result_rect_i = find_green_rectangle(initial_img)

    if result_rect_i['Found']:
        initial_rect_size = result_rect_i["Rect Size"]
        # print(f"Initial size: {initial_rect_size}")
    else:
        print("Initial size not found. Quitting...")
        exit()


    # if result_rect_s['Found']:
    #     if result_rect_s['Fish Inside']:
    #         print("Fish inside success rect\n")
    #     else:
    #         print("Should search for fish\n")
    #         print(f"Rect S size: {result_rect_s['Rect Size']}")


    if result_rect_f['Found']:

        if result_rect_f['Fish Inside']:
            print("Fish inside fail rect\n")

        else:

            print("Should search for fish\n")
            print(f"Rect F size: {result_rect_f['Rect Size']}")

            if initial_rect_size*1.1 > result_rect_f['Rect Size'] and initial_rect_size*0.9 < result_rect_f['Rect Size']:
                print("Fish is not blocking. Session failed")

            else:

                print("Fish or chest is blocking. Finding fish and chest in relation to the green bar height.")
                fish_height = result_fish_f["Center Height"]
                rect_height = result_rect_f['Center Height']

                if fish_height > rect_height:
                    print("Fish is bellow")

                    rect_highest_point = result_rect_f['Highest Point']
                    rect_lowest_point = rect_highest_point + initial_rect_size  # Subtracts because origin is top-left point

                    fish_low_point = result_fish_f["Lowest Point"]

                    cv2.circle(fail_img, (10, rect_lowest_point), 2, (255, 255, 255), 2)
                    cv2.circle(fail_img, (10, fish_low_point), 2, (0, 0, 0), 2)

                    if fish_low_point <= rect_lowest_point:
                        print("Fish inside")
                    else:
                        print("Fish outside")

                else:
                    print("Fish is above")

                    rect_lowest_point = result_rect_f['Lowest point']
                    rect_highest_point = rect_lowest_point - initial_rect_size # Subtracts because origin is top-left point

                    fish_high_point = result_fish_f["Highest Point"]
                    fish_low_point = result_fish_f["Lowest Point"]

                    cv2.circle(fail_img, (10, rect_highest_point), 2, (255, 255, 255), 2)
                    cv2.circle(fail_img, (10, fish_low_point), 2, (0, 0, 0), 2)

                    if fish_low_point >= rect_highest_point:
                        print("Fish inside")
                    else:
                        print("Fish outside")


    # if result_fish_f['Found']:
    #     print("Found fish in fail\n")
    #
    # if result_fish_s['Found']:
    #     print("Found fish in success\n")

    cv2.imshow('success', success_img)
    cv2.imshow('fail', fail_img)
    cv2.imshow('initial', initial_img)

    # cv2.imshow('success', a)
    # cv2.imshow('success', success_img)
    # cv2.imshow('fail', d)
    # cv2.imshow('fail', fail_img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
