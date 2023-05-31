import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import json
import argparse
from urllib.parse import urljoin


URL = 'https://tululu.org'


def read_args(page_count):
    text = 'Программа для скачивания книг с сайта https://tululu.org из командной строки'
    parser = argparse.ArgumentParser(description=text)
    text = 'Задайте первую страницу сайта c книгами'
    parser.add_argument('--start_page', type=int, default=1, help=text)
    text = 'Задайте последнюю страницу сайта  c книгами'
    parser.add_argument('--end_page', type=int, default=page_count, help=text)
    text = 'Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.'
    parser.add_argument('--dest_folder', default='books_folder', help=text)
    text = 'Не скачивать картинки'
    parser.add_argument('--skip_imgs', action='store_true',
                        default=False, help=text)
    text = 'Не скачивать книги'
    parser.add_argument('--skip_txt', action='store_true',
                        default=False, help=text)
    text = 'Укажите свой путь к *.json файлу с результатами'
    parser.add_argument('--json_path', default='', help=text)
    args = parser.parse_args()
    return args


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, dest_folder, payload):
    folder = f'{dest_folder}/books'
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_img(url, filename, dest_folder):
    folder = f'{dest_folder}/images'
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def save_descriptions(descriptions, dest_folder, json_path):
    folder = f'{dest_folder}/{json_path}'
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, 'описание_книг.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=2)


def parse_book_page(book_id, soup, directory='books/'):
    title_tag = soup.body.table.h1
    title, author = title_tag.text.split('::')
    title, author = title.strip(), author.strip()
    images_selector = '.tabs #content .d_book .bookimage a img'
    img_url = soup.select_one(images_selector)['src']
    description_selector = '.tabs tr td.ow_px_td #content .d_book'
    description = soup.select(description_selector)[2].text
    genres_selector = '.tabs tr td.ow_px_td #content span.d_book a'
    genres_tag = soup.select(genres_selector)
    genres = [genre.text for genre in genres_tag if genres_tag]
    comments_selector = '.tabs tr td.ow_px_td #content .texts span'
    comments_tag = soup.select(comments_selector)
    comments = [comment.text for comment in comments_tag if comments_tag]
    book = {'book_id': book_id,
            'author': author,
            'title': title,
            'genres': genres,
            'description': description,
            'genres': genres,
            'comments': comments,
            'img_url': img_url,
            'image_src': f'images/{img_url.split("/")[2]}',
            'book_path': f'books/{book_id}.{title}.txt'
            }
    return book


def get_page_count(category_url):
    response = requests.get(category_url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return int(soup.select('a.npage')[-1].text)


def get_books_ids(category_url, page):
    book_ids = []
    page_url = urljoin(category_url, str(page))
    response = requests.get(page_url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    a_tags = soup.select('#content .bookimage a')
    for a_tag in a_tags:
        book_id = a_tag['href'].replace('/', '').replace('b', '')
        book_ids.append(book_id)
    return book_ids


def main():
    # Категория: научная фантастика
    category = '/l55/'
    category_url = urljoin(URL, category)
    try:
        page_count = get_page_count(category_url)
    except requests.HTTPError:
        print('Страница отсутствует')
        exit()
    args = read_args(page_count)
    message = ''
    start_page, end_page = args.start_page, args.end_page
    if end_page > page_count:
        end_page = page_count
    book_ids = []
    for page in range(start_page, end_page + 1):
        while True:
            try:
                book_ids += get_books_ids(category_url, page)
                message = f'Получены id книг с {page} страницы сайта'
            except requests.HTTPError:
                print('Страница отсутствует')
            except requests.exceptions.ConnectionError:
                if message == 'Нет соединения':
                    time.sleep(60)
                else:
                    message = 'Нет соединения'
                print(message)
                continue
            print(message)
            break
    dest_folder = args.dest_folder
    skip_imgs, skip_txt = args.skip_imgs, args.skip_txt
    json_path = args.json_path
    descriptions = []
    os.makedirs(dest_folder, exist_ok=True)
    for book_id in book_ids:
        payload = {'id': book_id}
        title_url = urljoin(URL, f'b{book_id}/')
        file_url = urljoin(URL, 'txt.php')
        while True:
            try:
                response = requests.get(title_url)
                response.raise_for_status()
                check_for_redirect(response)
                message = f'Страница книги с id = {book_id} существует'
            except requests.HTTPError:
                print('Страница отсутствует')
                break
            except requests.exceptions.ConnectionError:
                if message == 'Нет соединения':
                    time.sleep(60)
                else:
                    message = 'Нет соединения'
                print(message)
                continue
            print(message)
            soup = BeautifulSoup(response.text, 'lxml')
            book = parse_book_page(book_id, soup)
            full_img_url = urljoin(title_url, book['img_url'])
            try:
                if not skip_txt:
                    filename = f'{book["book_id"]}.{sanitize_filename(book["title"])}.txt'
                    download_txt(file_url, filename, dest_folder, payload)
                if not skip_imgs:
                    filename = f'{book["image_src"].split("/")[1]}'
                    download_img(full_img_url, filename, dest_folder)
                message = f'Книга: {book["title"]}'
                descriptions.append(book)
            except requests.HTTPError:
                print('Файл книги отсутствует')
                break
            except requests.exceptions.ConnectionError:
                if message == 'Нет соединения':
                    time.sleep(60)
                else:
                    message = 'Нет соединения'
                print(message)
                continue
            print(message)
            break
    save_descriptions(descriptions, dest_folder, json_path)


if __name__ == '__main__':
    main()
