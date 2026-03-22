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
    b_and_w_dir
    )
import threading
from tkinter import messagebox
from qr_code import create_qr
from start import Prelaunch
from remove_control import make_photo
from bw import BWProcessor
import sys


class Main_window(ctk.CTk):
    
    def __init__(self, api):
        super().__init__()
        self.api = api

        ctk.set_appearance_mode("dark")
        self.geometry('700x500')

        info = api.client.get_disk_info()
        self.stop_flag = False
        self.bw_procces = BWProcessor()
        self.monitor = TwoMonitor(self)
        self.copy_active = False
        self.copy_dir = None
        self.last_photo = None 

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

        self.fr_start = ctk.CTkFrame(self.main_frame, height=50)
        self.fr_start.grid(row = 2, column = 0, sticky='nsew')
        self.fr_start.grid_propagate(False)

        self.fr_stop = ctk.CTkFrame(self.main_frame, height=70)
        self.fr_stop.grid(row = 2, column = 1, sticky='nsew')
        self.fr_stop.grid_propagate(False)


        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=4)  
        self.main_frame.grid_rowconfigure(2, weight= 2)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        self.user_login = ctk.CTkLabel(
            self.fr_info,
            text = f"Login: {info.user.display_name}",
            text_color='white',
            corner_radius=10,
            font=('Arial',16)
            )
        self.user_login.pack(pady=5, anchor='w')

        self.space = ctk.CTkLabel(
            self.fr_info,
            text = f"Space left: {round((info.total_space - info.used_space)/1024**3, 2)}gb",
            text_color='white',
            corner_radius=10,
            font=('Arial',16)
            )
        self.space.pack(pady=5, anchor='w')

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
        self.check_box = ctk.CTkCheckBox(
            self.fr_settings, 
            text = "B/W", 
            variable=self.enabled, 
            width=150,           
            height=60 
            )
        self.check_box.place(
            relx=0.5,           # 50% от ширины фрейма
            rely=0.5,            # 50% от высоты фрейма
            anchor='center',       # центр кнопки в центре фрейма            
        )

        self.start_button = ctk.CTkButton(
            self.fr_start, 
            text = "Start", 
            command = self.start, 
            width=150,
            height=60
            )
        self.start_button.place(
            relx=0.5,           # 50% от ширины фрейма
            rely=0.5,            # 50% от высоты фрейма
            anchor='center'       # центр кнопки в центре фрейма            
        )

        self.stop_button = ctk.CTkButton(
            self.fr_stop, 
            text = "Show QR", 
            state= 'disabled', 
            command = self.stop, 
            width=150,
            height=60
            )
        self.stop_button.place(
            relx=0.5,
            rely=0.5,
            anchor='center'
        )


    def start(self):
        delet_all_photo()
        if not self.enabled.get():
            self.normal_copying()

        else:
            self.normal_copying()
            self.bw_procces.start(self.copy_dir)


    def normal_copying(self):
        self.monitor.start()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

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
            self.stop_button.config(text="Stop", state='normal')
            self.stop_flag = True
        
        else:
            self.monitor.stop()
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            delet_all_photo()
            self.stop_flag = False
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
    threading.Thread(target=lambda: make_photo(), daemon=True).start()
    api = prelaunch.get_api()
    Main_window(api).mainloop()