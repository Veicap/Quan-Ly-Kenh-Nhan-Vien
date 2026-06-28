@echo off
chcp 65001 > nul
echo [%date% %time%] Bat dau backup database...
python -X utf8 "%~dp0backup_db.py"
echo.
echo Backup hoan tat! Nhan phim bat ky de dong...
pause
