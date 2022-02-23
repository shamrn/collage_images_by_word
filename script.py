import io
import os

import requests
from PIL import Image
from bs4 import BeautifulSoup

URL = 'https://ru.depositphotos.com/stock-photos/%s.html'
HEADERS = {
    ''
}

COUNT_IMAGE = 4
IMAGE_PATH = './images/'
FORMAT_IMAGE = '.jpg'
IMAGE_SIZE = (300, 300)

WORDS_PATH = './words'
FAIL_LOAD_PATH = './fail_load'
WORDS = list()


def load_images(images_urls: list, word: str) -> list:
    """Uploading an image via a link and saving"""

    global IMAGE_PATH

    paths_images = []

    for iter_, url in enumerate(images_urls, 1):
        image = requests.get(url)
        file_path = f'{IMAGE_PATH}{word}-{iter_}{FORMAT_IMAGE}'

        image = Image.open(io.BytesIO(image.content))
        image_res = image.resize(IMAGE_SIZE, Image.ANTIALIAS)
        image_res.save(file_path)

        paths_images.append(file_path)

    return paths_images


def delete_images(paths_images: list):

    for path_image in paths_images:
        os.remove(path_image, dir_fd=None)


def make_image_collage(paths_images: list, word: str):
    """Make a raw image and insert four images for the collage"""

    raw_image = Image.new('RGB', (600, 600))
    open_images = [Image.open(path) for path in paths_images]

    insert_points = [(0, 0), (0, 300), (300, 0), (300, 300)]

    for open_image, insert_point in zip(open_images, insert_points):
        raw_image.paste(open_image, insert_point)

    raw_image.save(IMAGE_PATH + word + FORMAT_IMAGE)


def get_image_url(html_data: 'BeautifulSoup') -> list:
    """Parsing url image by html"""

    global COUNT_IMAGE

    images_urls = list()
    items = html_data.findAll('a', class_='file-container__link')

    for item in items[:COUNT_IMAGE]:
        image_url = item.find('source')['srcset']
        images_urls.append(image_url.split(',')[0])
    return images_urls


def get_html(word: str) -> 'BeautifulSoup':
    """Parsing html by words"""

    global URL

    response = requests.get(URL % word, HEADERS)
    html_data = BeautifulSoup(response.content, 'html.parser')

    return html_data


def parse_words(file: str):
    """Parsing words with txt file"""

    with open(file, encoding='utf-8') as words:
        for word in words:
            if '[' in word:
                word = word.split('[')
            elif '(' in word:
                word = word.split('(')

            WORDS.append(word)


def save_fail_load_image(word: str, path_file: str):
    with open(file=path_file, mode='a', encoding='utf-8') as open_file:
        open_file.write(f'{word}\n')


parse_words(WORDS_PATH)
for word in WORDS:

    print(f'Word: {word}', end='')

    try:
        html_data = get_html(word)
        images_urls = get_image_url(html_data)
        paths_images = load_images(word=word, images_urls=images_urls)
        make_image_collage(word=word, paths_images=paths_images)
        delete_images(paths_images)

        print(' - success')

    except Exception as exc:
        save_fail_load_image(word=word, path_file=FAIL_LOAD_PATH)

        print(f' - error: {exc}')

        break