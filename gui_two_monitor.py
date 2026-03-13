from tkinter import *
from seconde_monitor import main_monitor_size, seconde_monitor_size, rotate_and_get_coords
from control_dir import check_last_photo
from PIL import Image, ImageTk

class TwoMonitor(Toplevel):
    def __init__(self, master = None):
        super().__init__(master)
        
        self.one_monitor = main_monitor_size()
        self.two_monitor = seconde_monitor_size()

        rotate_and_get_coords()

        self.title(None)     # устанавливаем заголовок окна
        self.geometry(f"{self.two_monitor[1]}x{self.two_monitor[0]}+{self.one_monitor[0]}+0")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.config(bg = 'black')
        

        self.label = Label(self, bg = 'black')
        self.label.pack(expand = True, fill = BOTH)

        self.current_photo = None
        self.active = False
        self.after_id = None 
    
    def update_photo(self):
        """Обновление фото"""
        if self.active:
            new_photo = check_last_photo()
            if new_photo != self.current_photo:
                with Image.open(new_photo) as image:
                    image = image.rotate(90, expand=True)
                    image.thumbnail((self.two_monitor[1], self.two_monitor[0]), Image.Resampling.LANCZOS)
                    self.photo = ImageTk.PhotoImage(image)
                    self.label.config(image=self.photo)
                    self.current_photo = new_photo
        self.after_id = self.after(2000, self.update_photo)

    def start(self):
        """Запуск показа фото"""
        if not self.active:
            self.active = True
            if self.after_id is None:
                self.update_photo()

    def stop(self):
        """Остановка показа фото"""
        self.active = False
        self.label.config(image='')
        self.current_photo = None
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

