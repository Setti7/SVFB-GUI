import cv2
import numpy as np

RGB = None   # global ;(
pixel = (20,60,80) # some stupid default

# mouse callback function
def pick_color(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = RGB[y,x]

        #you might want to adjust the ranges(+-10, etc):
        upper =  np.array([pixel[0] + 25, pixel[1] + 25, pixel[2] + 25])
        lower =  np.array([pixel[0] - 25, pixel[1] - 25, pixel[2] - 25])
        print(pixel, lower, upper)

        image_mask = cv2.inRange(RGB, lower, upper)
        cv2.imshow("mask",image_mask)

def main():
    import sys
    global RGB, pixel # so we can use it in mouse callback

    image_src = cv2.imread("test1.png")  # pick.py my.png
    if image_src is None:
        print ("the image read is None............")
        return
    cv2.imshow("bgr",image_src)

    ## NEW ##
    cv2.namedWindow('image_YCrCb')
    cv2.setMouseCallback('image_YCrCb', pick_color)

    # now click into the hsv img , and look at values:
    RGB = cv2.cvtColor(image_src,cv2.COLOR_BGR2HSV)
    cv2.imshow("image_YCrCb", RGB)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

main()