import yadisk
import os
import requests

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

