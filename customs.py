from enum import Enum as __Enum


# EXCEPTIONS
class AuthError:
    pass


class RegisterError:
    pass


class InvalidLogin(AuthError):
    def __str__(self):
        return 'Учётной записи не существует'


class InvalidPassword(AuthError):
    def __str__(self):
        return 'Неверный пароль'


class PasswordFormat(RegisterError):
    def __str__(self):
        return 'Пароль должен состоять минимум из 8 цифр, иметь хотя бы 1 заглавную, строчную буквы и 1 цифру'


class EmailFormat(RegisterError):
    def __str__(self):
        return 'Email не распознан.'


class WrongSecondPassword(RegisterError):
    def __str__(self):
        return 'Пароли не совпадают'


class LoginAlreadyTaken(RegisterError):
    def __str__(self):
        return 'Данный логин уже используется'


class EmailAlreadyTaken(RegisterError):
    def __str__(self):
        return 'Email уже зарегистрирован. Восстановить пароль можно по кнопке на странице входа'

# ENUMS


class qTypes(__Enum):
    HighestQuality = '1440p'
    FullHD = '1080p'
    HD = '720p'
    DVD = '480p'
    LowestQuality = '360p'

    HighestBitrate = '256kb/s'
    BetterMedium = '192kb/s'
    Medium = '160kb/s'
    LowestBitrate = '128kb/s'


class SortCategory(__Enum):
    pass


class VideoType(__Enum):
    pass


if __name__ == '__main__':
    print(qTypes.HighestQuality.name)
    print(qTypes.HighestQuality.value)
