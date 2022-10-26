from youtube_transcript_api import YouTubeTranscriptApi


def url_processign(url) -> str:
    return "=".join(url.split('=')[1:])


# print(url_processign("https://www.youtube.com/watch?v=cdZZpaB2kDM"))
def download_subtitles(url, name_for_file="sub_file") -> None:
    data = YouTubeTranscriptApi.get_transcript(
        url_processign(url),
        ('en', 'ru')
    )

    with open(f"downloaded_subtitles/{name_for_file}.txt", "w", encoding="utf-8") as file:
        for item in data:
            # if item starts with [ it's not our stuff :)
            if item["text"][0] != '[':
                file.write(item["text"] + "\n")
    
    return "Субтитры были скачаны."

# print(data)
# download_subtitles("https://www.youtube.com/watch?v=cdZZpaB2kDM")
