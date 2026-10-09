@echo off
if exist "%~dp0visitor-terminal\start_demo.bat" (
    call "%~dp0visitor-terminal\start_demo.bat"
) else (
    call "%~dp0visitor_terminal\start_demo.bat"
)
