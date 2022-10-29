import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, pyqtSlot

from downloadPage import DownloadPage
from mainPage import MainPage
from managerPage import ManagerPage
from registrationPage import registrationPage


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def switch(_from, _to):
    # Math at it's finest. My own creation =)
    lastPos = _from.pos()
    modifiedPos = (lastPos.x() + _from.width() // 2,
                   lastPos.y() + _from.height() // 2)
    newPos = (modifiedPos[0] - _to.width() // 2,
              modifiedPos[1] - _from.height() // 2)

    _to.move(*newPos)
    _to.show()
    _from.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Pages
    register = registrationPage()
    mainWin = MainPage()
    downloadWin = DownloadPage()
    managerWin = ManagerPage()

    # Initits
    register.show()
    mainWin.downloadButton.clicked.connect(
        lambda: switch(mainWin, downloadWin))
    mainWin.browseButton.clicked.connect(
        lambda: switch(mainWin, managerWin))

    downloadWin.returnButton.clicked.connect(
        lambda: switch(downloadWin, mainWin))
        
    @pyqtSlot(str)
    def successfulRegistration(login):
        mainWin.upperText.setText(f'Welcome, {login}! What brings you here today?')
        switch(register, mainWin)

    register.successfulRegister.connect(successfulRegistration)

    sys.exit(app.exec_())
