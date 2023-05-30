# Парсинг сайта  [Бесплатной бибилиотеки](https://tululu.org) и скачивание книг из категории 'Научная фантастика'
## Использование скрипта

```
python3 ./parse_tululu_category.py -h
```
```
usage: parse_tululu_category.py [-h] [--start_page START_PAGE] [--end_page END_PAGE] [--dest_folder DEST_FOLDER]
                                [--skip_imgs] [--skip_txt] [--all_book] [--json_path JSON_PATH]

Программа для скачивания книг с сайта https://tululu.org из командной строки

options:
  -h, --help            show this help message and exit
  --start_page START_PAGE
                        Задайте первую страницу сайта c книгами
  --end_page END_PAGE   Задайте последнюю страницу сайта c книгами
  --dest_folder DEST_FOLDER
                        Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.
  --skip_imgs           Не скачивать картинки
  --skip_txt            Не скачивать книги
  --all_book            Скачать все книги из этой категории
  --json_path JSON_PATH
                        Укажите свой путь к *.json файлу с результатами

```

По умолчанию заданы следующие параметры `start_page = 1`, `end_page = 1`, `skip_imgs = False`, `skip_txt = False`, `all_book = False`,
`dest_folder = 'books_folder'`, `json_path = ''`.
Параметр `all_book` имеет приоритет перед параметром `end_page` - будут скачиваться книги до последней страницы сайта.
Программа парсит сайт, для получения списка книг, а потом каждую веб страницу книги и сохраняет книгу, ее описание, жанр, комментарии, обложку. 
В директории с программой создаются (если они отсутсвовали) каталоги books, куда скачиваются книги,  и images, где сохраняются обложки книг.
В отдельный файл формата json сохраняются описания книг.


## Как установить
Python3 должен быть установлен. Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Рекомендуется использовать [virtualenv/venv](https://virtualenv.pypa.io/en/latest/index.html) для изоляции проекта.
## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
