import sys
from pytube import YouTube

sys.path.append("./")
from customs import qTypes


def download_video(
    link,
    path_to_save="downloaded_video",
    extension="mp4",
    resolution=qTypes.HD.value
) -> str:

    try:
        yt = YouTube(link)
    except:
        # it's time for Qt part
        print("Не удалось нати такую ссылку :( ")

    mp4video = yt.streams.filter(file_extension=extension).get_by_resolution(
        resolution)  # filter out all the files with mp4 extension and 720p resolution

    try:
        mp4video.download(path_to_save)
    except:
        print("Downloading error")

    return "ok"


# path_for_save = "downloaded_video/"

# url_link = "https://www.youtube.com/watch?v=Y2ptUZb-608"

# print(download_video(url_link, path_for_save))
