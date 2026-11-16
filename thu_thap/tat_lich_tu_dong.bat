@echo off
rem Tat lich tu dong da bat boi bat_lich_tu_dong.bat
powershell -NoProfile -Command "Unregister-ScheduledTask -TaskName PhuHoaHome_ThuThapDinhKy -Confirm:$false; Write-Host Da tat lich thu thap tu dong"
pause
