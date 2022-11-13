import sys
import traceback
from http.client import IncompleteRead
from os import remove, rename
from os.path import join, splitext
from threading import Thread

from typing import Any
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip, QMessageBox
from pytube import Playlist, YouTube, Stream
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

from datamanager import Audio, Manager, Profile, Subtitles, Video
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


def showMessage(title, text, infText):
    msgBox = QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.setInformativeText(infText)
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setStandardButtons(QMessageBox.Ok)

    msgBox.exec_()


def url_processign(url) -> str:
    return "=".join(url.split('=')[1:])


class getVideoInfo(QThread):
    finished = pyqtSignal(str, str, bytes, list, dict)
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

                    preview = downloadPreview(session.thumbnail_url)
                    # preview = QImage.fromData(downloadPreview(session.thumbnail_url))
                    # pixmap = QPixmap.fromImage(preview)

                    title = session.title
                    author = session.author.upper()

                    allRes = {v.resolution for v in session.streams.filter(
                        only_video=True) if v.resolution}
                    resolutions = sorted(allRes, key=lambda x: -int(x[:-1]))

                    sizes = self.getFileSizes(session, resolutions)
                    return self.finished.emit(title, author, preview, resolutions, sizes)
                else:
                    return self.notFound.emit()
            except IncompleteRead:
                # Happens if Internet is really slow or has high ping. In other words
                # the connection just gets interrupted, disconnected.
                print('connection got interrupted')
                count += 1
                continue



class DownloadPage(QMainWindow):
    downloadFinished = pyqtSignal(Video)
    downloadInterrupted = pyqtSignal()
    chunkDownloaded = pyqtSignal(Stream, bytes, int)

    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.currentlyDownloading = False
        self.activeSession = None

    def initUI(self) -> None:
        uic.loadUi(join('uis', 'downloadPage.ui'), self)
        self.progressBar.hide()
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
        self.downloadFinished.connect(self.onDownloadFinish)
        self.chunkDownloaded.connect(self.progressAchieved)
        self.downloadInterrupted.connect(self.onDownloadFail)

    @pyqtSlot(Video)
    def onDownloadFinish(self, newVideo):
        showMessage(
            title='Successfully downloaded',
            text='You can watch this video in the video manager',
            infText=''    
        )

    @pyqtSlot()
    def onDownloadFail(self):
        showMessage(
            title='Same video',
            text='You already have this video installed!',
            infText='Delete it first, then try again.'
        )

    @pyqtSlot(str, str, bytes, list, dict)
    def onPreviewLoad(self, title, author, previewInBytes, resolutions, sizes):
        self.savedTitle = title
        self.savedAuthor = author
        self.savedPreview = previewInBytes
        self.videoSizes = sizes
        self.videoPreview.setPixmap(QPixmap.fromImage(QImage.fromData(previewInBytes)))
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

    @pyqtSlot(Stream, bytes, int)
    def progressAchieved(self, stream, chunk, bytes_remaining):
        self.progressBar.show()
        self.progressBar.setFormat(f'{stream.title} - %p%')
        totalDownloaded = round((1 - bytes_remaining / stream.filesize) * 100)
        self.progressBar.setValue(totalDownloaded)

        if totalDownloaded == 100:
            self.progressBar.hide()

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
            print(self.link)
            yt = YouTube(self.link, on_progress_callback=self.chunkDownloaded.emit)
            print(yt)
            self.name_of_video = yt.title

            # video_size = yt.streams.filter(res=self.resolution).first(
            # ).filesize_approx / 1024 / 1024 / 1024 / 2
        except Exception as E:
            print(E)
            print("Link isn't valid")

        pr = Manager.getActiveUser()
        print(pr)

        if self.extension_video == "mp4" and self.extension_audio == "mp3":
            print(self.resolution[:-1])
            if int(self.resolution[:-1]) <= 720:
                resolutions = [
                    i.resolution for i in yt.streams.filter(progressive=False)]
                if self.extension_video == "mp4" and self.resolution in resolutions:
                    try:
                        filename = self.savedTitle
                        for punc in '\/:*?"<>|.':
                            filename = filename.replace(punc, '')
                        filename += '.mp4'

                        mp4video = yt.streams.filter(
                            progressive=True, res=self.resolution, mime_type="video/mp4")
                        mp4video.first().download(
                            pr.settings['directories']['video'], filename=filename)

                        user_login = pr.userLogin
                        path = join(pr.settings['directories']['video'], f"{filename}")                        
                        prev = self.savedPreview
                        title = self.savedTitle
                        author = self.savedAuthor
                        videoObj = Video(path, prev, title, author)

                        with Manager(user_login) as folder:
                            for video in folder.getVideos():
                                if video.videoPath == videoObj.videoPath:
                                    # showMessage(
                                    #     title='Same video download',
                                    #     text='You already have this video downloaded',
                                    #     infText='Delete it from the videomanager ui and try again'    
                                    # )
                                    self.downloadInterrupted.emit()
                                    self.currentlyDownloading = False
                                    break
                            else:
                                print('cool')
                                folder.addVideo(videoObj)
                                print('ok')  #TODO ALERT HERE!
                                self.downloadFinished.emit(videoObj)
                                self.currentlyDownloading = False

                    except AttributeError as AE:
                        print(AE)
                        print(
                            f"this video cannot be downloaded in mp4 format and {self.resolution} quality")
                    except Exception as e:
                        print(traceback.format_exc())
                        print("mp4")
                        print("Downloading error")
                else:
                    print(
                        f"This video cannot be downloaded in mp4 format and {self.resolution} quality")
            else:
                mp3audio = yt.streams.get_by_itag(251)  #.filter(only_audio=True, file_extension="mp4")
                print(mp3audio)
                try:
                    audio = mp3audio.download(
                        pr.settings['directories']['audio'])
                    base, ext = splitext(audio)
                    new_file = base + '.mp3'
                    try:
                        rename(audio, new_file)
                    except:
                        print("Your audio has already been uploaded")
                        remove(
                            join(pr.settings['directories']['audio'], audio))

                except:
                    print("mp3")
                    print("Download error")

                mp4video = yt.streams.filter(
                    file_extension=self.extension_video, res=self.resolution, only_video=True)
                try:
                    video = mp4video.first().download(pr.settings['directories']['video'])
                except:
                    print("mp4")
                    print("Downloading error")
        else:
            try:
                if self.extension_video == "mp4":
                    mp4video = yt.streams.filter(
                        file_extension=self.extension_video, res=self.resolution, only_video=True)
                    try:
                        mp4video.first().download(
                            pr.settings['directories']['video'])
                        print("ok")
                    except:
                        print("mp4")
                        print("Downloading error")

                if self.extension_audio == "mp3":
                    mp3audio = yt.streams.get_by_itag(251)  #.filter(only_audio=True)
                    try:
                        audio = mp3audio.download(
                            pr.settings['directories']['audio'])
                        base, ext = splitext(audio)
                        new_file = base + '.mp3'
                        try:
                            rename(audio, new_file)
                            print("ok")
                        except:
                            print("Your audio has already been uploaded")
                            remove(join(self.path_to_save_audio, audio))
                        self.currentlyDownloading = False
                    except:
                        print("Download error")
            except:
                print("Problems with the connection. Please reconnect")
                

        if self.extension_sub == "str":
            lang = 'ru'
            try:
                lists_tr = YouTubeTranscriptApi.list_transcripts(
                    url_processign(self.link))
                for i in lists_tr._translation_languages:
                    if i['language_code'] == lang:
                        print(True)
                        data = YouTubeTranscriptApi.get_transcript(
                            url_processign(self.link),
                            (lang, 'en')
                        )
                name_for_file = f"{self.name_of_video}(subtitles)"
                path = r'%s' % join(
                    pr.settings['directories']['subtitles'], name_for_file) + ".txt"
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
            except TranscriptsDisabled as e:
                print(f"Subtitles are disabled for this video (link: {self.link})")
                pass #TODO (TRANSCRIPTION ERROR!)

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
        try:
            if not self.currentlyDownloading:
                self.currentlyDownloading = True
                Thread(
                    target=self._download_video_or_audio, daemon=True
                ).start()
        except IncompleteRead:
            print('connection lost')
            self.currentlyDownloading = False
            self.download_video()

    @pyqtSlot(str)
    def calculateSize(self, quality) -> None:
        if quality in self.videoSizes:
            self.sizeText.setText(
                f'Estimated size: {translateSize(self.videoSizes[quality])}')

    def populateResolutions(self, items) -> None:
        self.qualityInput.clear()
        self.qualityInput.addItems(items)
        self.qualityInput.setCurrentText('720p')

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
    QApplication.instance().login = 'N1qro'

    window = DownloadPage()
    window.show()
    sys.exit(app.exec_())
