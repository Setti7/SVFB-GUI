# Done by Frannecklp

import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api


def grab_screen(region):


    hwin = win32gui.FindWindow(None, "Stardew Valley")

    if hwin:
        rect = win32gui.GetWindowRect(hwin)

        # If any dimension is negative the game is minimized, so we need to get the resolution from save file
        if any(i < 0 for i in rect):

            print("game running minimized")
            return None


        else:

            left, top = rect[0:2]
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            hwindc = win32gui.GetWindowDC(hwin)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, width, height)
            memdc.SelectObject(bmp)
            memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

            signedIntsArray = bmp.GetBitmapBits(True)
            img = np.fromstring(signedIntsArray, dtype='uint8')
            img.shape = (height, width, 4)

            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

    else:
        print("game not running")
        return None

