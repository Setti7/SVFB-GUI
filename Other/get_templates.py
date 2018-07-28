import time
import win32api as wapi
import win32gui
import win32ui

import cv2
import numpy as np
import win32con


class GetTemplates():
    """
    Classe de auxílio para capturar templates.

    Quando é apertado Q, é tirado um screenshot que é salvo com seu nível de zoom no nome.
    A primeira screenshot deve ter zoom level = -5, com as próximas sendo cada vez mais um nível maior.
    """

    def __init__(self):
        zm = -5
        print(f"Waiting for zoom: {zm}")

        while True:

            key = self.key_check("Q")

            if key:
                screen = self.grab_screen()

                cv2.imwrite(f"Get-Templates\\Template {zm}.png", screen)

                zm += 1

                if zm > 5:
                    print("Done")
                    exit(1)

                print(f"Waiting for zoom: {zm}")
                time.sleep(1)

    def grab_screen(self):

        hwin = win32gui.GetDesktopWindow()

        rect = win32gui.GetWindowRect(hwin)

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

    def key_check(self, key):
        if wapi.GetAsyncKeyState(ord(key)):
            return True
        else:
            return False


def fishing_region(img, region_template_gray):
    w, h = region_template_gray.shape[::-1]  # 121, 474

    res = cv2.matchTemplate(img, region_template_gray, cv2.TM_CCOEFF_NORMED)

    threshold = 0.4
    # threshold = 0.7913

    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        # Caso seja encontrado o template matching, será retornado apenas um valor, que é o primeiro ponto aonde houve
        # o match. Seria melhor mudar isso para retornar o valor daonde teve o melhor match.
        x1, y1 = pt[0], pt[1]
        x2, y2 = pt[0] + w, pt[1] + h

        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        print(loc)
        break

    # Só roda caso não seja achado a região
    return img


# Constants:
ZOOM = "-4AA"

# if __name__ == '__main__':
#
#     # Loading template according to zoom level:
#     template = 'media\\Images\\fr {}.png'.format(ZOOM)
#     img = 'media\\Images\\t.png'
#
#     rt_BGR = cv2.imread(template)
#     img = cv2.imread(img)
#
#     img_GRAY = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
#     rt_BGRA = cv2.cvtColor(rt_BGR, cv2.COLOR_BGR2BGRA)
#
#     rt_BGRA_2_GRAY = cv2.cvtColor(rt_BGR, cv2.COLOR_BGRA2GRAY)
#     rt_BGR_2_GRAY = cv2.cvtColor(rt_BGR, cv2.COLOR_BGR2GRAY)
#
#     s = fishing_region(img_GRAY, rt_BGR_2_GRAY)
#
#
#     cv2.imshow('BGR', s)
#     # cv2.imshow('BGRA', rt_BGRA)
#     # cv2.imshow('BGR 2 GRAY', rt_BGR_2_GRAY)
#     # cv2.imshow('BGRA 2 GRAY', rt_BGRA_2_GRAY)
#     #
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

if __name__ == '__main__':
    GetTemplates()
