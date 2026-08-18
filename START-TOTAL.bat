@echo off
title DEEP-AUREA - Inicializacao Unificada (com GGUF local)
cd /d "%~dp0"

echo ============================================
echo     DEEP-AUREA - Inicializacao Unificada
echo ============================================
echo.

REM 1. Mata processos antigos
echo [1/6] Limpando processos antigos...
<<<<<<< HEAD
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im llama-server.exe >nul 2>&1
=======
taskkill /f /im "llama-server.exe" >nul 2>&1
taskkill /f /im "node.exe" >nul 2>&1
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
timeout /t 2 /nobreak >nul
echo  OK

REM 2. Verifica dependencias
echo [2/6] Verificando dependencias...
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] npm nao encontrado. Instale Node.js.
    pause
    exit /b 1
)
if not exist "venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual nao encontrado em venv\n    pause
    exit /b 1
)
echo  OK

REM 3. Inicia llama-server com GGUF (porta 8080)
echo [3/6] Iniciando llama-server GGUF (porta 8080)...
set "MODEL_GGUF=%~dp0models\gguf\Qwen2.5-7B-Instruct-Q4_K_M.gguf"
if exist "%~dp0bin\vulkan\llama-server.exe" (
<<<<<<< HEAD
    start "LLamaCPP :8080" cmd /c "\"%~dp0bin\vulkan\llama-server.exe\" --model \"%MODEL_GGUF%\" --port 8080 --ctx-size 8192 --host 0.0.0.0"
    timeout /t 3 /nobreak >nul
=======
    start "LLamaCPP :8080" cmd /c "%~dp0bin\vulkan\llama-server.exe" --model "%MODEL_GGUF%" --port 8080 --ctx-size 8192 --host 0.0.0.0
    timeout /t 5 /nobreak >nul
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
    echo  OK
) else (
    echo  AVISO: llama-server.exe nao encontrado em bin\vulkan\
)

REM 4. Inicia Backend (porta 8001)
echo [4/6] Iniciando Backend (FastAPI + WebSocket/PowerShell)...
<<<<<<< HEAD
start "WBC Backend :8001" cmd /c "cd /d "%~dp0backend" && "%~dp0venv\Scripts\python" -m uvicorn main:app --host 0.0.0.0 --port 8001 --log-level warning"
=======
set "BACKEND_DIR=%~dp0backend"
set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
start "WBC Backend :8001" cmd /c "cd /d "%BACKEND_DIR%" && "%PYTHON_EXE%" -m uvicorn main:app --host 0.0.0.0 --port 8001 --log-level warning"
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
timeout /t 4 /nobreak >nul
echo  OK

REM 5. Inicia Frontend (porta 5175)
echo [5/6] Iniciando Frontend (Vite + React)...
<<<<<<< HEAD
start "WBC Frontend :5175" cmd /c "cd /d "%~dp0frontend" && npm run dev"
=======
set "FRONTEND_DIR=%~dp0frontend"
start "WBC Frontend :5175" cmd /c "cd /d "%FRONTEND_DIR%" && npm run dev"
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
timeout /t 3 /nobreak >nul
echo  OK

REM 6. Abre navegador
echo [6/6] Abrindo navegador...
start "" "http://localhost:5175"

echo.
echo ============================================
echo  Tudo pronto!
echo  Backend:    http://localhost:8001
echo  Frontend:   http://localhost:5175
echo  LLamaCPP:   http://localhost:8080/v1
<<<<<<< HEAD
(echo  Modelo GGUF padrao: %MODEL_GGUF%)
=======
echo  Modelo GGUF padrao: %MODEL_GGUF%
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
echo  Terminal Web integrado em /ws/terminal
echo ============================================
echo.
echo  Para encerrar tudo, feche as janelas ou
echo  execute stop.bat
echo.
echo  Pressione qualquer tecla para ocultar esta janela...
pause >nul
exit
