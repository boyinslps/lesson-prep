@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===== Beike Cockpit / Bei-Ke Jia-Shi-Cang =====
echo Server: http://127.0.0.1:8770  (opening browser...)
echo Close this window to stop the server.
start "" http://127.0.0.1:8770
"%~dp0runtime\python\python.exe" "%~dp0server.py"
echo.
echo Server stopped.
pause
