from enum import Enum as __Enum

# EXCEPTIONS


class AuthError(Exception):
    def __str__(self):
        return self.msg


class RegisterError(Exception):
    def __str__(self):
        return self.msg


class InvalidLogin(AuthError):
    msg = 'Учётной записи не существует'


class InvalidPassword(AuthError):
    msg = 'Неверный пароль'


class PasswordFormat(RegisterError):
    msg = 'Неправильный формат пароля.\nПароль должен состоять минимум из 8 символов\nСреди них должна быть 1 заглавная,\nстрочная буквы и цифра'


class EmailFormat(RegisterError):
    msg = 'Email не распознан.'


class WrongSecondPassword(RegisterError):
    msg = 'Пароли не совпадают'


class LoginAlreadyTaken(RegisterError):
    msg = 'Данный логин уже используется'


class EmailAlreadyTaken(RegisterError):
    msg = 'Email уже зарегистрирован. Восстановить пароль можно по кнопке на странице входа'

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
