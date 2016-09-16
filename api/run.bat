@echo off
set "PROJECT_PATH=C:\Users\NDSTHK\Documents\Immersive lab\api"
set "VIRTUAL_ENV=%PROJECT_PATH%\venv"
set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"
cd %PROJECT_PATH%
python app.py
