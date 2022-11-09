import sys
from time import sleep

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, pyqtSlot
from datamanager import Manager, Profile

from datetime import date
from downloadPage import DownloadPage
from mainPage import MainPage
from managerPage import ManagerPage
from registrationPage import RegistrationPage
from profileSelector import profileSelector
from loginPage import LoginPage

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


# yesterday = date(2022, 11, 7)
# print(date.today())
# print(yesterday)
# print((date.today() - yesterday).days)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    def switch(_to):
        active = app.activeWindow()
        app.setActiveWindow(_to)

        lastPos = active.pos()
        modifiedPos = (lastPos.x() + active.width() // 2 - _to.width() // 2,
                    lastPos.y() + active.height() // 2 - _to.height() // 2)

        _to.move(*modifiedPos)
        _to.show()
        active.hideEvent = lambda x: _to.show()
        active.hide()
        active = _to

    def openRegistration():
        app.registerWin = RegistrationPage()
        app.loginWin = LoginPage()
        app.registerWin.show()
    
        app.registerWin.loginButton.clicked.connect(lambda: switch(app.loginWin))
        app.loginWin.registerButton.clicked.connect(lambda: switch(app.registerWin))
        app.registerWin.successfulRegister.connect(successfulLogin)

    @pyqtSlot(str)
    def successfulLogin(login):
        QApplication.instance().login = login
        app.mainWin = MainPage(login)
        app.mainWin.upperText.setText(
            f'Welcome, {login}! What brings you here today?')

        app.downloadPage = DownloadPage()
        app.managerPage = ManagerPage()
        app.mainWin.downloadButton.clicked.connect(lambda: switch(app.downloadPage))
        app.mainWin.browseButton.clicked.connect(lambda: switch(app.managerPage))
        # app.mainWin.logoutButton.clicked.connect(openRegistration)

        app.downloadPage.returnButton.clicked.connect(lambda: switch(app.mainWin))

        register = getattr(app, 'registerWin', None)
        login = getattr(app, 'loginWin', None)
        if register is not None and login is not None:
            statusReg = app.registerWin.close()
            statusLog = app.loginWin.close()
            app.registerWin = app.loginWin = None
        
        app.mainWin.show()

    profiles = Manager.loadProfiles()
    distinctProfiles = tuple(set(profiles.values()))
    recentProfile = profiles.get('recentProfile', None)

    if not distinctProfiles:
       openRegistration()
    elif recentProfile is not None:
        successfulLogin(recentProfile[0].userLogin)
    elif len(distinctProfiles) == 1:
        successfulLogin(distinctProfiles[0].userLogin)
    else:
        app.profileSelector = profileSelector(distinctProfiles)
        app.profileSelector.show()
        app.profileSelector.profileSelected.connect(successfulLogin)

    sys.exit(app.exec_())