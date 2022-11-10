import os
import pickle
from dataclasses import dataclass
from PyQt5.QtWidgets import QApplication
from datetime import datetime
from datetime import date

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

            'preferredQuality': '1080p',
            'optimizeFor': 'Video download'
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
            try:
                os.makedirs(dirPath)
            except FileExistsError:
                continue

        print(allProfiles)
        with open('profiles.pkl', 'wb') as profileFile:
            pickle.dump(allProfiles, profileFile, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def loadProfiles() -> dict:
        profiles = dict()
        if os.path.exists('profiles.pkl') and os.path.getsize('profiles.pkl'):
            with open('profiles.pkl', 'rb') as profileFile:
                data = pickle.load(profileFile)
                for userlogin, profile in data.items():
                    if type(profile).__name__ == "Profile":
                        profiles[userlogin] = profile
                return profiles
        return profiles

    @staticmethod
    def getRecentProfile() -> tuple:
        if os.path.exists('profiles.pkl') and os.path.getsize('profiles.pkl'):
            with open('profiles.pkl', 'rb') as profiles:
                data = pickle.load(profiles)
                recentProfile = data.get('recentProfile', None)
                lastEntry = data.get('lastLoginDate', None)
                return recentProfile, lastEntry
        return None, None

    @classmethod
    def getActiveUser(cls) -> Profile:
        try:
            login = QApplication.instance().login
            return cls.loadProfiles()[login]
        except Exception:
            return None

    @staticmethod
    def setRecentProfile(login: str | Profile) -> None:
        with open('profiles.pkl', 'rb') as f:
            profiles = pickle.load(f)

        lastLoginDate = date.today()
        if isinstance(login, str):
            profiles['recentProfile'] = profiles[login]
        elif isinstance(login, Profile):
            profiles['recentProfile'] = login
        else:
            raise TypeError('Not a "str" or "profile" like object.')
        profiles['lastLoginDate'] = lastLoginDate

        with open('profiles.pkl', 'wb') as f:
            pickle.dump(profiles, f, pickle.HIGHEST_PROTOCOL)

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

if __name__ == "__main__":
    profiles = Manager.loadProfiles()
    recentProfile = Manager.getRecentProfile()

    # with open('profiles.pkl', 'rb') as f:
    #     print(pickle.load(f))

    print(profiles)
    #print(recentProfile)