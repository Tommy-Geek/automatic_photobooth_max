import screeninfo
import subprocess
import os
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import sys


class Prelaunch():
    """предзапуск над полностью переделать и пофиксить токен.txt"""

    def check_proc(self, name_process="CameraControl.exe"):
        '''проверяю запущен ли СameraСontrol'''
        try:
            output = subprocess.run(
                ['tasklist', '/fi', f'imagename eq {name_process}'],
                capture_output=True,
                text=True,
                timeout=5
            )
        
            if name_process not in output.stdout:
                subprocess.Popen(["C:\\Program Files (x86)\\digiCamControl\\CameraControl.exe"])
        
            return True  # Возвращаем True, если всё ок
        
        except FileNotFoundError:
            return False, "Системе не удается найти digiCamControl по пути C:\\Program Files (x86)\\digiCamControl\\CameraControl.exe"
        except PermissionError:
            return False, "Отказано в доступе. Запустите программу от имени администратора"
        except Exception as e:
            return False, f"Ошибка при запуске digiCamControl: {e}"

    def check_seconde_monitor(self):
        '''проверяю есть ли в системе второй монитор скип при запуске если false'''
        try:
            monitors = screeninfo.get_monitors()
            if len(monitors) < 2:
                return False, "Подключите второй монитор"
            return True
        except Exception as e:
            return False, f"Ошибка при проверке мониторов: {e}"

    def check_session(self):
        '''проверяю существует ли путь сессии digicam'''
        session_path = os.path.expandvars("%userprofile%\\Pictures\\digiCamControl\\Session1")
        if os.path.isdir(session_path):
            return True
        return False, "Проверьте путь сессии: должна быть папка Session1 в %userprofile%\\Pictures\\digiCamControl\\"


    def check_reserv(self):
        '''проверяю есть ли папка для резерв файлов'''
        reserv = os.path.expandvars("%userprofile%\\Desktop\\Reserv")
        if os.path.isdir(reserv):
            return True
    
        try:
            os.mkdir(reserv)
            return True
        except Exception as e:
            return False, f"Не удалось создать папку резерва: {e}"

    def start(self):
        '''главная функция проверки'''
        errors = []
        
        # Проверяем каждую функцию и собираем ошибки
        checks = [
            ("digiCamControl", self.check_proc()),
            ("Второй монитор", self.check_seconde_monitor()),
            ("Сессия", self.check_session()),
            ("Папка резерва", self.check_reserv()),
        ]
        
        for name, result in checks:
            if result is not True:  # если вернулся кортеж с ошибкой
                errors.append(f"{name}: {result[1]}")
        
        if errors:
            # Показываем все ошибки сразу
            error_text = "Обнаружены проблемы при запуске:\n\n" + "\n".join(errors)
            messagebox.showerror("Ошибка", error_text)
            return False
        
        return True