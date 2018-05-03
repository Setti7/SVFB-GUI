from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt, QTimer
import time



class Main(QObject):
    divisible_by_4 = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.run = True

    def main(self):
        x = 1
        while self.run:

            print(x)
            if x%4 == 0:
                self.divisible_by_4.emit()
                x=0
            time.sleep(1)
            x += 1


    def stop(self):
        self.run = False