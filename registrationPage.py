import string
import sys
from os.path import join

from database import Database
from datamanager import Manager
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import uic


def passwordCheck(password: str) -> bool:
    if len(password) < 8:
        return False

    hasLower = hasUpper = hasDigit = False
    for letter in password:
        if letter.islower():
            hasLower = True
        elif letter.isupper():
            hasUpper = True
        elif letter.isdigit():
            hasDigit = True

        if hasLower and hasUpper and hasDigit:
            return True
    return False


def emailCheck(email: str) -> bool:
    hasNoSpace = ' ' not in email
    hasOneAT = email.count('@') == 1
    hasDotAfterAT = email.rfind('@') < email.rfind('.')

    return hasNoSpace and hasOneAT and hasDotAfterAT


def loginCheck(login: str) -> bool:
    if len(login) < 4:
        return False

    for letter in login:
        if letter in string.punctuation:
            return False
    return True


class RegistrationPage(QWidget):
    successfulRegister = pyqtSignal(str)

    msgs = {
        'password': 'Password should have at least 8 characters, 1 upper/lowercase letter, digit',
        'login': 'Login should have at least 4 characters and no punctuation symbols',
        'email': 'Check your email',
        'password+password2': 'Passwords are not the same'
    }

    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.highligtedFiels = list()
        self.userData = None

    def onRegister(self) -> None:
        email = self.emailField.text()
        login = self.loginField.text()
        pass1 = self.passwordField.text()
        pass2 = self.password2Field.text()

        try:
            assert emailCheck(email), 'email'
            assert loginCheck(login), 'login'
            assert passwordCheck(pass1), 'password'
            assert pass1 == pass2, 'password+password2'

            with Database('Accounts.db') as db:
                emailExists = db.check(email=email)
                loginExists = db.check(login=login)

            if emailExists and loginExists:
                raise AssertionError(
                    'This account already exists, do you wish to login?')
            elif emailExists:
                raise AssertionError('This email is already used')
            elif loginExists:
                raise AssertionError('This login is already used')
        except AssertionError as ae:
            msg = str(ae)

            self.errDisplay.setMaximumHeight(999)
            if msg in self.msgs:
                self.highlight(*msg.split('+'))
                self.errDisplay.setText(self.msgs[msg])
            else:
                fields = msg.split()[1].replace('account', 'login+email')
                self.highlight(*fields.split('+'))

                self.errDisplay.setText(msg)
        else:  # In case it registered and need to move forward
            self.highlight()
            self.errDisplay.setMaximumHeight(0)
            self.errDisplay.setText('')

            self.successfulRegister.emit(login)
            with Database('Accounts.db') as db:
                db.add(email, login, pass1)
                print('added entry!')
                self.userData = email, login, pass1

            Manager.createUserDirectory(login)

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
        uic.loadUi(join('uis', 'registration.ui'), self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.exit.clicked.connect(
            lambda: sys.exit(QApplication.instance().exit()))
        self.minimize.clicked.connect(lambda: self.showMinimized())
        self.controlPanel.mouseMoveEvent = self.moveWindow
        self.registerButton.clicked.connect(self.onRegister)

        self.emailField.returnPressed.connect(lambda: self.loginField.setFocus())
        self.loginField.returnPressed.connect(lambda: self.passwordField.setFocus())
        self.passwordField.returnPressed.connect(lambda: self.password2Field.setFocus())
        self.password2Field.returnPressed.connect(self.onRegister)

    def moveWindow(self, event) -> None:
        # if not self.isMaximized():
        self.move(self.pos() + event.globalPos() - self.clickPosition)
        self.clickPosition = event.globalPos()
        event.accept()

    def mousePressEvent(self, event) -> None:
        self.clickPosition = event.globalPos()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RegistrationPage()
    window.show()
    sys.exit(app.exec_())
