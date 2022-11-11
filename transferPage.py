import sys
from os.path import join

from datamanager import Manager
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic


class TransferWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(join('uis', 'transfer.ui'), self)
        self.stopButton.clicked.connect(self.close)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.mouseMoveEvent = self.moveWindow
        self.startServer()

    def closeEvent(self, event) -> None:
        self.closeServer()

    def startServer(self):
        directory = Manager.getActiveUser().settings['directories']['home']
        # в directory уже лежит директория пользователя. Используй её
        # ..Здесь открой сервер..


        #........................
        qrImage = None  # Сюда положи путь к qr коду.
        self.qrLabel.setFixedSize(450, 450)
        self.qrLabel.setScaledContents(True)
        self.qrLabel.setPixmap(QPixmap(qrImage))

    def closeServer(self):
        # Функция выполниться при закрытии окна (Нажатии на кнопку)
        # ..Здесь закрой сервер..


        #........................
        pass

    def moveWindow(self, event) -> None:
        self.move(self.pos() + event.globalPos() - self.clickPosition)
        self.clickPosition = event.globalPos()
        event.accept()

    def mousePressEvent(self, event) -> None:
        self.clickPosition = event.globalPos()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransferWindow()
    window.show()
    app.exec_()