import sys
from os.path import join

from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from download_video.video import download_video
from youtube import getVideoInfo
# from download_video.video.download_video import DownloadPage
from pytube import YouTube


class DownloadPage(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        uic.loadUi(join('uis', 'downloadPage.ui'), self)
        self.exit.clicked.connect(
            lambda: sys.exit(QApplication.instance().exit()))
        self.minimize.clicked.connect(lambda: self.showMinimized())
        self.urlInput.returnPressed.connect(self.onURLtype)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.controlPanel.mouseMoveEvent = self.moveWindow

        self.gripSize = 16
        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

        self.downloadButton.clicked.connect(self.download_video)

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
            else:  # If parser couldn't load at least some data from page.
                self.leftPageList.setCurrentWidget(self.placeholderPage)
                self.alert.setText('Something went wrong. Type in other URL')
        else:
            self.leftPageList.setCurrentWidget(self.placeholderPage)
            self.alert.setText('This is not a valid youtube url!')

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

    def download_video(
        self,
        path_to_save="downloaded_video/",
    ) -> str:

        self.link = self.urlInput.text()
        self.resolution = self.qualityInput.currentText()  # get resolution from Interface
        self.extension = self.comboBox_2.currentText()  # get extension from Interface
        self.path_to_save = "downloaded_video/"
        # print(self.resolution, self.extension)

        yt = YouTube(self.link)

        # it's time for Qt part
        # print("Не удалось нати такую ссылку :( ")

        # !!!!!!
        video_size = yt.streams.filter(res="1080p").first(
        ).filesize_approx / 1024 / 1024 / 1024 / 2  # get the file size in gb
        # print(video_size)
        self.sizeText.setText(f"Estimated size: {str(round(video_size, 2))}GB")

        mp4video = yt.streams.filter(
            file_extension=self.extension, res=self.resolution)
        # filter out all the files with mp4 extension and 720p resolution
        mp4video.first().download(self.path_to_save)
        # except:
        #     print("Downloading error")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DownloadPage()
    window.show()
    sys.exit(app.exec_())
