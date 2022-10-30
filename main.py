import sys
from time import sleep

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, pyqtSlot

from downloadPage import DownloadPage
from mainPage import MainPage
from managerPage import ManagerPage
from registrationPage import RegistrationPage
from loginPage import LoginPage


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Pages
    registerWin = RegistrationPage()
    mainWin = MainPage()
    downloadWin = DownloadPage()
    managerWin = ManagerPage()
    loginWin = LoginPage()

    active = registerWin
    def switch(_to):
        global active
        lastPos = active.pos()
        modifiedPos = (lastPos.x() + active.width() // 2 - _to.width() // 2,
                    lastPos.y() + active.height() // 2 - _to.height() // 2)

        _to.move(*modifiedPos)
        _to.show()
        active.hideEvent = lambda x: _to.show()
        active.hide()
        active = _to

    # Initits
    active.show()

    loginWin.registerButton.clicked.connect(
        lambda: switch(registerWin))
    registerWin.loginButton.clicked.connect(
        lambda: switch(loginWin))
    mainWin.downloadButton.clicked.connect(
        lambda: switch(downloadWin))
    mainWin.browseButton.clicked.connect(
        lambda: switch(managerWin))

    downloadWin.returnButton.clicked.connect(
        lambda: switch(mainWin))

    # After register/login was successful
    @pyqtSlot(str)
    def successfulLogin(login):
        mainWin.upperText.setText(
            f'Welcome, {login}! What brings you here today?')
        switch(mainWin)

    registerWin.successfulRegister.connect(successfulLogin)
    loginWin.successfulLogin.connect(successfulLogin)

    sys.exit(app.exec_())
