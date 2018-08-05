import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api

def grab_screen():
    e1 = cv2.getTickCount()
    hwnd = win32gui.FindWindow(None, "Stardew Valley")

    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)

        # If all dimensions are negative the game is minimized
        if all(i < 0 for i in rect):

            print(rect)
            print("game running minimized")
            return None


        else:

            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bot - top
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

            saveDC.SelectObject(saveBitMap)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            img = np.fromstring(bmpstr, dtype='uint8')
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            e2 = cv2.getTickCount()
            print((e2 - e1) / cv2.getTickFrequency())
            return img

    else:
        print("game not running")
        return None

