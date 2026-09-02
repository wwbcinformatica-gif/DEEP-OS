@echo off
title DEEP-OS SaaS

cd /d "%~dp0"

echo.
echo Iniciando DEEP-OS SaaS...
echo.

:: Inicia backend
echo [1/2] Iniciando Backend (porta 8001)...
start "DEEP-OS Backend" cmd /k "cd /d C:\DEEP-OS\backend && C:\DEEP-OS\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload"

:: Aguarda backend iniciar
timeout /t 5 /nobreak >nul

:: Inicia frontend
echo [2/2] Iniciando Frontend SaaS (porta 5176)...
start "DEEP-OS Frontend" cmd /k "cd /d C:\DEEP-OS\frontend && npx vite --mode saas --port 5176"

timeout /t 4 /nobreak >nul

echo.
echo ============================================
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:5176
echo ============================================
echo.
echo Abrindo navegador...
start http://localhost:5176

echo.
echo Pressione QUALQUER TECLA para fechar esta janela...
pause >nul
