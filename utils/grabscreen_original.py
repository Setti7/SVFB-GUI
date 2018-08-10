import win32con
import win32gui
import win32ui

import numpy as np


def grab_screen():
    hwin = win32gui.FindWindow(None, "Stardew Valley")

    if hwin:
        rect = win32gui.GetWindowRect(hwin)

        # If all dimensions are negative the game is minimized
        if all(i < 0 for i in rect):

            print(rect)
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

            # print(f"Top-Left corner: ({left}, {top}). Dimensions: ({width}, {height})")

            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

            return img

    else:
        print("game not running")
        return None
