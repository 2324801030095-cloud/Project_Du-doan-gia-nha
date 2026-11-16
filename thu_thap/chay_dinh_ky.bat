@echo off
rem Thu thap du lieu dinh ky: tai lai tin rao moi nhat + luu anh chup co ghi ngay vao data\lich_su\
rem Duoc Task Scheduler goi moi tuan (xem bat_lich_tu_dong.bat). Co the bam dup de chay tay.
chcp 65001 >nul
cd /d "%~dp0.."
set "PY=%~dp0..\..\..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
echo ==== %date% %time% ====>> "data\lich_su\nhat_ky_thu_thap.txt"
"%PY%" -X utf8 thu_thap\cap_nhat_dinh_ky.py >> "data\lich_su\nhat_ky_thu_thap.txt" 2>&1
echo Ket thuc, ma loi = %errorlevel% >> "data\lich_su\nhat_ky_thu_thap.txt"
