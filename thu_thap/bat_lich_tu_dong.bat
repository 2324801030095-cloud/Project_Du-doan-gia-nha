@echo off
rem Bat lich tu dong: chay chay_dinh_ky.bat luc 07:00 MOI NGAY (chay bu khi may vua mo lai neu lo lich):
rem thu thap tin moi nhat roi chay lai toan bo notebook, trang web, README va kiem thu.
rem Chay CA KHI KHONG DANG NHAP (LogonType S4U, khong can luu mat khau): dang xuat / khoa may khong con lam ngat
rem tac vu nhu lan 22/11/2026 (ma 0xC000013A). Dang ky S4U can quyen Administrator nen script tu xin quyen (UAC).
net session >nul 2>&1
if errorlevel 1 (
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "$a = New-ScheduledTaskAction -Execute '%~dp0chay_dinh_ky.bat'; $t = New-ScheduledTaskTrigger -Daily -At 7am; $s = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2); $p = New-ScheduledTaskPrincipal -UserId '%USERDOMAIN%\%USERNAME%' -LogonType S4U -RunLevel Limited; Register-ScheduledTask -TaskName PhuHoaHome_ThuThapDinhKy -Action $a -Trigger $t -Settings $s -Principal $p -Description 'Thu thap tin rao nha dat dinh ky cho de tai du doan gia nha Phu Hoa' -Force | Out-Null; Get-ScheduledTask -TaskName PhuHoaHome_ThuThapDinhKy | Select-Object TaskName, State, @{n='LogonType';e={$_.Principal.LogonType}}"
pause
