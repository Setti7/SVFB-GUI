import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(levelname)s (%(name)s):\t%(asctime)s \t %(message)s', datefmt='%d/%m/%Y %I:%M:%S')

import json, datetime
from urllib.request import urlopen
from urllib.error import URLError
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

BASE_URL = 'http://127.0.0.1'


class CheckForUpdates(QObject):
    update_text = pyqtSignal(dict)

    with open("config.json", "r") as f:
        output = json.loads(f.read())
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

            last_info = output["Version Control"][0]
            version = last_info['Version']
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

        except URLError:
            self.update_text.emit({"Update": False})
            logger.warning("Offline, could not check updates")