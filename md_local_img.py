import os
import re
import random
import string
import urllib.request
import time
import logging

# Создать папку для скачиваемых изображений
class FolderCreator:
    def __init__(self, location = "."):
        self.location = location

    def create_folder(self, name):
        self.name = name
        self.folder = os.path.join(self.location, self.name)
        if not os.path.exists(self.folder):
            #os.mkdir(self.folder)
            os.makedirs(self.folder, exist_ok=True)

# Записать содержимое в файл
class FileWriter:
    def write_file(self, folder_path, filename, filedata):
        self.folder_path = folder_path
        self.filename = filename
        self.filedata = filedata
        with open(os.path.join(self.folder_path, self.filename), "w", encoding="utf-8") as file:
            file.write(self.filedata)

# Скачать изображения по обнаруженными в .md ссылкам в папку
class ImgDownloader:
    def download_images(self, url_dict, folder_path, user_agent):
        self.url_dict = url_dict
        self.folder_path = folder_path
        self.user_agent = user_agent

        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', self.user_agent)]
        urllib.request.install_opener(opener)

        for url, name in self.url_dict.items():
            save_name = os.path.join(self.folder_path, name)

            try:
                urllib.request.urlretrieve(url, save_name)
            except Exception as e:
                logging.exception(f"Ошибка при загрузке {url}")
            time.sleep(random.randint(0,1))

# Открыть и прочитать файл
class FileOpener:
    def open_and_read(self, filename):
        self.filename = filename
        try:
            with open(os.path.join(os.getcwd(), filename), "r", encoding="utf-8") as self.current_opened_file:
                print(f"\n\033[35mОткрываем файл:\033[0m {self.filename}")
                logging.info(f"Открываем файл: {self.filename}\n")
                return self.current_opened_file.read()
        except Exception as e:
            logging.exception(f"Ошибка при открытии файла {self.filename}")

# Ищем url в file_date и создаём словарь из url и имени файла для сохранения
class UrlDictCreator:
    def create(self, regex, file_data, file_name):
        self.file_name = file_name
        self.url_dict = {}
        self.regex = regex
        self.file_data = file_data
        
        try:
            # Используем re.finditer для поиска совпадений
            matches = re.finditer(self.regex, self.file_data)

            for match in matches:
                url = match.group(0)  # Полный URL
                file_extension = match.group(1)  # Расширение файла

                # Извлечение имени файла из URL (до последней точки)
                file_name_without_ext = url.split('/')[-1].rsplit('.', 1)[0]

                #print(f"URL: {url}, Имя файла: {file_name_without_ext}, Расширение: .{file_extension}")  # Отладочный вывод
                file_name = file_name.replace(" ", "_")
                new_file_name = f"{file_name[:-3]}_{len(self.url_dict)}.{file_extension}"
                print(f"URL: {url}, Имя файла: {new_file_name}")

                # Сохранение URL и нового имени файла в словаре
                if url not in self.url_dict:
                    self.url_dict[url] = new_file_name

        except Exception as e:
            logging.exception("Ошибка при попытке найти URL и добавить их в словарь: %s", e)

        return self.url_dict

# Замена url в md файлах на путь к локальным файлам
class FileDataEditor:
    def edit(self, file_data, url_dict, file_name):
        self.file_name = file_name
        self.url_dict = url_dict
        self.file_data = file_data
        for key, value in url_dict.items():
            self.file_data = self.file_data.replace(key, value)
            print(f"Замена: {key} на {value}\nв файле {self.file_name}\n")
            logging.info(f"Замена: {key} на: {value}\nв файле: {self.file_name}\n")

        return self.file_data

# Создать новый log файл
logging.basicConfig(filename='debug.log', encoding='utf-8', filemode="w",   level=logging.DEBUG)

# Назначить папку для записи отредактированных .md файлов и загруженных изображений
folder_name = "output"
folder_path = os.path.abspath(os.path.join(os.getcwd(), folder_name))

folder_creator = FolderCreator()
folder_creator.create_folder(folder_name)
logging.info(f"Создана новая директория: {folder_path}\n")
print(f"Создана новая директория: {folder_path}")

# Regex для поиска ulr изображений в .md
# ![](https://www.ip.com/img.png)
# ![text](https://www.ip.com/img.png)
# ![](https://www.ip.com/img.png "text")
# ![](https://www.ip.com/img.png.png.png)
regex = r'(?<=\]\()https?:\/\/[^\s"()]+\.(png|jpg|jpeg|gif|bmp|svg|webp)(?=\s*["\)]|$)'

# Поиск каждого markdown файла в папке скрипта
for filename in os.listdir(os.getcwd()):

    if filename[-3:] != ".md":
        #logging.info(f"Пропущенный файл: {filename}\n")
        #print(f"Пропущенный файл: {filename}")
        continue

    # Открыть и прочитать весь файл
    file_opener = FileOpener()
    file_data = file_opener.open_and_read(filename)

    # Создать словарь с url изображений и новым именем файла для сохранения
    url_dict_creator = UrlDictCreator()
    url_dict = url_dict_creator.create(regex, file_data, filename)

    # Редактируем содержимое файла, заменяя найденные url на локальные имена файлов
    file_data_editor = FileDataEditor()
    edited_file_data = file_data_editor.edit(file_data, url_dict, filename)

    # Загружаем изображения из словаря найденных url
    images_downloader = ImgDownloader()
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
    images_downloader.download_images(url_dict, folder_path, user_agent)

    # Записываем изменённые md
    if url_dict:
        file_name_writter = FileWriter()
        file_name_writter.write_file(folder_path,filename, edited_file_data)
    
    print(f"\033[35mЗакрываем файл:\033[0m {filename}")
    logging.info(f"Закрываем файл: {filename}\n")

print("\nЕсли всё прошло без ошибок можно проверить модифицированные markdown файлы и скачанные изображения в папке:")
print(f"{folder_path}")

print(f"\nДетальная информация в лог файле \n{os.getcwd()}\\debug.log")
