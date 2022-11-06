import requests
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError


def downloadPreview(previewLink: str) -> bytes:
    rSlashIndex = previewLink.rfind('/')
    previewLink = previewLink[:rSlashIndex + 1] + 'maxresdefault.jpg' 

    response = requests.get(previewLink)
    if 'x10JFIF' in response:  # In case video doesn't have max res image
        newPreviewLink = previewLink[:rSlashIndex + 1] + 'hqdefault.jpg'
        response = requests.get(newPreviewLink)
    if response.status_code == 200:
        return response.content


def getYTSession(url: str) -> YouTube | None:
    try:
        session = YouTube(url)
        assert session.author != 'unknown'
    except (VideoUnavailable, RegexMatchError, AssertionError):
        return None
    return session