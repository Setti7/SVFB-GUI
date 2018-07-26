# Done by Frannecklp

import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api


def grab_screen(region):

    if region:
        hwin = win32gui.GetDesktopWindow()

        left, top, x2, y2 = region
        width = x2 - left + 1
        height = y2 - top + 1

    else:

        hwin = win32gui.FindWindow(None, "Stardew Valley")

        if hwin:
            rect = win32gui.GetWindowRect(hwin)

            # If any dimension is negative the game is minimized, so we need to get the resolution from save file
            if any(i < 0 for i in rect):

                width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
                height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
                left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
                top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
                print("game running minimized")


            else:
                print("game running")

                left, top = rect[0:2]
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]

        else:
            print("game not running")

            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

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