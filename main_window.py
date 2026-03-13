from tkinter import *
from gui_two_monitor import TwoMonitor
from control_dir import new_time_dir, delet_all_photo, check_last_photo, copy_reserv, SESSION_PATH
import threading
from tkinter import simpledialog, messagebox
import os
from qr_code import create_qr
import webbrowser
from start import Prelaunch
from remove_control import make_photo


class Main_window(Tk):
    
    def __init__(self, api):
        super().__init__()
        self.api = api

        self.geometry('700x500')

        self.stop_flag = False
        self.monitor = TwoMonitor(self)
        self.copy_active = False
        self.copy_dir = None           # куда копируем
        self.last_photo = None 

        self.main_frame = Frame(self, bg = "white")
        self.main_frame.pack(fill = BOTH, expand = True)

        self.fr_label_info = Frame(self.main_frame, bg = 'green')
        self.fr_label_info.grid(row = 0, column = 0, sticky='nsew')

        self.fr_label_settings = Frame(self.main_frame, bg = 'red')
        self.fr_label_settings.grid(row = 0, column = 1, sticky='nsew')

        self.fr_info = Frame(self.main_frame, bg = 'black')
        self.fr_info.grid(row = 1, column = 0, sticky='nsew')

        self.fr_settings = Frame(self.main_frame, bg = 'orange')
        self.fr_settings.grid(row = 1, column = 1, sticky='nsew')

        self.fr_start = Frame(self.main_frame, bg = 'pink')
        self.fr_start.grid(row = 2, column = 0, sticky='nsew')
        self.fr_start.grid_propagate(False)

        self.fr_stop = Frame(self.main_frame, bg = 'silver')
        self.fr_stop.grid(row = 2, column = 1, sticky='nsew')
        self.fr_stop.grid_propagate(False)


        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=4)  
        self.main_frame.rowconfigure(2, weight= 2)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        self.start_button = Button(self.fr_start, text = "Start", command = self.start)
        self.start_button.place(
            relx=0.5,           # 50% от ширины фрейма
            rely=0.5,            # 50% от высоты фрейма
            anchor=CENTER,       # центр кнопки в центре фрейма
            width=150,           # ширина 150 пикселей
            height=60            # высота 60 пикселей
        )

        self.stop_button = Button(self.fr_stop, text = "Show QR", state= DISABLED, command = self.stop)
        self.stop_button.place(
            relx=0.5,
            rely=0.5,
            anchor=CENTER,
            width=150,
            height=60
        )

    def start(self):
        self.monitor.start()
        self.start_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)

        self.copy_dir = new_time_dir()
        self.last_photo = None
        self.copy_active = True
        self.stop_flag = False

        self.api.create_folder(self.copy_dir) #cоздам папку в я.д

        print("start")
        self.check_photo()

    def check_photo(self):
        if not self.copy_active:
            return
        
        new_photo = check_last_photo()

        if self.last_photo != new_photo:
            self.last_photo = new_photo
            copy_reserv(self.copy_dir, self.last_photo)
            threading.Thread(
                target=lambda: self.api.upload_photo(self.copy_dir, self.last_photo),
                daemon=True
            ).start()
        self.after(500, self.check_photo)
        

    def stop(self):
        if not self.stop_flag:
            url = self.api.publish_folder(self.copy_dir)
            create_qr(url, SESSION_PATH)
            self.copy_active = False
            self.stop_button.config(text="Stop", state=NORMAL)
            self.stop_flag = True
        
        else:
            self.monitor.stop()
            self.start_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)
            delet_all_photo()
            self.stop_flag = False

    def destroy(self):
        """автоматом убивает обьект второго монитора при закрытии"""
        if hasattr(self, 'monitor'):
            self.monitor.destroy()
        super().destroy()

if __name__ == "__main__":
    prelaunch = Prelaunch()
    
    # Запускаем все проверки
    if prelaunch.start():
        threading.Thread(
            target = lambda: make_photo(), 
            daemon = True).start()
        # Если все проверки пройдены - получаем API и запускаем главное окно
        api = prelaunch.get_api()  # API уже сохранен внутри prelaunch
        Main_window(api).mainloop()
    else:
        # Если есть ошибки - программа уже показала сообщение и завершается
        exit()