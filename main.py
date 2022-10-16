import sys

from PyQt5.QtWidgets import QApplication

from downloadPage import downloadWindow
from mainPage import mainPage


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
    mainWin = mainPage()
    downloadWin = downloadWindow()
    mainWin.show()

    mainWin.downloadButton.clicked.connect(
        lambda: switch(mainWin, downloadWin))
    downloadWin.returnButton.clicked.connect(
        lambda: switch(downloadWin, mainWin))

    sys.exit(app.exec_())
