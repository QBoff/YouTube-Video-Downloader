from enum import Enum as __Enum

# EXCEPTIONS



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
