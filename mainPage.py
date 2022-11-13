import sys
from functools import partial
from os.path import join, abspath

from transferPage import TransferWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip
from PyQt5.QtCore import Qt
from PyQt5 import uic
from datamanager import Manager, Profile


class MainPage(QMainWindow):
    def __init__(self, login) -> None:
        super().__init__()
        self.activeUser = login
        self.initUI()

    def initUI(self) -> None:
        uic.loadUi(join('uis', 'mainPage.ui'), self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.loadSettings()

        self.exit.clicked.connect(
            lambda: sys.exit(QApplication.instance().exit()))
        self.minimize.clicked.connect(self.showMinimized)
        self.controlPanel.mouseMoveEvent = self.moveWindow

        self.gripSize = 16
        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

        self.settingsButton.clicked.connect(partial(self.stackedWidget.setCurrentWidget, self.settingsPage))
        self.returnButton.clicked.connect(partial(self.stackedWidget.setCurrentWidget, self.mainPage))
        self.transferButton.clicked.connect(self.openTransfer)

    def loadSettings(self):
        try:
            settings = Manager.getActiveUser().settings
        except AttributeError:
            settings = Profile.DefaultSettings(self.activeUser)

        qualityPref = settings['preferredQuality']
        optimizeFor = settings['optimizeFor']
        
        dirs = settings['directories']
        videoDir = dirs['video'],
        audioDir = dirs['audio'],
        subDir = dirs['subtitles']

        self.qualityPreference.setCurrentText(qualityPref)
        self.optimizePreference.setCurrentText(optimizeFor)
        self.videoDirectory.setText(abspath(videoDir[0]))
        self.audioDirectory.setText(abspath(audioDir[0]))
        self.subtitlesDirectory.setText(abspath(subDir))
    
        self.settings = settings

    def openTransfer(self):
        openedTransferWindow = getattr(self, 'transferWindow', None)
        if not openedTransferWindow:
            self.transferWindow = TransferWindow()
            self.transferWindow.show()
            self.transferWindow.closeEvent(lambda: setattr(self, 'transferWindow', None))
        elif getattr(openedTransferWindow, 'closing', None):
            self.transferWindow = None
            self.openTransfer()



    def resizeEvent(self, event) -> None:
        QMainWindow.resizeEvent(self, event)
        rect = self.rect()
        self.grips[1].move(rect.right() - self.gripSize, 0)
        self.grips[2].move(
            rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        self.grips[3].move(0, rect.bottom() - self.gripSize)

    def moveWindow(self, event) -> None:
        # if not self.isMaximized():
        self.move(self.pos() + event.globalPos() - self.clickPosition)
        self.clickPosition = event.globalPos()
        event.accept()

    def mousePressEvent(self, event) -> None:
        self.clickPosition = event.globalPos()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.instance().login = 'N1qro'
    window = MainPage('N1qro')
    window.show()

    window.loadSettings()
    sys.exit(app.exec_())
