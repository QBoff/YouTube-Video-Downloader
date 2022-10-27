import sys
from pytube import YouTube
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow

# sys.path.append("./")
# from customs import qTypes

class DownloadPage(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("uis/downloadPage.ui", self)
        # text += self.text1.text()


    # app = QApplication(sys.argv)
    # dw = DownloadPage()
    # print(dw.qualityInput.currentText())

    def download_video(
        self,
        path_to_save="downloaded_video",
    ) -> str:

        link = self.urlInput.text()
        resolution = self.qualityInput.currentText()  # get resolution from Interface
        extension = self.comboBox_2.currentText()  # get extension from Interface
        
        try:
            yt = YouTube(link)
        except:
            # it's time for Qt part
            print("Не удалось нати такую ссылку :( ")

        # !!!!!!
        video_size = yt.streams.filter(file_extension=extension).get_by_resolution(
            resolution).filesize_approx / 1024 / 1024 / 1024  # get the file size in gb
        # !!!!!!
        self.alert.setText(str(round(video_size, 5)))

        mp4video = yt.streams.filter(file_extension=extension).get_by_resolution(
            resolution)  # filter out all the files with mp4 extension and 720p resolution

        try:
            mp4video.download(path_to_save)
        except:
            print("Downloading error")

        return "ok"


    # dw.downloadButton.clicked.connect(lambda: download_video(dw.urlInput.text()))


# path_for_save = "downloaded_video/"

# url_link = "https://www.youtube.com/watch?v=Y2ptUZb-608"

# print(download_video(url_link, path_for_save))

# print(dw.text1.text())

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
