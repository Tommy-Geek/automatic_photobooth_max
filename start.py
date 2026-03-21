import screeninfo
import subprocess
import os
import tkinter.messagebox as messagebox
import webbrowser
import tkinter.simpledialog as simpledialog
import sys


class Prelaunch():
    """предзапуск над полностью переделать и пофиксить токен.txt"""
    def __init__(self):
        self.token_file = "token.txt"
        self.client_id = "aef14e72488c4f87bce1deff4d9120c6"
        self.api = None

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

    def get_base_path(self):
        #парсим базавый путь файла если это .exe или .py
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))


    def load_token(self):
        '''загружает токен из файла'''
        token_path = os.path.join(self.get_base_path(), self.token_file)
        try:
            with open(token_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def save_token(self, token):
        token_path = os.path.join(self.get_base_path(), self.token_file)
        with open(token_path, "w") as file:
            file.write(token.strip())
            

    def check_yandex_token(self):
        '''проверяю токен Яндекс.Диска'''
        try:
            # Загружаем токен из файла
            token = self.load_token()
            
            # Если токена нет - запрашиваем
            if token is None:
                result = self.request_new_token(
                    "Токен Яндекс.Диска", 
                    "Браузер открыт со страницей получения токена.\n"
                    "Вставьте полученный токен и нажмите ОК:"
                )
                if result is True:
                    return True
                else:
                    return result  # Возвращаем кортеж с ошибкой
            
            # Создаём API и проверяем токен
            from api_yandex import YandexAPI
            self.api = YandexAPI(token)
            
            if not self.api.check_token():
                # Токен невалидный - запрашиваем новый
                result = self.request_new_token(
                    "Токен недействителен",
                    "Браузер открыт со страницей получения нового токена.\n"
                    "Вставьте новый токен и нажмите ОК:"
                )
                if result is True:
                    return True
                else:
                    return result
            
            return True  # Токен валидный
            
        except Exception as e:
            return False, f"Ошибка при проверке токена Яндекс.Диска: {e}"

    def request_new_token(self, title, message):
        '''запрашивает новый токен у пользователя'''
        webbrowser.open(f"https://oauth.yandex.ru/authorize?response_type=token&client_id={self.client_id}")
        new_token = simpledialog.askstring(title, message)
        
        if not new_token:
            return False, "Токен не введён. Авторизация невозможна."
        
        # Проверяем новый токен
        from api_yandex import YandexAPI
        temp_api = YandexAPI(new_token)
        
        if temp_api.check_token():
            self.save_token(new_token)
            self.api = temp_api  # Сохраняем API в атрибут класса
            return True
        else:
            return False, "Полученный токен недействителен"

    def get_api(self):
        '''возвращает объект API после успешной авторизации'''
        return self.api

    def start(self):
        '''главная функция проверки'''
        errors = []
        
        # Проверяем каждую функцию и собираем ошибки
        checks = [
            ("digiCamControl", self.check_proc()),
            ("Второй монитор", self.check_seconde_monitor()),
            ("Сессия", self.check_session()),
            ("Папка резерва", self.check_reserv()),
            ("Яндекс.Диск", self.check_yandex_token())
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