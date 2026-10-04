@echo off
chcp 65001 >nul
title KI-Besucherterminal // llama.cpp Live-Demo

echo ==========================================================
echo 🏢  STARTING KI-BESUCHERTERMINAL LIVE DEMO
echo ==========================================================
echo.

:: 1. Check if llama-server is running on port 8080
netstat -ano | findstr ":8080" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] llama-server läuft bereits auf Port 8080.
) else (
    echo [..] Starte llama.cpp Server mit Gemma-4 E4B + mmproj + MTP Drafter...
    start "llama-server-backend" "D:\local_ai\dll\start.bat"
    
    echo [..] Warte kurz, bis das Modell in den VRAM geladen ist...
    timeout /t 5 /nobreak >nul
)

echo.
echo [..] Starte lokalen Webserver für das Besucherterminal...
cd /d "%~dp0"
python "%~dp0server.py"

pause
