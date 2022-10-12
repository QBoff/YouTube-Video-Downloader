import sys

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QWidget, QApplication
from customs import *


def passwordCheck(password: str):
    if len(password) >= 8:
        hasDigit = hasLower = hasUpper = None
        for letter in password:
            if letter.isupper():
                hasUpper = True
            elif letter.islower():
                hasLower = True
            elif letter.isdigit():
                hasDigit = True
            if hasDigit and hasLower and hasUpper:
                return True
        return False
    return False


def emailCheck(email: str):
    if email.count(' ') == 0:
        if email.count('@') == 1:
            if email.rfind('.') > email.rfind('@'):
                return True
            return False
        return False
    return False


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('uis\Registration.ui', self)

        self.submitButton.clicked.connect(self.onSubmit)
        self.loginButton.clicked.connect(self.onLogin)

    def getInput(self):
        email = self.emailInput.text()
        login = self.loginInput.text()
        password = self.passwordInput.text()
        password2 = self.password2Input.text()

        return email, login, password, password2

    def onSubmit(self):
        email, login, pass1, pass2 = self.getInput()

        try:
            assert passwordCheck(pass1), PasswordFormat.msg
            assert pass1 == pass2, WrongSecondPassword.msg
            assert emailCheck(email), EmailFormat.msg
        except AssertionError as errMsg:
            self.errText.setText(str(errMsg))
            self.adjustSize()
        else:
            self.errText.setText('')

    def onLogin(self):
        print('login')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RegistrationWindow()
    ex.show()
    sys.exit(app.exec_())
