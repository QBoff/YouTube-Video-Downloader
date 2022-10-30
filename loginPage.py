import string
import sys
from os.path import join

from database import Database
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import uic


class LoginPage(QWidget):
    successfulLogin = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.highligtedFiels = list()

    def onLogin(self) -> None:
        login = self.loginField.text()
        password = self.passwordField.text()

        try:
            assert login and password, 'blankFields'
            with Database('Accounts.db') as db:
                user = db.check(email=login, login=login)
                assert user, 'userNotFound'

                state, login = db.login(password, email=login, login=login)
                assert state, 'wrongPassword'

                print('successfully logged in')
                self.successfulLogin.emit(login)
        except AssertionError as ae:
            self.highlight('login', 'password')
            self.errDisplay.setText('Login or password is not right')
        else:
            self.highlight()
            self.errDisplay.setText('')

    def highlight(self, *fieldnames: str) -> None:
        for field in self.highligtedFiels:
            getattr(self, field + "Field").setStyleSheet('')
        self.highligtedFiels = list()

        if fieldnames:
            for field in fieldnames:
                getattr(self, field +
                        "Field").setStyleSheet('border: 2px solid red;')
                self.highligtedFiels.append(field)

    def initUI(self) -> None:
        uic.loadUi(join('uis', 'loginPage.ui'), self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.exit.clicked.connect(
            lambda: sys.exit(QApplication.instance().exit()))
        self.minimize.clicked.connect(lambda: self.showMinimized())
        self.controlPanel.mouseMoveEvent = self.moveWindow
        self.loginButton.clicked.connect(self.onLogin)

    def moveWindow(self, event) -> None:
        # if not self.isMaximized():
        self.move(self.pos() + event.globalPos() - self.clickPosition)
        self.clickPosition = event.globalPos()
        event.accept()

    def mousePressEvent(self, event) -> None:
        self.clickPosition = event.globalPos()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginPage()
    window.show()
    sys.exit(app.exec_())
