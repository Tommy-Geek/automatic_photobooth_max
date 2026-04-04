# bw.py (дополняем)
from multiprocessing import Process, Queue
import time
import os
from control_dir import check_last_photo, b_and_w_dir
from PIL import Image


def full_painting_cycle(new_time_dir, bw_last):
    """покраска с переворотом в чб"""
    last_photo_dir_one = check_last_photo(new_time_dir)
    last_photo_dir_two = check_last_photo(bw_last)
    if last_photo_dir_one and last_photo_dir_one[-1] != "w" and last_photo_dir_one != last_photo_dir_two:
        with Image.open(last_photo_dir_one) as img:
            img = img.convert('L')
            img = img.rotate(90, expand=True)
            filename = os.path.basename(last_photo_dir_one)
            save_path = os.path.join(bw_last, filename)
            img.save(save_path)


# Функция, которая будет выполняться в отдельном процессе
def bw_worker(copy_dir, bw_last, stop_queue):
    """проверка флага стопа и бесконечный цикл с проверкой фото"""
    import time
    while True:
        try:
            if not stop_queue.empty():
                if stop_queue.get_nowait() == "STOP":
                    break
        except:
            pass

        try:
            full_painting_cycle(copy_dir, bw_last)

        except Exception as e:
            print(f"Ошибка в фоновом процессе: {e}")

        time.sleep(0.5)

class BWProcessor:
    """Класс для управления фоновым процессом конвертации в Ч/Б"""

    def __init__(self):
        self.process = None
        self.stop_queue = None
        self.copy_dir = None
        self.bw_dir = None

    def start(self, copy_dir):
        """Запускает фоновый процесс"""
        if self.process and self.process.is_alive():
            return self.bw_dir

        self.copy_dir = copy_dir
        self.bw_dir = b_and_w_dir(copy_dir)  # создаём подпапку bw
        self.stop_queue = Queue()

        self.process = Process(
            target=bw_worker,
            args=(self.copy_dir, self.bw_dir, self.stop_queue)
        )
        self.process.start()
        return self.bw_dir

    def stop(self, timeout=2):
        """Останавливает фоновый процесс"""
        if self.process and self.process.is_alive():
            self.stop_queue.put("STOP")
            self.process.join(timeout=timeout)
            if self.process.is_alive():
                self.process.terminate()
                self.process.join()
        self.process = None
        self.stop_queue = None

    def is_alive(self):
        """Проверяет жив ли процесс"""
        return self.process is not None and self.process.is_alive()

















# def full_painting_cycle(new_time_dir, bw_last):

#     last_photo_dir_one = check_last_photo(new_time_dir)
#     last_photo_dir_two = check_last_photo(bw_last)
#     if last_photo_dir_one[-1] != "w" and last_photo_dir_one != last_photo_dir_two:
#         with Image.open(last_photo_dir_one) as img:
#             img = img.convert('L')
#             img.save(bw_last)


