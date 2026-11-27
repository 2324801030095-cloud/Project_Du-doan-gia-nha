@echo off
rem Lich thu thap tu dong (Task Scheduler). Cach dung:
rem   lich_tu_dong.bat        bat lich: chay "lich_tu_dong.bat chay" luc 07:00 MOI NGAY (chay bu khi may vua mo lai neu lo lich)
rem   lich_tu_dong.bat tat    tat lich
rem   lich_tu_dong.bat chay   thu thap ngay (tai tin moi nhat, luu anh chup vao dataset\history\, chay lai toan bo de tai)
rem Lich chay CA KHI KHONG DANG NHAP (LogonType S4U, khong can luu mat khau): dang xuat / khoa may khong lam ngat
rem tac vu nhu lan 22/11/2026 (ma 0xC000013A). Dang ky S4U can quyen Administrator nen script tu xin quyen (UAC).
if /i "%~1"=="chay" goto chay
if /i "%~1"=="tat" goto tat

net session >nul 2>&1
if errorlevel 1 (
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "$a = New-ScheduledTaskAction -Execute '%~f0' -Argument 'chay'; $t = New-ScheduledTaskTrigger -Daily -At 7am; $s = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2); $p = New-ScheduledTaskPrincipal -UserId '%USERDOMAIN%\%USERNAME%' -LogonType S4U -RunLevel Limited; Register-ScheduledTask -TaskName PhuHoaHome_ThuThapDinhKy -Action $a -Trigger $t -Settings $s -Principal $p -Description 'Thu thap tin rao nha dat dinh ky cho de tai du doan gia nha Phu Hoa' -Force | Out-Null; Get-ScheduledTask -TaskName PhuHoaHome_ThuThapDinhKy | Select-Object TaskName, State, @{n='LogonType';e={$_.Principal.LogonType}}"
pause
exit /b

:tat
powershell -NoProfile -Command "Unregister-ScheduledTask -TaskName PhuHoaHome_ThuThapDinhKy -Confirm:$false; Write-Host Da tat lich thu thap tu dong"
pause
exit /b

:chay
chcp 65001 >nul
cd /d "%~dp0.."
rem Dung Python cua .venv o thu muc mon hoc (3 cap tren scripts) neu co, khong thi python tren PATH; nhat ky ghi vao dataset\history
set "PY=%~dp0..\..\..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
echo ==== %date% %time% ====>> "dataset\history\nhat_ky_thu_thap.txt"
"%PY%" -X utf8 scripts\cap_nhat_dinh_ky.py >> "dataset\history\nhat_ky_thu_thap.txt" 2>&1
echo Ket thuc, ma loi = %errorlevel% >> "dataset\history\nhat_ky_thu_thap.txt"
