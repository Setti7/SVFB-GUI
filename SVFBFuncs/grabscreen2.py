import win32gui
import win32ui
from ctypes import windll
import cv2
import numpy as np

hwnd = win32gui.FindWindow(None, 'Stardew Valley')

if hwnd:
    print("Game found!")
    while True:
        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bot - top

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

        saveDC.SelectObject(saveBitMap)

        result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        img = np.fromstring(bmpstr, dtype='uint8')
        img.shape = (bmpinfo['bmHeight'],bmpinfo['bmWidth'], 4)

        cv2.imshow("page",cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

else:
    print("Game not Found!!!")