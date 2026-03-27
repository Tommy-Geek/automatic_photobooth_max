import yadisk
import os
import webbrowser
import sys
import tkinter.simpledialog as simpledialog


class YandexAPI:
    def __init__(self, token):
        self.token = token
        self.client = yadisk.YaDisk(token=token)

    def check_token(self):
        """Проверяет, валиден ли текущий токен"""
        with self.client:
            return self.client.check_token()

    def update_token(self, new_token):
        """Обновляет токен и пересоздаёт клиента"""
        self.token = new_token
        self.client = yadisk.YaDisk(token=new_token)

    def create_folder(self, copy_dir):
        """Создаёт папку на Яндекс.Диске по имени, извлечённому из copy_dir"""
        with self.client:
            folder_name = copy_dir[-16:].replace('\\', '_')
            self.client.mkdir(f"/{folder_name}")

    def upload_photo(self, copy_dir, last_photo):
        """Загружает фото на Яндекс.Диск в соответствующую папку"""
        if last_photo is None:
            return
        with self.client:
            folder_name = copy_dir[-16:].replace('\\', '_')
            file_name = os.path.basename(last_photo)
            disk_path = f"/{folder_name}/{file_name}"
            self.client.upload(last_photo, disk_path)

    def publish_folder(self, copy_dir):
        '''делает папаку публичной и возвращает ее url для формирования qrcode'''
        with self.client:
            folder_name = copy_dir[-16:].replace('\\', '_')
            self.client.publish(folder_name)
            public_url = self.client.get_meta(folder_name).public_url
            return public_url


token_file = "token.txt"
client_id = "aef14e72488c4f87bce1deff4d9120c6"

def get_base_path():
        #парсим базавый путь файла если это .exe или .py, рядом с запускашкой
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))


def load_token():
        #загружает токен из файла
        token_path = os.path.join(get_base_path(), token_file)
        try:
            with open(token_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            new_token = request_new_token()
            if new_token is None:
                raise ValueError("Токен не получен. Авторизация невозможна.")
            return new_token


def request_new_token(title = "Ошибка", message = "Вставте токен из браузера"):
        '''запрашивает новый токен у пользователя'''
        webbrowser.open(f"https://oauth.yandex.ru/authorize?response_type=token&client_id={client_id}")
        new_token = simpledialog.askstring(title, message)
        
        if not new_token:
            return None
        
        token_path = os.path.join(get_base_path(), token_file)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(new_token)
        return new_token
        


        