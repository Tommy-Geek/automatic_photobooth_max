@echo off
chcp 65001 >nul
title Сборка Photobooth

echo Активация виртуального окружения...
call "%~dp0virtual\Scripts\activate.bat"

if errorlevel 1 (
    echo Ошибка: не удалось активировать виртуальное окружение.
    echo Убедитесь, что папка virtual существует в %~dp0
    pause
    exit /b 1
)

echo Запуск PyInstaller...
pyinstaller --onefile --name Photobooth ^
    --add-data "token.txt;." ^
    --hidden-import yadisk ^
    --hidden-import requests ^
    --hidden-import keyboard ^
    --hidden-import pycaw ^
    --hidden-import comtypes ^
    --hidden-import screeninfo ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    --hidden-import PIL ^
    --hidden-import qrcode ^
    --collect-all yadisk ^
    --collect-all requests ^
    --collect-all PIL ^
    main_window.py

if errorlevel 1 (
    echo Произошла ошибка при сборке.
    pause
    exit /b 1
)

echo.
echo Сборка успешно завершена! Исполняемый файл находится в папке dist.
pause