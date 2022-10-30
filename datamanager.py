import os
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Video:
    videoPath: str
    previewPath: str
    title: str
    author: str
    uploadDate: datetime
    downloadDate: datetime = datetime.now()


@dataclass(frozen=True)
class Audio:
    audioPath: str
    title: str
    author: str
    downloadDate: datetime = datetime.now()


@dataclass(frozen=True)
class Subtitles:
    associatedVideo: Video
    downloadDate: datetime = datetime.now()


class Manager:
    def __init__(self, userLogin) -> None:
        if not os.path.exists(userLogin):
            raise ValueError('User directory do not exist')
        self.userLogin = userLogin

    @staticmethod
    def createUserDirectory(userLogin) -> None:
        if not os.path.exists(userLogin):
            os.makedirs(userLogin)

    def addVideo(self, video) -> None:
        pass

    def addAudio(self, audio) -> None:
        pass

    def addSubtitles(self, subtitles) -> None:
        pass

    def getVideos(self, sortKey=None) -> list:
        pass

    def getAudio(self, sortKey=None) -> list:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val:
            raise


# if __name__ == '__main__':
#     with Manager('N1qro') as folder:
#         folder.getVideos()
