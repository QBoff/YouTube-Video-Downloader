import sys
from os.path import join, splitext
from os import rename, remove
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from youtube import getVideoInfo
from pytube import YouTube, Playlist
from threading import Thread
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import requests


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
        self.addToQueueButton.clicked.connect(self.download_playlist)

    # the logic of this page begins
    def _download_video_or_audio(self, link=None, res=None, ext_v=None) -> str:

        self.path_to_save_video = join("downloaded_video")
        self.path_to_save_audio = join("downloaded_audio")
        self.path_to_save_subtitles = join("download_subtitles")

        self.link = self.urlInput.text() if link is None else link
        self.resolution = None if res is None else res
        self.extension_video = None if ext_v is None else ext_v
        self.extension_audio = None
        self.extension_sub = None
        self.name_of_video = ""

        # get extension from Interface
        if self.videoButton.isChecked():
            self.extension_video = "mp4"
            self.resolution = self.qualityInput.currentText()  # get resolution from Interface

        if self.audioButton.isChecked():
            self.extension_audio = "mp3"

        if self.subtitlesButton.isChecked():
            self.extension_sub = "str"

        try:
            # if link is correct and this video is on youtube
            yt = YouTube(self.link)
            self.name_of_video = yt.title
            
            video_size = yt.streams.filter(res=self.resolution).first(
            ).filesize_approx / 1024 / 1024 / 1024 / 2
        except:
            print("Link isn't valid")

        video_size = yt.streams.filter(res=self.resolution).first(
        ).filesize_approx / 1024 / 1024 / 1024 / 2  # get the file size in gb

        self.sizeText.setText(f"Estimated size: {str(round(video_size, 2))}GB")

        if self.extension_video == "mp4":
            mp4video = yt.streams.filter(
                file_extension=self.extension_video, res=self.resolution)
            try:
                mp4video.first().download(self.path_to_save_video)
            except:
                print("mp4")
                print("Downloading error")

        if self.extension_audio == "mp3":
            mp3audio = yt.streams.filter(only_audio=True)
            try:
                audio = mp3audio.first().download(self.path_to_save_audio)
                base, ext = splitext(audio)
                new_file = base + '.mp3'
                try:
                    rename(audio, new_file)
                except:
                    print("Your audio has already been uploaded")
                    remove(join(self.path_to_save_audio, audio))

            except:
                print("Download error")

        if self.extension_sub == "str":
            data = YouTubeTranscriptApi.get_transcript(
                self.url_processign(self.link),
                ('en', 'ru')
            )
            name_for_file = f"{self.name_of_video}(subtitles)"
            try:
                with open(join(self.path_to_save_subtitles, f"{name_for_file}.str"), "w", encoding="utf-8") as file:

                    for item in data:
                        # if item starts with [ it's not our stuff :)
                        print(item)
                        if item["start"] < 60:
                            time = f'{str(item["start"])} сек'
                        elif item["start"] >= 60 and item["start"] < 3600:
                            time = f'{item["start"] // 60} мин {str(item["start"] % 60)} сек'
                        elif item["start"] >= 3600:
                            time = f'{item["start"] // 3600} час {item["start"] % 3600 // 60} мин {item["start"] % 60} сек'
                        if item["text"][0] != '[':
                            file.write(item["text"] + " |" + time + "|" + "\n")
            except:
                print("Your subtitles has already been uploaded")

    def _download_your_playlist(self):
        self.path_to_save_video = join("downloaded_video")
        self.path_to_save_audio = join("downloaded_audio")
        self.path_to_save_subtitles = join("download_subtitles")

        link = self.urlInput.text()
        try:
            playList = Playlist(link)
            # print(playList.title)
            
            for i in playList:
                Thread(
                    target=self._download_video_or_audio(link=i, res="360p", ext_v="mp4"), daemon=True
                )
        except:
            print("Link isn't valid")
    
    def download_playlist(self):
        Thread(
            target=self._download_your_playlist, daemon=True
        ).start()
        

    def download_video(self):
        Thread(
            target=self._download_video_or_audio(), daemon=True
        ).start()

    def url_processign(self, url) -> str:
        return "=".join(url.split('=')[1:])

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
