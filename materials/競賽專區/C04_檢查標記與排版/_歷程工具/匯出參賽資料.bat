@echo off
chcp 65001 >nul
cd /d "%~dp0..\..\..\.."
"工作台\runtime\python\python.exe" "materials\競賽專區\C04_檢查標記與排版\_歷程工具\匯出參賽資料.py" %*
echo.
if exist "materials\競賽專區\_繳交輸出" explorer "materials\競賽專區\_繳交輸出"
pause
