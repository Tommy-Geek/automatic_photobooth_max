import multiprocessing
multiprocessing.freeze_support()
import customtkinter as ctk
from gui_two_monitor import TwoMonitor
from control_dir import (
    new_time_dir, 
    delet_all_photo, 
    check_last_photo, 
    copy_reserv, 
    SESSION_PATH, 
    )
import threading
from tkinter import messagebox
from qr_code import create_qr
from seconde_monitor import has_seconde_monitor
from start import Prelaunch
from remove_control import make_photo
from bw import BWProcessor
import sys
import os

from api_yandex import YandexAPI, load_token, request_new_token


class Main_window(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.geometry('700x500')

        self.bw_procces = BWProcessor()
        self.monitor = TwoMonitor(self)
        self.copy_active = False
        self.copy_dir = None
        self.last_photo_loacal = None
        self.last_photo_yadisk = None 
        self.last_photo_bw = None
        self.api = None
        self.in_all_photo = 0
        self.bw_painting = 0

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill = 'both', expand = True)

        self.fr_label_info = ctk.CTkFrame(self.main_frame, height=30)
        self.fr_label_info.grid(row = 0, column = 0, sticky='nsew')
        self.fr_label_info.grid_propagate(False)

        self.fr_label_settings = ctk.CTkFrame(self.main_frame, height=30)
        self.fr_label_settings.grid(row = 0, column = 1, sticky='nsew')

        self.fr_info = ctk.CTkFrame(self.main_frame, height=70)
        self.fr_info.grid(row = 1, column = 0, sticky='nsew')

        self.fr_settings = ctk.CTkFrame(self.main_frame, height=70)
        self.fr_settings.grid(row = 1, column = 1, sticky='nsew')

        self.fr_button = ctk.CTkFrame(self.main_frame, height=50)
        self.fr_button.grid(row = 2, column = 0, sticky='nsew', columnspan=2)
        self.fr_button.grid_propagate(False)


        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=4)  
        self.main_frame.grid_rowconfigure(2, weight= 2)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)


        if not has_seconde_monitor():
            self.text = "Не обнаружен"
        else:
            self.text = "Обнаружен"

        self.seconde_monitor = ctk.CTkLabel(
            self.fr_info,
            text= f"Второй монитор: {self.text}",
            text_color='white',
            corner_radius=10,
            font=('Arial',16)
        )
        self.seconde_monitor.pack(pady=5, anchor='center')

        self.user_login = ctk.CTkLabel(
            self.fr_info,
            text="Login: не авторизован",
            text_color='white',
            corner_radius=10,
            font=('Arial',16)
        )
        self.user_login.pack(pady=5, anchor='center')

        self.space = ctk.CTkLabel(
            self.fr_info,
            text="Свободное место: не авторизован",
            text_color='white',
            corner_radius=10,
            font=('Arial',16)
        )
        self.space.pack(pady=5, anchor='center')


        self.total_photo = ctk.CTkLabel(
            self.fr_info,
            text="Всего фото: 0",
            text_color='white',
            corner_radius=10,
            font=('Arial', 16)
        )
        self.total_photo.pack(pady=5, anchor='center')


        self.painting_photo = ctk.CTkLabel(
            self.fr_info,
            text="Покрашено: 0",
            text_color='white',
            corner_radius=10,
            font=('Arial', 16)
        )
        self.painting_photo.pack(pady=5, anchor='center')


        self.sent_photo = ctk.CTkLabel(
            self.fr_info,
            text="Отправлено: 0",
            text_color='white',
            corner_radius=10,
            font=('Arial', 16)
        )
        self.sent_photo.pack(pady=5, anchor='center')


        token = load_token()
        if token:
            try:
                self.api = YandexAPI(token)
                info = self.api.client.get_disk_info()
                self.user_login.configure(text=f"Login: {info.user.display_name}")
                free_gb = round((info.total_space - info.used_space) / 1024**3, 2)
                self.space.configure(text=f"Свободно: {free_gb} ГБ")
            except Exception:
                pass

        self.label = ctk.CTkLabel(
            self.fr_label_info,
            text='Information',
            text_color='white',
            corner_radius=10,
            font=('Arial', 16)
        )
        self.label.place(relx=0.5, rely=0.5, anchor = 'center')

        self.label = ctk.CTkLabel(
            self.fr_label_settings,
            text='Settings',
            text_color='white',
            corner_radius=10,
            font=('Arial', 16)
        )
        self.label.place(relx=0.5, rely=0.5, anchor = 'center')


        self.enabled = ctk.BooleanVar()
        self.bw_check_box = ctk.CTkCheckBox(
            self.fr_settings, 
            text = "B/W", 
            variable=self.enabled, 
            width=150,           
            height=60 
        )
        self.bw_check_box.place(
            relx=0.5,           # 50% от ширины фрейма
            rely=0.6,            # 50% от высоты фрейма
            anchor='center',       # центр кнопки в центре фрейма            
        )


        self.on_download_yadisk = ctk.BooleanVar()
        self.yadisk_check_box = ctk.CTkCheckBox(
            self.fr_settings, 
            text = "download yadisk", 
            variable=self.on_download_yadisk,
            command=self.toggle_yandex_api, 
            width=150,           
            height=60 
        )
        self.yadisk_check_box.place(
            relx=0.5,           # 50% от ширины фрейма
            rely=0.4,            # 50% от высоты фрейма
            anchor='center',       # центр кнопки в центре фрейма         
        )

        self.start_button = ctk.CTkButton(
            self.fr_button, 
            text = "Start", 
            command = self.start, 
            width=150,
            height=60
        )
        self.start_button.place(
            relx=0.1,           # 50% от ширины фрейма
            rely=0.5,            # 50% от высоты фрейма
            anchor='w'       # центр кнопки в центре фрейма            
        )

        self.stop_button = ctk.CTkButton(
            self.fr_button, 
            text = "Stop", 
            state= 'disabled', 
            command = self.stop, 
            width=150,
            height=60
        )
        self.stop_button.place(
            relx=0.9,
            rely=0.5,
            anchor='e'
        )

        self.qr_code_button = ctk.CTkButton(
            self.fr_button,
            text = "Show QR",
            state='disabled',
            command= self.show_qr,
            width=150,
            height=60
        )
        self.qr_code_button.place(
            relx=0.5,
            rely=0.5,
            anchor='center'
        ) 


    def start(self):
        delet_all_photo()
        self.sent_photo.configure(text="Отправлено: 0")
        self.painting_photo.configure(text="Покрашено: 0")
        self.total_photo.configure(text="Всего фото: 0")
        self.stop_button.configure(state='normal')
        self.start_button.configure(state='disabled')

        self.in_all_photo = 0
        self.bw_painting = 0
        
        self.normal_copying()

        if self.enabled.get():
            self.bw_procces.start(self.copy_dir)
            self.update_bw_label()

        if self.on_download_yadisk.get():
            self.qr_code_button.configure(state='normal')
            self.api.create_folder(self.copy_dir)
            self.download_yadisk()

        if self.enabled.get() and self.on_download_yadisk.get():
            self.api.create_bw_folder(self.copy_dir)
            self.download_bw()
        
    

    def update_bw_label(self):
        bw_dir = os.path.join(self.copy_dir, "bw")
        self.bw_painting = self.amount_photo(bw_dir, self.painting_photo, self.bw_painting)
        self.after(500, self.update_bw_label)


    def download_bw(self):
        if not self.copy_active: 
            return
        bw_path = os.path.join(self.copy_dir, 'bw')
        new_photo = check_last_photo(bw_path)

        if self.last_photo_bw != new_photo and new_photo:
            self.last_photo_bw = new_photo
            threading.Thread(
                    target=self.api.upload_bw_photo,
                    args=(self.copy_dir, new_photo),
                    daemon=True
                ).start()
        self.after(500, self.download_bw)

        self.total_photo

    def toggle_yandex_api(self):
        token = load_token()
        if token is None:
            token = request_new_token()
        if token:
            self.api = YandexAPI(token)
            try:
                info = self.api.client.get_disk_info()
                self.user_login.configure(text=f"Login: {info.user.display_name}")
                free_gb = round((info.total_space - info.used_space) / 1024**3, 2)
                self.space.configure(text=f"Свободно: {free_gb} ГБ")
            except Exception as er:
                self.user_login.configure(text="Login: ошибка")
                self.space.configure(text="Свободно: ошибка")
        
    def download_yadisk(self):
        if not self.copy_active: 
            return
        new_photo = check_last_photo()

        if self.last_photo_yadisk != new_photo:
            self.last_photo_yadisk = new_photo
            threading.Thread(
                    target=self.upload_photo_wrapper,
                    args=(self.copy_dir, new_photo),
                    daemon=True
                ).start()
        self.after(500, self.download_yadisk)


    def upload_photo_wrapper(self, copy_dir, photo_path):
        """Обёртка для вызова загрузки с последующим обновлением счётчика."""
        success = self.api.upload_photo(copy_dir, photo_path)
        if success:
            self.after(0, self.increment_counter(self.sent_photo))


    def increment_counter(self, label: ctk.CTkLabel):
        """Увеличивает счётчик фото"""
        text = label.cget("text")
        parts = text.split(": ")
        prefix = parts[0]
        current_num = int(parts[1])
        label.configure(text=f"{prefix}: {current_num + 1}")


    def normal_copying(self):
        self.monitor.start()

        self.copy_dir = new_time_dir()
        self.last_photo_loacal = None
        self.last_photo_yadisk = None
        self.copy_active = True

        print("start")
        self.check_photo()


    def check_photo(self):
        if self.copy_active == False:
            return
        
        self.in_all_photo = self.amount_photo(SESSION_PATH, self.total_photo, self.in_all_photo)
        new_photo = check_last_photo()

        if self.last_photo_loacal != new_photo:
            self.last_photo_loacal = new_photo
            copy_reserv(self.copy_dir, self.last_photo_loacal)
        self.after(500, self.check_photo)


    def amount_photo(self, dir, label, initial_quantity):
        amount = len(os.listdir(dir))
        if initial_quantity != amount:
            print(amount, initial_quantity)
            initial_quantity += 1
            self.increment_counter(label)
        return initial_quantity


    def show_qr(self):
        """делает папку публичной и генерит qrcode"""
        url = self.api.publish_folder(self.copy_dir)
        create_qr(url, SESSION_PATH)


    def stop(self):
        if not self.copy_active:
            return
        
        self.copy_active = False
        self.monitor.stop()
        self.qr_code_button.configure(state='disabled')
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        delet_all_photo()
        self.bw_procces.stop()

    def destroy(self):
        """автоматом убивает обьект второго монитора и краски при закрытии"""
        if hasattr(self, 'bw_procces'):
            self.bw_procces.stop()
        if hasattr(self, 'monitor'):
            self.monitor.destroy()
        super().destroy()

if __name__ == "__main__":
    prelaunch = Prelaunch()
    while True:
        if prelaunch.start():
            # Все проверки пройдены – выходим из цикла
            break
        else:
            retry = messagebox.askyesno(
                "Ошибка",
                "Исправьте указанные проблемы и нажмите 'Да' для повторной проверки, или 'Нет' для выхода."
            )
            if not retry:
                sys.exit(0)
    
    # Успешный предзапуск: запускаем фоновые задачи и главное окно
    threading.Thread(target=make_photo, daemon=True).start()
    Main_window().mainloop()
