import win32gui
import win32ui
from ctypes import windll
import cv2
import numpy as np

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
            #based on https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-printwindow + https://docs.microsoft.com/en-us/windows/desktop/gdi/capturing-an-image
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bot - top

            gameHandle = win32gui.GetWindowDC(hwnd)
            gameDC = win32ui.CreateDCFromHandle(gameHandle)

            memoryDC = gameDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(gameDC, w, h)

            memoryDC.SelectObject(saveBitMap)

            windll.user32.PrintWindow(hwnd, memoryDC.GetSafeHdc(), 1) #printa a tela pra pegar o frame

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            img = np.fromstring(bmpstr, dtype='uint8')
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

            win32gui.DeleteObject(saveBitMap.GetHandle())
            memoryDC.DeleteDC()
            gameDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, gameHandle)
            return img

    else:
        print("game not running")
        return None

