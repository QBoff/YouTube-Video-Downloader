from pytube import YouTube


def download_video(path_to_save, link):
    try:
        yt = YouTube(link)
    except:
        # it's time for Qt part
        print("Не удалось нати такую ссылку :( ")

    mp4video = yt.streams.filter(file_extension="mp4").get_by_resolution("720p")  # filter out all the files with mp4 extension
    # I should add true name of thid video

    try:
        mp4video.download(path_to_save)
    except:
        print("Downloading error")

    return "ok"


path_for_save = "downloaded_video/"

# in future you will chode it by yourself
url_link = "https://www.youtube.com/watch?v=Y2ptUZb-608"

print(download_video(path_for_save, url_link))
