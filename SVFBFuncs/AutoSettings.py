import os
import win32gui
import xml.etree.ElementTree as ET


class AutoSettings:

    def get_zoom(self):  # not fully implemented yet
        zooms = []
        path = os.getenv('APPDATA') + "\StardewValley\Saves"
        saves = os.listdir(path)
        for save in saves:
            with open(path + "\\" + save + "\\" + save, "r") as f:
                content = f.read()
                zoom = content.split('<zoomLevel>', 1)[-1]
                zoom = zoom.split('</zoomLevel>', 1)[0]
                zooms.append(zoom)

        return zooms

    def get_res(self) -> dict:
        """
        Retorna dicionário com tuples da resolução e do ponto origem do jogo.
        Check automático caso o jogo eseja minimizado ou fechado.
        """

        hwnd = win32gui.FindWindow(None, "Stardew Valley")

        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)

            # If any dimension is negative the game is minimized, so we need to get the resolution from save file
            if any(i < 0 for i in rect):
                return {"Error": True, "Details": "Game is minimized"}

            x1, y1 = rect[0:2]
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]

            return {"Starting Point": (x1, y1), "Resolution": (w, h), "Error": False}

        else:
            return {"Error": True, "Details": "Game is not running"}

    def get_res_by_save(self) -> dict:
        saves_folders = os.path.join(os.getenv('APPDATA'), "StardewValley\Saves")

        char_folders = [save_folder for save_folder in os.listdir(saves_folders)]

        resolution_dict = {}
        for character in char_folders:

            save_file = os.path.join(saves_folders, character) + f"\\{character}"

            tree = ET.parse(save_file)

            char_name = tree.find("player/name").text

            for x_res in tree.iter(tag='preferredResolutionX'):
                for y_res in tree.iter(tag='preferredResolutionY'):
                    resolution_dict[char_name] = (int(x_res.text), int(y_res.text))

        return resolution_dict


if __name__ == "__main__":
    auto_set = AutoSettings()

    res_result = auto_set.get_res()

    if res_result["Error"]:
        print("Game is closed or minimized, getting resolution from save files")
        res_result = auto_set.get_res_by_save()

    print(res_result)

    zoom = auto_set.get_zoom()
    print(zoom)
