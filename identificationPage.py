import string
import sys
from os.path import join

from functools import partial
from datamanager import Manager, Database, Profile
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


class IdentificationPage(QWidget):
    successfulLogin = pyqtSignal(str)

    msgs = {
        'password': ('Password should have at least 8 characters, 1 upper/lowercase letter, digit', 'password'),
        'login': ('Login should have at least 4 characters and no punctuation symbols', 'login'),
        'email': ('Check your email', 'email'),
        'password+password2': ('Passwords are not the same', 'password+password2')
    }

    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.pageOrder = (self.registrationPage, self.loginPage)
        self.highlightedFields = list()
        self.userData = None

    def initUI(self) -> None:
        uic.loadUi(join('uis', 'identificationPage.ui'), self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.makeConnections()

    def makeConnections(self) -> None:
        self.exit.clicked.connect(
            lambda: sys.exit(QApplication.instance().exit()))

        self.minimize.clicked.connect(self.showMinimized)
        self.controlPanel.mouseMoveEvent = self.moveWindow

        self.registerButton.clicked.connect(self.onRegister)
        self.loginButton.clicked.connect(self.onLogin)
        self.toLoginButton.clicked.connect(partial(self.stackedWidget.setCurrentWidget, self.loginPage))
        self.toRegisterButton.clicked.connect(partial(self.stackedWidget.setCurrentWidget, self.registrationPage))
        self.stackedWidget.currentChanged.connect(self.onPageChange)

        #QOL
        self.emailField.returnPressed.connect(self.loginField.setFocus)
        self.loginField.returnPressed.connect(self.passwordField.setFocus)
        self.passwordField.returnPressed.connect(self.password2Field.setFocus)
        self.password2Field.returnPressed.connect(self.onRegister)

        self.logField.returnPressed.connect(self.passField.setFocus)
        self.passField.returnPressed.connect(self.onLogin)

    def onPageChange(self, index) -> None:
        names = ('Login', 'Registration')
        self.appTitle.setText(names[index])

    def onRegister(self) -> None:
        email = self.emailField.text()
        login = self.loginField.text()
        pass1 = self.passwordField.text()
        pass2 = self.password2Field.text()

        try:
            assert emailCheck(email), self.msgs['email']
            assert loginCheck(login), self.msgs['login']
            assert passwordCheck(pass1), self.msgs['password']
            assert pass1 == pass2, self.msgs['password+password2']

            with Database('Accounts.db') as db:
                emailExists = db.check(email=email)
                loginExists = db.check(login=login)

            if emailExists and loginExists:
                raise AssertionError((
                    'This account already exists, do you wish to login?', 'login+email'))
            elif emailExists:
                raise AssertionError((
                    'This email is already used', 'email'))
            elif loginExists:
                raise AssertionError((
                    'This login is already used', 'login'))
        except AssertionError as ae:
            errorMessage, fieldsToHightlight = ae.args[0]
            self.registrationErr.setText(errorMessage)
            self.highlight(*fieldsToHightlight.split('+'))
        else:  # Successful registration
            self.registrationErr.setText('')
            self.highlight()

            with Database('Accounts.db') as db:
                db.add(email, login, pass1)
                self.userData = email, login, pass1

            Manager.createUserDirectory(login)
            self.successfulLogin.emit(login)

    def onLogin(self) -> None:
        login = self.logField.text()
        password = self.passField.text()

        try:
            assert login and password, 'blankFields'
            with Database('Accounts.db') as db:
                user = db.check(email=login, login=login)
                assert user, 'userNotFound'

                state, login = db.login(password, email=login, login=login)
                assert state, 'wrongPassword'

                self.successfulLogin.emit(login)
        except AssertionError as ae:
            self.highlight('log', 'pass')
            self.errDisplay.setText('Login or password is not right')
        else:
            self.highlight()
            self.errDisplay.setText('')

    def highlight(self, *fieldnames: tuple) -> None:
        for field in self.highlightedFields:
            getattr(self, field + 'Field').setStyleSheet('')
        else:
            self.highlightedFields.clear()

        for field in fieldnames:
            getattr(self, field + 'Field').setStyleSheet('border: 2px solid red;')
            self.highlightedFields.append(field)

    def moveWindow(self, event) -> None:
        self.move(self.pos() + event.globalPos() - self.clickPosition)
        self.clickPosition = event.globalPos()
        event.accept()

    def keyPressEvent(self, event) -> None:
        leftArrowPressed = event.key() in (Qt.Key.Key_Left, Qt.Key.Key_A) 
        rightArrowPressed = event.key() in (Qt.Key.Key_Right, Qt.Key.Key_D)

        if leftArrowPressed or rightArrowPressed:
            currentIndex = self.pageOrder.index(self.stackedWidget.currentWidget())
            nextIndex = currentIndex + (1 if rightArrowPressed else -1)
            if len(self.pageOrder) > nextIndex >= 0:
                self.stackedWidget.setCurrentWidget(self.pageOrder[nextIndex])
                event.accept() 

    def mousePressEvent(self, event) -> None:
        focusWidget = QApplication.focusWidget()
        if focusWidget:
            focusWidget.clearFocus()
        self.clickPosition = event.globalPos()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IdentificationPage()
    window.show()
    sys.exit(app.exec_())
