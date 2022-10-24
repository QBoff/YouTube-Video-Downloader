from youtube_transcript_api import YouTubeTranscriptApi


def url_processign(url) -> str:
    return "=".join(url.split('=')[1:])


# print(url_processign("https://www.youtube.com/watch?v=cdZZpaB2kDM"))
data = YouTubeTranscriptApi.get_transcript(
    url_processign("https://www.youtube.com/watch?v=cdZZpaB2kDM"),
    ('en', 'ru')
)

with open("download_video/subtitles/subtitles_from_video.txt", "w", encoding="utf-8") as file:
    for item in data:
        # if item starts with [ it's not our stuff :)
        if item["text"][0] != '[':
            file.write(item["text"] + "\n")

# print(data)
