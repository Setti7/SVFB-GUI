import win32gui
import win32ui

import numpy as np
import win32con


# from ctypes import windll
# import mss, cv2


def grab_screen(method=0):
    hwin = win32gui.GetForegroundWindow()
    foreground_window_title = win32gui.GetWindowText(hwin)

    # if the foreground window is not the Stardew Valley, return None
    if foreground_window_title != "Stardew Valley":
        return None

    rect = win32gui.GetWindowRect(hwin)

    # If all dimensions are negative the game is minimized
    if all(i < 0 for i in rect):
        return None

    # Method 0: (default)
    # FPS Deco: 60
    # TODO: ainda tem o bug que não captura a imagem no canto direito inferior
    if method == 0:
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

    # Method 1: (Voltani)
    # FPS Deco: 15
    # elif method == 1:
    #
    #     width = rect[2] - rect[0]
    #     height = rect[3] - rect[1]
    #
    #     gameHandle = win32gui.GetWindowDC(hwin)
    #     gameDC = win32ui.CreateDCFromHandle(gameHandle)
    #
    #     memoryDC = gameDC.CreateCompatibleDC()
    #
    #     saveBitMap = win32ui.CreateBitmap()
    #     saveBitMap.CreateCompatibleBitmap(gameDC, width, height)
    #
    #     memoryDC.SelectObject(saveBitMap)
    #
    #     windll.user32.PrintWindow(hwin, memoryDC.GetSafeHdc(), 1)  # printa a tela pra pegar o frame
    #
    #     bmpinfo = saveBitMap.GetInfo()
    #     bmpstr = saveBitMap.GetBitmapBits(True)
    #
    #     img = np.fromstring(bmpstr, dtype='uint8')
    #     img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
    #
    #     win32gui.DeleteObject(saveBitMap.GetHandle())
    #     memoryDC.DeleteDC()
    #     gameDC.DeleteDC()
    #     win32gui.ReleaseDC(hwin, gameHandle)
    #     return img

    # Method 2: (extra)
    # FPS Deco: 30
    # elif method == 2:
    #     left, top = rect[0:2]
    #     width = rect[2] - rect[0]
    #     height = rect[3] - rect[1]
    #
    #     mon = {"top": top, "left": left, "width": width, "height": height}
    #     sct = mss.mss()
    #     img = np.asarray(sct.grab(mon))
    #
    #     return img
