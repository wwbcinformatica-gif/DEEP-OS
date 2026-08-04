@echo off
title WBC - Parando servidores

echo.
echo Parando Backend e Frontend...
echo.

for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Parando Backend PID %%a...
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do (
    echo Parando Frontend PID %%a...
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| find ":5174" ^| find "LISTENING"') do (
    echo Parando Frontend (fallback) PID %%a...
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Servidores parados.
echo.
pause
