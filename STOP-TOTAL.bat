@echo off
chcp 65001 >nul 2>&1
title DEEP-OS - ENCERRANDO SISTEMA
color 0C

echo ===================================================
echo   DEEP-OS - ENCERRANDO SISTEMA
echo ===================================================
echo.

echo [1/4] Finalizando Backend (FastAPI)...
taskkill /FI "WINDOWTITLE eq WBC Backend*" /F >nul 2>&1
:: Mata processos Python que estejam rodando uvicorn na porta 8001
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8001 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo       Backend finalizado

echo [2/4] Finalizando Frontend (Vite/React)...
taskkill /FI "WINDOWTITLE eq WBC Frontend*" /F >nul 2>&1
:: Mata processos Node que estejam rodando na porta 5175
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :5175 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo       Frontend finalizado

echo [3/4] Finalizando llama-server...
taskkill /FI "WINDOWTITLE eq LLamaCPP*" /F >nul 2>&1
taskkill /f /im llama-server.exe >nul 2>&1
echo       llama-server finalizado

echo [4/4] Finalizando Ollama...
taskkill /FI "WINDOWTITLE eq Ollama*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq ollama*" /F >nul 2>&1
echo       Ollama finalizado

echo.
echo ===================================================
echo   Sistema finalizado!
echo ===================================================
echo.
echo   Para reiniciar: START-TOTAL.bat
echo.
pause
