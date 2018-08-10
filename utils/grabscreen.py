import win32gui
import win32ui
import win32con
import win32api
from ctypes import windll
import cv2
import numpy as np

def grab_screen(method=0):
    hwnd = win32gui.FindWindow(None, "Stardew Valley")

    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]

        # If all dimensions are negative the game is minimized
        if all(i < 0 for i in rect):

            print(rect)
            print("game running minimized")
            return None


        else:
            if method == 0: #meu metodo
                #based on https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-printwindow + https://docs.microsoft.com/en-us/windows/desktop/gdi/capturing-an-image


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

            elif method == 1:#metodo adaptado de https://github.com/Sentdex/pygta5/blob/master/grabscreen.py
                #esse metodo pega toda sua tela(tipo um print sqn), e dps corta a regiao que o game esta
                width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
                height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
                left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
                top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

                hwin = win32gui.GetDesktopWindow()

                hwindc = win32gui.GetWindowDC(hwin)
                srcdc = win32ui.CreateDCFromHandle(hwindc)
                memdc = srcdc.CreateCompatibleDC()
                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(srcdc, width, height)
                memdc.SelectObject(bmp)
                memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

                signedIntsArray = bmp.GetBitmapBits(True)
                img = np.fromstring(signedIntsArray, dtype='uint8')

                img.shape = (height,width, 4)
                img = img[rect[1]:rect[3], rect[0]:rect[2]] # corta a imagem, pegando só a regiao do jogo
                srcdc.DeleteDC()
                memdc.DeleteDC()
                win32gui.ReleaseDC(hwin, hwindc)
                win32gui.DeleteObject(bmp.GetHandle())


                return img

            elif method == 2:#grabscreen que funfo pra vc
                left, top = rect[0:2]
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                hwindc = win32gui.GetWindowDC(hwnd)
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
                win32gui.ReleaseDC(hwnd, hwindc)
                win32gui.DeleteObject(bmp.GetHandle())


                return img
    else:
        print("game not running")
        return None