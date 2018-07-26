import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import json, datetime
from urllib.request import urlopen
from urllib.error import URLError
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from SVFBFuncs.Globals import BASE_URL
import os

class CheckForUpdates(QObject):
    update_text = pyqtSignal(dict)
    if os.path.isfile("config.json"):
        with open("config.json", "r") as f:
            output = json.loads(f.read())
            version = output['Version']
            date = datetime.datetime.strptime(output['Date'], '%Y-%m-%d')

    else:
        print("config file missing. Creating new one")
        default_json = {"Version": 1.0, "Date": "2018-06-23", "Used key": "C", "Resolution": "1280x720", "Zoom": "-4",
                        "User": "", "Password": "", "Ignore Login Popup": False, "Fist time": False}

        with open("config.json", "w") as f:
            f.write(json.dumps(default_json))

        output = default_json
        version = output['Version']
        date = datetime.datetime.strptime(output['Date'], '%Y-%m-%d')

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    @pyqtSlot()
    def do_work(self):
        try:
            logger.info("Checking updates")
            data = urlopen(BASE_URL + "/api/version-control").read()
            output = json.loads(data)

            changes = []
            versions = []
            critical = False
            for data in output['Version Control']:
                if datetime.datetime.strptime(data['Date'], '%Y-%m-%d') > self.date:
                    changes.append(data['Changes'])
                    versions.append(float(data['Version']))
                if data['Critical']:
                    critical = True

            changes = "Changes since v{} (your current version):\n".format(self.version) + "\n".join(changes)
            if len(output["Version Control"]): #checks for null version
                last_info = output["Version Control"][0]
                output["Version Control"][0]
                date = datetime.datetime.strptime(last_info['Date'], '%Y-%m-%d')
                if self.date < date:
                    self.update_text.emit(
                        {
                            "Update": True,
                            "Current Version": self.version,
                            "New Version": version,
                            "Changes": changes,
                            "Critical": critical
                        })
                    logger.info("Update found")
                else:
                    self.update_text.emit({"Update": False})
                    logger.info("No updates available")
            else:
                print("Error, Version Control is null")
                self.update_text.emit({"Update": False})
                logger.info("Cannot check for updates")
                last_info = 'null'





        except URLError:
            self.update_text.emit({"Update": False})
            logger.warning("Offline, could not check updates")