import sys
from os import remove, rename
from os.path import join, splitext
from threading import Thread

from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip
from pytube import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from datamanager import Manager, Profile
import moviepy.editor as mpe
from time import sleep
from http.client import IncompleteRead
import traceback

from youtube import downloadPreview, getYTSession


def translateSize(size: int) -> str:
    dataTypes = 'B', 'KB', 'MB', 'GB'
    currentIndex = 0

    while currentIndex < len(dataTypes):
        nextSize = size / 1024
        if nextSize > 1:
            currentIndex += 1
            size = nextSize
        else:
            break

    return str(round(size, 2)) + dataTypes[currentIndex]


def url_processign(url) -> str:
    return "=".join(url.split('=')[1:])


class getVideoInfo(QThread):
    finished = pyqtSignal(str, str, QPixmap, list, dict)
    notFound = pyqtSignal()

    def __init__(self, url):
        super().__init__()
        self.url = url

    def getFileSizes(self, session, resolutions):
        sizes = dict()
        try:
            for res in resolutions:
                size = session.streams.filter(resolution=res).first().filesize
                sizes[res] = size
            return sizes
        except:
            return sizes

    def run(self):
        count = 0
        while count < 10:
            try:
                session = getYTSession(self.url)

                if session is not None:
                    if isinstance(session, Playlist):
                        session = session.videos[0]

                    preview = QImage.fromData(downloadPreview(session.thumbnail_url))
                    pixmap = QPixmap.fromImage(preview)

                    title = session.title
                    author = session.author.upper()

                    allRes = {v.resolution for v in session.streams.filter(
                        only_video=True) if v.resolution}
                    resolutions = sorted(allRes, key=lambda x: -int(x[:-1]))

                    sizes = self.getFileSizes(session, resolutions)
                    return self.finished.emit(title, author, pixmap, resolutions, sizes)
                else:
                    return self.notFound.emit()
            except IncompleteRead:
                # Happens if Internet is really slow or has high ping. In other words
                # the connection just gets interrupted, disconnected.
                print('connection got interrupted')
                count += 1
                continue



class DownloadPage(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.activeSession = None

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

        def previewLoad():
            self.leftPageList.setCurrentWidget(self.placeholderPage)
            self.loadingGif = QMovie(join('icons', 'loading.gif'))
            self.alert.setMovie(self.loadingGif)
            self.loadingGif.start()

            self.activeThread = getVideoInfo(self.urlInput.text())
            self.activeThread.finished.connect(self.onPreviewLoad)
            self.activeThread.notFound.connect(self.onFailedPreviewLoad)
            self.activeThread.start(QThread.Priority.NormalPriority)

        self.searchButton.clicked.connect(previewLoad)
        self.qualityInput.currentTextChanged.connect(self.calculateSize)
        self.downloads.buttonClicked.connect(self.download_video)

    @pyqtSlot(str, str, QPixmap, list, dict)
    def onPreviewLoad(self, title, author, pixmap, resolutions, sizes):
        self.savedTitle = title
        self.savedAuthor = author
        self.savedPreview = pixmap
        self.videoSizes = sizes
        self.videoPreview.setPixmap(self.savedPreview)
        self.videoTitle.setText(title)
        self.channelName.setText(author)
        self.leftPageList.setCurrentWidget(self.videoInfo)
        self.populateResolutions(resolutions)
        self.setSelectorButtonsEnabled(True)
        self.loadingGif.stop()

    @pyqtSlot()
    def onFailedPreviewLoad(self):
        self.leftPageList.setCurrentWidget(self.placeholderPage)
        self.alert.setText('This is not a valid youtube url!')
        self.setSelectorButtonsEnabled(False)

    def _download_video_or_audio(self, link=None, res=None, ext_v=None) -> str:

        self.path_to_save_video = join("downloaded_video")
        self.path_to_save_audio = join("downloaded_audio")
        self.path_to_save_subtitles = join("downloaded_subtitles")

        self.link = self.urlInput.text() if link is None else link
        print(self.urlInput.text())
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

            # video_size = yt.streams.filter(res=self.resolution).first(
            # ).filesize_approx / 1024 / 1024 / 1024 / 2
        except:
            print("Link isn't valid")

        account = Manager.getActiveUser()
        pr = Profile(account.userLogin)
        print(pr.settings)
        
        if self.extension_video == "mp4" and self.extension_audio == "mp3":
            if int(self.resolution[:-1]) <= 720:
                if self.extension_video == "mp4":
                    mp4video = yt.streams.filter(
                    file_extension=self.extension_video, res=self.resolution)
                try:
                    mp4video.first().download(pr.settings['directories']['video'])
                    print("ok")
                except:
                    print("mp4")
                    print("Downloading error")
            else:
                mp3audio = yt.streams.filter(only_audio=True)
                try:
                    audio = mp3audio.first().download(filename="a.mp4")
                    base, ext = splitext(audio)
                    new_file = base + '.mp3'
                    try:
                        rename(audio, new_file)
                    except:
                        print("Your audio has already been uploaded")
                        remove(join(pr.settings['directories']['audio'], audio))

                except:
                    print("mp3")
                    print("Download error")
                    
                mp4video = yt.streams.filter(
                        file_extension=self.extension_video, res=self.resolution, only_video=True)
                try:
                    video = mp4video.first().download()
                except:
                    print("mp4")
                    print("Downloading error")
                name = str(video)
                print(name)
                clip = mpe.VideoFileClip(name)
                audio = mpe.AudioFileClip("a.mp3")
                sleep(0.2)
                final_audio = mpe.CompositeAudioClip([audio])
                final_clip = clip.set_audio(final_audio)
                final_clip.write_videofile(join(pr.settings['directories']['video'], name.split('\\')[-1]))
                remove("a.mp3")
                remove(video)
        else:
            if self.extension_video == "mp4":
                mp4video = yt.streams.filter(
                    file_extension=self.extension_video, res=self.resolution, only_video=True)
                try:
                    mp4video.first().download(pr.settings['directories']['video'])
                except:
                    print("mp4")
                    print("Downloading error")

            if self.extension_audio == "mp3":
                mp3audio = yt.streams.filter(only_audio=True)
                try:
                    audio = mp3audio.first().download(pr.settings['directories']['audio'])
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
                lang = 'ru'
                try:
                    lists_tr = YouTubeTranscriptApi.list_transcripts(url_processign(self.link))
                    for i in lists_tr._translation_languages:
                        if i['language_code'] == lang:
                            print(True)
                            data = YouTubeTranscriptApi.get_transcript(
                                url_processign(self.link),
                                (lang,)
                            )
                    # print(lists_tr._translation_languages)
                    # print('ru' in lists_tr._translation_languages.split())
                    # print(lists_tr.find_transcript(language_codes='ru'))
                    name_for_file = f"{self.name_of_video}(subtitles)"
                    path = r'%s' % join(pr.settings['directories']['subtitles'], name_for_file) + ".txt"
                    for punctuation in ':*?"<>|':
                        path = path.replace(punctuation, '')
                    try:
                        with open(path.replace(r"\\", "/"), "w", encoding="utf-8") as file:

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
                                    file.write(item["text"] +
                                            " |" + time + "|" + "\n")
                    except Exception as e:
                        print(traceback.format_exc())
                        print("Your subtitles has already been uploaded")
                except Exception as e:
                    print(traceback.format_exc())
                    print(
                        """Could not retrieve a transcript for the video https://www.youtube.com/watch?v=QMkK47pX6HI! This is most likely caused by: Subtitles are disabled for this video"""
                    )

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
                    target=self._download_video_or_audio(link=i, res=self.qualityInput.currentText(), ext_v="mp4"), daemon=True
                )
        except:
            print("Link isn't valid")

    def download_playlist(self):
        Thread(
            target=self._download_your_playlist, daemon=True
        ).start()

    def download_video(self):
        Thread(
            target=self._download_video_or_audio, daemon=True
        ).start()

    @pyqtSlot(str)
    def calculateSize(self, quality) -> None:
        if quality in self.videoSizes:
            self.sizeText.setText(
                f'Estimated size: {translateSize(self.videoSizes[quality])}')

    def populateResolutions(self, items) -> None:
        self.qualityInput.clear()
        self.qualityInput.addItems(items)

    def setSelectorButtonsEnabled(self, state: bool) -> None:
        self.videoButton.setEnabled(state)
        self.audioButton.setEnabled(state)
        self.subtitlesButton.setEnabled(state)
        self.qualityInput.setEnabled(state)
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
