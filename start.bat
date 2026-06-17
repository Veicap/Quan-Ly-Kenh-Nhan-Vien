@echo off
chcp 65001 > nul
title Quan Ly Kenh Nhan Su - YouTube HR Manager
color 0A

echo.
echo ============================================================
echo    QUAN LY KENH NHAN SU - YouTube HR Channel Manager
echo ============================================================
echo.

:: Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python. Vui long cai dat Python 3.10+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Kiem tra va cai dat dependencies...
cd /d "%~dp0backend"

pip install -r requirements.txt -q
if errorlevel 1 (
    echo [LOI] Khong the cai dat dependencies!
    pause
    exit /b 1
)

echo [2/3] Dependencies da san sang!
echo [3/3] Khoi dong server...
echo.
echo ============================================================
echo  Server dang chay tai: http://localhost:5000
echo  Tai khoan mac dinh  : admin / admin123
echo  Nhan Ctrl+C de dung server
echo ============================================================
echo.

python run.py

pause
