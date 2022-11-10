import os
import pickle
import shutil
import sqlite3
import hashlib
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


class Database:
    def __init__(self, dbName: str) -> None:
        self.dbName = dbName

    def __enter__(self):
        self.db = sqlite3.connect(self.dbName)
        self.cursor = self.db.cursor()
        return self

    def add(self, email: str, login: str, password: str) -> None:
        """
            Adds an entry to the database. Given password should be plaintext
            it will be hashed, salted and safely stored in the table without any
            vulnerability issues.
        """
        key, salt = self.hashPlaintext(password)

        query = f"""
            INSERT INTO Entries ('login', 'password', 'email') 
            VALUES ('{login}', '{key.hex() + salt.hex()}', '{email}')
        """

        self.cursor.execute(query)
        self.db.commit()

    def remove(self, email='', login=''):
        query = """
            DELETE FROM Entries
            WHERE login = (?)
            OR email = (?)
        """

        self.cursor.execute(query, (login, email))
        self.db.commit()

    def check(self, email='', login='') -> bool:
        """
            Checks if user with given email or login already exists
            in the database. Returns True/False depending on result.
        """
        user = self.cursor.execute(f"""
            SELECT login, email
            FROM Entries
            WHERE email = "{email}" OR login = "{login}"
        """).fetchone()

        return bool(user)

    def hashPlaintext(self, plaintext: str, salt=None):
        """
            Uses certain algorithms to hash and salt plaintexts such as password
            to store them safely in the database.
        """
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac(
            'sha256', plaintext.encode('utf-8'), salt, 100000)
        return key, salt

    def login(self, password: str, email='', login='') -> str:
        """
            Tries to fetch the userdata from the db, checking for data validity.
            Returns specialized str to indicate the result.
        """
        retrievedPass = self.cursor.execute(f"""
            SELECT password, login
            FROM Entries
            WHERE email = "{email}" OR login = "{login}"
        """).fetchone()

        if retrievedPass:
            key = retrievedPass[0][:64]
            salt = bytes.fromhex(retrievedPass[0][64:])
            
            if self.hashPlaintext(password, salt)[0].hex() == key:
                return True, retrievedPass[1]
            else:
                return False, 'wrong password'
        else:
            return False, 'not found'

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.db.close()
        if exc_val:
            raise


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

        with open('profiles.pkl', 'wb') as profileFile:
            pickle.dump(allProfiles, profileFile, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def loadProfiles() -> dict:
        profiles = dict()
        if os.path.exists('profiles.pkl') and os.path.getsize('profiles.pkl'):
            with open('profiles.pkl', 'rb') as profileFile:
                data = pickle.load(profileFile)
                for userlogin, profile in data.items():
                    if type(profile).__name__ == "Profile" and userlogin != 'recentProfile':
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

    @classmethod
    def removeUserData(cls, login: str | Profile, removeDBEntry=True) -> None:
        """
            Fully deletes the home directory of the profile.
            Erases profile entry from profiles.pkl
            And sets the recentProfile to None if the last entered profile
            was this exact profile.
        """
        allProfiles = cls.loadProfiles()

        if isinstance(login, str):
            assert login in allProfiles
            deletingProfile = allProfiles[login]
        elif isinstance(login, Profile):
            assert login in allProfiles.values()
            deletingProfile = login

        # Remove the home directory
        homePath = deletingProfile.settings['directories']['home']
        shutil.rmtree(homePath, ignore_errors=True)

        # Clear the recentProfile data
        recentProfile = allProfiles.get('recentProfile', None)
        if recentProfile and recentProfile == deletingProfile:
            del allProfiles['recentProfile']
            del allProfiles['lastLoginDate']
        del allProfiles[deletingProfile.userLogin]

        # Save changes
        with open('profiles.pkl', 'wb') as f:
            pickle.dump(allProfiles, f, pickle.HIGHEST_PROTOCOL)

        if removeDBEntry:
            with Database('Accounts.db') as db:
                db.remove(login=deletingProfile.userLogin)

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

