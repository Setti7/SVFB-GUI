import datetime
import json
from urllib.error import URLError
from urllib.request import urlopen

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from utils.Globals import VERSION, RELEASE_DATE, VERSION_CONTROL_URL
from utils.Globals import logger


class CheckForUpdates(QObject):
    update_text = pyqtSignal(dict)

    # Version details:
    version = VERSION
    date = datetime.datetime.strptime(RELEASE_DATE, '%Y-%m-%d')

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    @pyqtSlot()
    def do_work(self):
        try:
            logger.info("Checking updates")
            data = urlopen(VERSION_CONTROL_URL).read()
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

        except Exception as e:
            self.update_text.emit({"Update": False})
            logger.error(e)
