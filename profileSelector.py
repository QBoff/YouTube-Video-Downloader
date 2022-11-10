import sys
from os.path import join

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import uic


class ProfileSelector(QWidget):
    profileSelected = pyqtSignal(str)
    newProfileRequest = pyqtSignal()

    def __init__(self, profiles: set) -> None:
        super().__init__()
        self.profiles = sorted(profiles, key=lambda x: x.userLogin)
        self.initUI()
        self.profileButtons.buttonClicked.connect(self.onProfileClick)

    def initUI(self) -> None:
        uic.loadUi(join('uis', 'profileSelector.ui'), self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.exit.clicked.connect(
            lambda: sys.exit(QApplication.instance().exit()))
        self.minimize.clicked.connect(lambda: self.showMinimized())
        self.controlPanel.mouseMoveEvent = self.moveWindow

        for i, profile in enumerate(self.profiles, start=1):
            btn = getattr(self, f'profile{i}Button')
            btn.setText(profile.userLogin)

        if i == 3:
            self.createProfile.deleteLater()
        else:
            self.limitLabel.deleteLater()
        #     self.profile3.deleteLater()
        
    def onProfileClick(self, btn):
        login = btn.text()
        if login == "No one's profile":
            self.newProfileRequest.emit()
        else:
            self.profileSelected.emit(login)
        self.close()

    def moveWindow(self, event) -> None:
        self.move(self.pos() + event.globalPos() - self.clickPosition)
        self.clickPosition = event.globalPos()
        event.accept()

    def mousePressEvent(self, event) -> None:
        self.clickPosition = event.globalPos()


if __name__ == "__main__":
    from datamanager import Manager
    from PyQt5.QtCore import pyqtSlot 

    @pyqtSlot(str)
    def onProfileSelect(login):
        print(f'Selected profile is: {login}')


    app = QApplication(sys.argv)
    window = ProfileSelector(set(Manager.loadProfiles().values()))
    window.profileSelected.connect(onProfileSelect)

    window.show()
    reason = app.exec_()
    print('closing..')
    sys.exit(reason)

    # Был текст: You've reached the profile limit
    # Стал: Cannot create anymore profiles. Limit has been reached