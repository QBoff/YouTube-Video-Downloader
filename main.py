import sys

import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5 import uic
from downloadPage import downloadWindow
from mainPage import mainPage
from register import RegistrationWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window1 = mainPage()
    window2 = downloadWindow()
    window1.show()
    window2.show()
    print(app.activeWindow())
    sys.exit(app.exec_())
