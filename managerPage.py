import sys
from os.path import join, getsize, isfile
from os import startfile, listdir

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QSizeGrip, QLabel, QSizePolicy, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import uic
from datamanager import Manager, Video
from downloadPage import translateSize

class AspectWidget(QWidget):
    '''
    A widget that maintains its aspect ratio.
    '''
    def __init__(self, *args, ratio=4/3, **kwargs):
        super().__init__(*args, **kwargs)
        self.ratio = ratio
        self.adjusted_to_size = (-1, -1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))

    def resizeEvent(self, event):
        size = event.size()
        if size == self.adjusted_to_size:
            # Avoid infinite recursion. I suspect Qt does this already,
            # but it's best to be safe.
            return
        self.adjusted_to_size = size

        full_width = size.width()
        full_height = size.height()
        width = min(full_width, full_height * self.ratio)
        height = min(full_height, full_width / self.ratio)

        h_margin = round((full_width - width) / 2)
        v_margin = round((full_height - height) / 2)

        self.setContentsMargins(h_margin, v_margin, h_margin, v_margin)


class VideoPreview(QWidget):
    def __init__(self, *args, video, **kwargs):
        super().__init__(*args, **kwargs)
        self.videoObj = video
        self.initUI()
    
    def initUI(self):
        uic.loadUi(join('uis', 'videoWidgetItem.ui'), self)
        # previewRatioHolder = QWidget(self.previewContainer)
        self.previewLabel.setFixedSize(267, 150)
        previewHolder = QLabel(self.previewLabel)
        previewHolder.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        previewImage = QImage.fromData(self.videoObj.preview)
        self.videoName.setText(self.videoObj.title)

        self.playButton.clicked.connect(lambda: startfile(self.videoObj.videoPath))
        self.deleteButton.clicked.connect(self.deleteVideo)

        width = self.previewLabel.width()
        height = self.previewLabel.height()
        previewHolder.setPixmap(QPixmap.fromImage(previewImage).scaled(width, height))

    def deleteVideo(self):
        if True:  # TODO CHECK FOR USERSETTINGS!
            msgBox = QMessageBox()
            msgBox.setWindowTitle('Confirm deleting video')
            msgBox.setText("Are you sure you want to delete the video?")
            msgBox.setInformativeText("You can disable this message in your settings")
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)

            def afterClick(btn):
                operation = btn.text().replace('&', '')
                if operation == 'Yes':
                    userLogin = Manager.getActiveUser().userLogin
                    with Manager(userLogin) as folder:
                        folder.removeVideo(self.videoObj)
                    print('deleting the video.')
                    pass

            msgBox.buttonClicked.connect(afterClick)
            msgBox.exec_()
        else:
            userLogin = Manager.getActiveUser().userLogin
            with Manager(userLogin) as folder:
                folder.removeVideo(self.videoObj)

class ManagerPage(QMainWindow):
    sortingAttributes = {
        'Title': 'title',
        'Author': 'author',
        'Download date': 'downloadDate',
    }

    def __init__(self) -> None:
        super().__init__()
        self.videoTemplates = list()
        self.initUI()

    def initUI(self) -> None:
        uic.loadUi(join('uis', 'videoManager.ui'), self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        videoPath = Manager.getActiveUser().settings['directories']['video']
        totalSize = sum(getsize(f) for f in listdir(videoPath) if isfile(f))
        translatedSize = translateSize(totalSize)
        self.spaceLabel.setText(f'space taken: {translatedSize}')

        self.exit.clicked.connect(
            lambda: sys.exit(QApplication.instance().exit()))
        self.minimize.clicked.connect(lambda: self.showMinimized())
        self.controlPanel.mouseMoveEvent = self.moveWindow
        self.makeConnections()

        self.gripSize = 16
        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

    def makeConnections(self):
        self.sortingButton.clicked.connect(self.onSortButtonClick)
        self.showingButton.clicked.connect(self.onShowButtonClick)
        self.orderButton.clicked.connect(self.onOrderButtonClick)

    def onSortButtonClick(self):
        variants = ('Title', 'Author', 'Download date')

        currentIndex = variants.index(self.sortingButton.text()[9:])
        self.sortingButton.setText(f'Sort by: {variants[(currentIndex + 1) % 3]}')
        self.sortTemplates()

    def onShowButtonClick(self):
        variants = ('All', 'Favorites')

        currentIndex = variants.index(self.showingButton.text()[6:])
        self.showingButton.setText(f'Show: {variants[(currentIndex + 1) % 2]}')
        self.sortTemplates()

    def onOrderButtonClick(self):
        variants = ('Ascending', 'Descending')
        currentIndex = variants.index(self.orderButton.text()[:-6])
        self.orderButton.setText(f'{variants[(currentIndex + 1) % 2]} order')
        self.sortTemplates()

    def loadTemplates(self):
        userLogin = Manager.getActiveUser().userLogin
        with Manager(userLogin) as folder:
            videos = folder.getVideos()
        v_layout= QVBoxLayout(self.scrollContents)

        for video in videos:
            item = VideoPreview(self.scrollContents, video=video)
            v_layout.addWidget(item)
            self.videoTemplates.append(item)

    def updateTemplates(self, videos):
        for video in videos:
            item = VideoPreview(window.scrollContents, video=video)
            v_layout.addWidget(item)
            self.videoTemplates.append(item)

    def sortTemplates(self):
        showAll = self.showingButton.text()[6:] == 'All'
        order = self.orderButton.text()[:-6]
        sort = self.sortingButton.text()[9:]

        sort = self.sortingAttributes[sort]
        order = order == 'Ascending'

        def sortFunction(video):
            return getattr(video, sort)

        self.videoTemplates.sort(key=sortFunction, reverse=order)


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


if __name__ == "__main__":
    # folder.getVideos()[2, 3] - Нормально работающие видео.
    from youtube import downloadPreview, getYTSession
    from os.path import join

    with Manager('N1qro') as folder:
        # vid1 = folder.getVideos()[3]
        vid2 = folder.getVideos()[2]

    app = QApplication(sys.argv)
    QApplication.instance().login = 'N1qro'

    window = ManagerPage()
    v_layout= QVBoxLayout(window.scrollContents)
    # for i in range(20):  #TODO OVERLOADED SCROLL AREA TODO
    #     template1 = VideoPreview(window.scrollContents, video=vid1)
    #     v_layout.addWidget(template1)
    # template1 = VideoPreview(window.scrollContents, video=vid1)
    template2 = VideoPreview(video=vid2)
    # v_layout.addWidget(template1)
    v_layout.addWidget(template2)


    window.show()
    sys.exit(app.exec_())
    
    #session = getYTSession('https://www.youtube.com/watch?v=IapQMgMbDLM')
    # session = getYTSession('https://www.youtube.com/watch?v=czGZyBlikKI')
    # previewInBytes = downloadPreview(session.thumbnail_url)

    # author = session.author
    # title = session.title
    # path = join('N1qro', 'Videos', title + '.mp4')
    # video1 = Video(path, previewInBytes, title, author)

    # with Manager('N1qro') as folder:
    #     folder.addVideo(video1)

    # app = QApplication(sys.argv)
    # with Manager('N1qro') as folder:
    #     video = folder.getVideos()[0]
    #     video2 = folder.getVideos()[1]

    # window = ManagerPage()
    # v_layout= QVBoxLayout(window.contents)
    # template1 = VideoPreview(window.contents, video=video)
    # template2 = VideoPreview(window.contents, video=video2)
    # v_layout.addWidget(template1)
    # v_layout.addWidget(window.pushButton)
    # v_layout.addWidget(template2)
    # v_layout.addWidget(window.pushButton_2)

    # window.show()
    # sys.exit(app.exec_())
