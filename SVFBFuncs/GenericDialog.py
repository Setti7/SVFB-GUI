from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

class GenericDialog():

    def __init__(self, text, informative_text, title, icon=None, show=True):
        """
        :param text: First paragraph of the dialog
        :param informative_text: main paragraph of the dialog
        :param title: title of the window
        :param icon: icon of the window
        :param show: if this is set to True, window will be executed with .show() method, if false, it will be .exec_()
        """

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)

        self.msg.setText(text)
        self.msg.setInformativeText(informative_text)
        self.msg.setWindowTitle(title)

        if icon:
            self.msg.setWindowIcon(QIcon(icon))

        ok_btn = self.msg.addButton(QMessageBox.Ok)

        ok_btn.clicked.connect(lambda: print('Hi'))

        if show:
            self.msg.show()
        else:
            self.msg.exec_()

if __name__ == "__main__":
    GenericDialog("Text", "This is informative text", "This is title", show=True)