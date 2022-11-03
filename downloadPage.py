import sys
from os.path import join

from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from youtube import getVideoInfo
from pytube import YouTube


class DownloadPage(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.activeURL = None

    def initUI(self) -> None:
        uic.loadUi(join('uis', 'downloadPage.ui'), self)
        self.exit.clicked.connect(
            lambda: sys.exit(QApplication.instance().exit()))
        self.minimize.clicked.connect(lambda: self.showMinimized())
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.controlPanel.mouseMoveEvent = self.moveWindow

        self.gripSize = 16
        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

        # After general stuff
        self.downloadButton.clicked.connect(self.download_video)
        self.searchButton.clicked.connect(self.onURLtype)
    
    # the logic of this page begins
    def download_video(self) -> str:

        self.link = self.urlInput.text()
        self.resolution = self.qualityInput.currentText()  # get resolution from Interface
        self.extension = self.comboBox_2.currentText()  # get extension from Interface
        self.path_to_save = "downloaded_video/"

        try:
            yt = YouTube(self.link)  # if link is correct and this video is on youtube
        except:
            print("Link isn't valid")

        video_size = yt.streams.filter(res="1080p").first(
        ).filesize_approx / 1024 / 1024 / 1024 / 2  # get the file size in gb

        self.sizeText.setText(f"Estimated size: {str(round(video_size, 2))}GB")

        mp4video = yt.streams.filter(
            file_extension=self.extension, res=self.resolution)
        
        try:    
            mp4video.first().download(self.path_to_save)
        except:
            print("Downloading error")

    def onURLtype(self) -> None:
        url = self.urlInput.text()
        if url.startswith('https://www.youtube.com/watch?'):  # If url points to YouTube
            data = getVideoInfo(url)
            if data:  # If successfuly loaded all data
                self.leftPageList.setCurrentWidget(self.videoInfo)
                self.videoTitle.setText(data['title'])
                self.channelName.setText(data['channel'])

                pixmap = QPixmap(data['thumbnail'])
                self.videoPreview.setPixmap(pixmap)
                self.setSelectorButtonsEnabled(True)
            else:  # If url has no video in it.
                self.leftPageList.setCurrentWidget(self.placeholderPage)
                self.alert.setText('Something went wrong. Type in other URL')
                self.setSelectorButtonsEnabled(False)
        else:
            self.leftPageList.setCurrentWidget(self.placeholderPage)
            self.alert.setText('This is not a valid youtube url!')
            self.setSelectorButtonsEnabled(False)

    def setSelectorButtonsEnabled(self, state: bool) -> None:
        self.videoButton.setEnabled(state)
        self.audioButton.setEnabled(state)
        self.subtitlesButton.setEnabled(state)
        if state:
            self.videoButton.setChecked(True)
            self.audioButton.setChecked(True)
        else:
            self.videoButton.setChecked(False)
            self.audioButton.setChecked(False)
            self.subtitlesButton.setChecked(False)

    def resizeEvent(self, event) -> None:
        QMainWindow.resizeEvent(self, event)
        rect = self.rect()
        self.grips[1].move(rect.right() - self.gripSize, 0)
        self.grips[2].move(
            rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        self.grips[3].move(0, rect.bottom() - self.gripSize)

    def moveWindow(self, event) -> None:
        # if not self.isMaximized():
        self.move(self.pos() + event.globalPos() - self.clickPosition)
        self.clickPosition = event.globalPos()
        event.accept()

    def mousePressEvent(self, event) -> None:
        self.clickPosition = event.globalPos()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DownloadPage()
    window.show()
    sys.exit(app.exec_())
