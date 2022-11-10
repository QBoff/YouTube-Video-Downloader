import sys
from time import sleep

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, pyqtSlot
from datamanager import Manager, Profile

from datetime import date
from downloadPage import DownloadPage
from mainPage import MainPage
from managerPage import ManagerPage
from profileSelector import ProfileSelector
from identificationPage import IdentificationPage

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


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
        active.hide()
        active = _to

    def openRegistration(page='registration'):
        IDPage = IdentificationPage()
        IDPage.successfulLogin.connect(successfulLogin)
        IDPage.stackedWidget.setCurrentWidget(getattr(IDPage, page + 'Page'))
        IDPage.show()

        app.identification = IDPage

    @pyqtSlot(str)
    def onProfileDeletion(login):
        ps = app.ProfileSelector
        for profileIndex in range(1, 4):
            btn = getattr(ps, f'profile{profileIndex}Button')
            if btn.text() == login:
                deleteBtn = getattr(ps, f'delete{profileIndex}Btn')
                deleteBtn.deleteLater()
                break
        btn.setText("No one's profile")
        Manager.removeUserData(login)

    def openProfileSelector(preloadedProfiles=None):
        if getattr(app, 'mainWin', None):
            app.mainWin.close()

        if getattr(app, 'managerPage', None):
            app.managerPage.close()
        if getattr(app, 'downloadPage', None):
            app.downloadPage.close()

        if preloadedProfiles is None:
            preloadedProfiles = Manager.loadProfiles().values()
        
        app.ProfileSelector = ProfileSelector(preloadedProfiles)
        app.ProfileSelector.show()
        app.ProfileSelector.profileSelected.connect(successfulLogin)
        app.ProfileSelector.newProfileRequest.connect(openRegistration)
        app.ProfileSelector.profileDeleteRequest.connect(onProfileDeletion)

    profiles = Manager.loadProfiles()
    recentProfile, lastEnterDate = Manager.getRecentProfile()

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
        app.mainWin.logoutButton.clicked.connect(lambda: openProfileSelector())
        app.downloadPage.returnButton.clicked.connect(lambda: switch(app.mainWin))

        indentificationWin = getattr(app, 'identification', None)
        if indentificationWin:
            indentificationWin.close()
        
        app.mainWin.show()
        Manager.setRecentProfile(login)

    if not profiles:
        openRegistration()
    elif (recentProfile is not None) and (date.today() - lastEnterDate).days <= 7:
        successfulLogin(recentProfile.userLogin)
    else:
        openProfileSelector(profiles.values())

    sys.exit(app.exec_())