import requests
from bs4 import BeautifulSoup
PREVIEW_FILE_NAME = 'temp.jpg'


def downloadPreview(url):
    response = requests.get(url)
    if response.status_code == 200:
        with open(PREVIEW_FILE_NAME, 'wb') as file:
            file.write(response.content)
        return PREVIEW_FILE_NAME


def getVideoInfo(url) -> dict:
    """
        Возвращает название, имя автора и превью видео.\n
        Ключи <title, channel, thumbnail>
        rtype: dict[str]

        В случае неудачи не выбрасывает исключение и возвращает FALSE
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('meta', {'property': 'og:title'})['content']
        channelName = soup.find('link', {'itemprop': 'name'})['content']
        previewLink = soup.find('meta', {'property': 'og:image'})['content']
        preview = downloadPreview(previewLink)

        return {'title': title, 'channel': channelName, 'thumbnail': preview}
    except TypeError:
        return False
