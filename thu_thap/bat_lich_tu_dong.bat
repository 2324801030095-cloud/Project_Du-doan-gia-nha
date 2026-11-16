@echo off
rem Bat lich tu dong: chay chay_dinh_ky.bat luc 08:00 moi Chu nhat (chay ca khi may vua mo lai neu lo lich).
powershell -NoProfile -ExecutionPolicy Bypass -Command "$a = New-ScheduledTaskAction -Execute '%~dp0chay_dinh_ky.bat'; $t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 8am; $s = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2); Register-ScheduledTask -TaskName PhuHoaHome_ThuThapDinhKy -Action $a -Trigger $t -Settings $s -Description 'Thu thap tin rao nha dat dinh ky cho de tai du doan gia nha Phu Hoa' -Force | Out-Null; Get-ScheduledTask -TaskName PhuHoaHome_ThuThapDinhKy | Select-Object TaskName, State"
pause
