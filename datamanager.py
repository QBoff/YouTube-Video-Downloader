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


class Profile:
    def __init__(self, userLogin) -> None:
        self.userLogin = userLogin
        self.videos = list()
        self.audio = list()
        self.subtitles = list()
        self.settings = self.DefaultSettings(userLogin)

    @staticmethod
    def DefaultSettings(userLogin) -> dict:
        settings = {
            'directories': {
                'home': userLogin,
                'video': os.path.join(userLogin, 'Videos'),
                'audio': os.path.join(userLogin, 'Audio'),
                'subtitles': os.path.join(userLogin, 'Subtitles')
            },

            'preferredQuality': '1080p'
        }

        return settings


class Manager:
    dictionaryKeys = 'Videos', 'Audio', 'Subtitles'

    def __init__(self, userLogin) -> None:
        if not os.path.exists(userLogin):
            raise ValueError('User directory do not exist')
        self.allProfiles = self.loadProfiles()
        self.userLogin = userLogin

    @classmethod
    def createUserDirectory(cls, userLogin: str) -> None:
        allProfiles = cls.loadProfiles()
        newProfile = Profile(userLogin)

        allProfiles[userLogin] = newProfile
        for dirPath in newProfile.settings['directories'].values():
            os.makedirs(dirPath)

        with open('profiles.pkl', 'wb') as profileFile:
            pickle.dump(allProfiles, profileFile, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def loadProfiles(cls) -> list:
        if os.path.exists('profiles.pkl'):
            with open('profiles.pkl', 'rb') as profiles:
                return pickle.load(profiles)
        return dict()

    def addVideo(self, video) -> None:
        if not isinstance(video, Video):
            raise ValueError('Passed argument is not a video')
        self.activeProfile.videos.append(video)

    def addAudio(self, audio) -> None:
        if not isinstance(audio, Audio):
            raise ValueError('Passed argument is not an audio')
        self.activeProfile.audio.append(audio)

    def addSubtitles(self, subtitles) -> None:
        if not isinstance(subtitles, Subtitles):
            raise ValueError('Passed argument is not subtitles')
        self.activeProfile.subtitles.append(subtitles)

    def getVideos(self, *, sortKey=None, filterBy=None) -> list:
        videos = self.activeProfile.videos
        if filterBy is not None:
            videos = list(filter(filterBy, videos))
        if sortKey is not None:
            videos.sort(key=sortKey)
        return videos

    def getAudio(self, *, sortKey=None, filterBy=None) -> list:
        audio = self.activeProfile.audio
        if filterBy is not None:
            audio = filter(filterBy, audio)
        if sortKey is not None:
            audio.sort(key=sortKey)
        return audio

    def __enter__(self):
        self.activeProfile: Profile = self.allProfiles[self.userLogin]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.allProfiles[self.userLogin] = self.activeProfile

        with open('profiles.pkl', 'wb') as profiles:
            pickle.dump(self.allProfiles, profiles, pickle.HIGHEST_PROTOCOL)

        if exc_val:
            raise