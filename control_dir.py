import os
import shutil
from shutil import rmtree
from datetime import datetime
from pathlib import Path
import psutil

SESSION_PATH = os.path.expandvars("%userprofile%\\Pictures\\digiCamControl\\Session1")
RESERV = os.path.expandvars("%userprofile%\\Desktop\\Reserv")

def new_date_dir():
    '''создаем папку в резерве с текущий датой'''
    present_day = datetime.today().strftime("%Y-%m-%d")
    full_path_day = os.path.join(RESERV, present_day)
    os.makedirs(full_path_day, exist_ok=True)  # exist_ok=True заменяет try/except
    return full_path_day


def new_time_dir():
    '''создаем папку точного времени начала в папке даты в резерве и возвращает фулл путь до папки'''
    present_time = datetime.now().strftime("%H-%M")
    present_day = new_date_dir()
    full_path_time = os.path.join(present_day, present_time)
    os.makedirs(full_path_time, exist_ok=True)
    return full_path_time


def check_last_photo():
    '''получает полный путь последней фотографии добавленной в папку'''
    try:
        photo_list = os.listdir(SESSION_PATH)
        if photo_list:  # проверяем что список не пустой
            last_photo = os.path.join(SESSION_PATH, photo_list[-1])
            return last_photo
        return None
    except (IndexError, FileNotFoundError):
        print("папка пуста или не найдена")
        return None


def copy_reserv(full_path, last_photo):
    try:
        shutil.copy2(last_photo, full_path)
    except Exception as e:
        print(f"Ошибка копирования: {e}")
    

def delet_all_photo():
    for path in Path(SESSION_PATH).glob('*'):
        if path.is_dir():
            rmtree(path)
        else:
            path.unlink()

