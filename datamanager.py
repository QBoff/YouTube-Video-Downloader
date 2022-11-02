import os
import pickle
from dataclasses import dataclass
from enum import Enum
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
    localization: str
    downloadDate: datetime = datetime.now()


class Manager:
    dictionaryKeys = 'Videos', 'Audio', 'Subtitles'

    def __init__(self, userLogin) -> None:
        if not os.path.exists(userLogin):
            raise ValueError('User directory do not exist')
        self.userLogin = userLogin
        self.filePath = os.path.join(userLogin, 'hashmap.pkl')

    @classmethod
    def createUserDirectory(cls, userLogin) -> None:
        if os.path.exists(userLogin):
            raise FileExistsError('User directory already initialized')
        os.makedirs(userLogin)
        emptyDict = {key: list() for key in cls.dictionaryKeys}
        with open(os.path.join(userLogin, 'hashmap.pkl'), 'wb') as dataFile:
            pickle.dump(emptyDict, dataFile, pickle.HIGHEST_PROTOCOL)

    def addVideo(self, video) -> None:
        if not isinstance(video, Video):
            raise ValueError('Passed argument is not a video')
        self.data['Videos'].append(video)

    def addAudio(self, audio) -> None:
        if not isinstance(audio, Audio):
            raise ValueError('Passed argument is not an audio')
        self.data['Audio'].append(audio)

    def addSubtitles(self, subtitles) -> None:
        if not isinstance(subtitles, Subtitles):
            raise ValueError('Passed argument is not subtitles')
        self.data['Subtitles'].append(subtitles)

    def getVideos(self, /, sortKey=None, filterBy=None) -> list:
        videos = self.data['Videos']
        if filterBy is not None:
            videos = list(filter(filterBy, videos))
        if sortKey is not None:
            videos.sort(key=sortKey)
        return videos

    def getAudio(self, /, sortKey=None, filterBy=None) -> list:
        audio = self.data['Audio']
        if filterBy is not None:
            audio = filter(filterBy, audio)
        if sortKey is not None:
            audio.sort(key=sortKey)
        return audio

    def __enter__(self):
        if not os.path.exists(self.filePath):
            raise FileNotFoundError("Couldn't find the hashmap")
        with open(self.filePath, 'rb') as dataFile:
            self.data = pickle.load(dataFile)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        with open(self.filePath, 'wb') as dataFile:
            pickle.dump(self.data, dataFile, pickle.HIGHEST_PROTOCOL)
        if exc_val:
            raise