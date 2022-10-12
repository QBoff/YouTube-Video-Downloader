import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import uic, QtGui


class mainPage(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('uis\mainPage.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)

        # self.setAttribute(Qt.WA_NoSystemBackground)
        self.exit.clicked.connect(lambda: app.exit())
        self.minimize.clicked.connect(lambda: self.showMinimized())
        self.controlPanel.mouseMoveEvent = self.moveWindow

    def moveWindow(self, event):
        if not self.isMaximized():
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()

    def mousePressEvent(self, event) -> None:
        self.clickPosition = event.globalPos() 


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = mainPage()
    window.setWindowIcon(QtGui.QIcon('icons/app.png'))
    window.show()
    sys.exit(app.exec_())
