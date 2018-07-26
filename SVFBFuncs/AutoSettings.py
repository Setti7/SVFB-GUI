import win32,win32gui, win32api
import os
from os import walk,  listdir
import glob
class AutoSettings:
    def __init__(self):
        self.get_res()
        self.get_zoom()

    def get_zoom(self):#not fully implemented yet
        print("get zoom")
        path = os.getenv('APPDATA') + "\StardewValley\Saves"
        saves = os.listdir(path)
        for save in saves:

            with open(path+"\\"+save+"\\"+save, "r") as f:

                content = f.read()
                zoom = content.split('<zoomLevel>', 1)[-1]
                zoom = zoom.split('</zoomLevel>', 1)[0]

                return zoom


    def get_res(self):
        hwnd = win32gui.FindWindow(None, "Stardew Valley")
        rect = win32gui.GetWindowRect(hwnd)
        resolution = [0, 0]
        resolution[0] = rect[2] - rect[0]
        resolution[1] = rect[3] - rect[1]
        return resolution




a = AutoSettings()