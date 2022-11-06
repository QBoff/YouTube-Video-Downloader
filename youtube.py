import requests
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError


def downloadPreview(previewLink: str) -> bytes:
    previewLink = previewLink[:previewLink.rfind('/') + 1] + 'maxresdefault.jpg' 

    response = requests.get(previewLink)
    if response.status_code == 200:
        return response.content


def getYTSession(url: str) -> YouTube | None:
    try:
        session = YouTube(url)
        assert session.author != 'unknown'
    except (VideoUnavailable, RegexMatchError, AssertionError):
        return None
    return session