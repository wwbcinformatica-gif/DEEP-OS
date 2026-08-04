@echo off
title DEEP-AUREA â€” START TOTAL
cd /d "%~dp0"

echo ============================================
echo     DEEP-AUREA â€” Inicializacao Unificada
echo ============================================
echo.

REM 1. Mata processos antigos
echo [1/5] Limpando processos antigos...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo  OK

REM 2. Verifica dependencias
echo [2/5] Verificando dependencias...
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] npm nao encontrado. Instale Node.js.
    pause
    exit /b 1
)
if not exist "venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual nao encontrado em venv\
    pause
    exit /b 1
)
echo  OK

REM 3. Inicia Backend (porta 8001)
echo [3/5] Iniciando Backend (FastAPI + WebSocket/PowerShell)...
start "WBC Backend :8001" cmd /c "cd /d "%~dp0backend" && "%~dp0venv\Scripts\python" -m uvicorn main:app --host 0.0.0.0 --port 8001 --log-level warning"
timeout /t 4 /nobreak >nul
echo  OK

REM 4. Inicia Frontend (porta 5175)
echo [4/5] Iniciando Frontend (Vite + React)...
start "WBC Frontend :5175" cmd /c "cd /d "%~dp0frontend" && npm run dev"
timeout /t 3 /nobreak >nul
echo  OK

REM 5. Abre navegador
echo [5/5] Abrindo navegador...
start "" "http://localhost:5175"

echo.
echo ============================================
echo  Tudo pronto!
echo  Backend:  http://localhost:8001
echo  Frontend: http://localhost:5175
echo  Terminal Web integrado em /ws/terminal
echo ============================================
echo.
echo  Para encerrar tudo, feche as janelas ou
echo  execute stop.bat
echo.
echo  Pressione qualquer tecla para ocultar esta janela...
pause >nul
exit
