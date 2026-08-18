@echo off
title Importar Modelos Bonsai para Ollama - DEEP-AUREA
cd /d "%~dp0"

echo ==========================================
echo  DEEP-AUREA - Importar Modelos Bonsai
echo ==========================================
echo.

:: Verificar se Ollama esta rodando
echo [1/4] Verificando Ollama...
curl -s http://localhost:11434/api/tags >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERR] Ollama nao detectado!
    echo       Execute: ollama serve
    pause
    exit /b 1
)
echo [OK] Ollama rodando!
echo.

:: Verificar se os modelos ja existem
echo [2/4] Verificando modelos existentes...
ollama list | findstr /i "bonsai-27b" >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Modelos Bonsai ja importados!
    echo.
    ollama list | findstr /i "bonsai"
    echo.
    goto :menu
)

:: Importar Ternary-Bonsai-27B
echo [3/4] Importando Ternary-Bonsai-27B...
set "TERNARY=%~dp0models\ternary-gguf\27B\Ternary-Bonsai-27B-Q2_0.gguf"
if exist "%TERNARY%" (
    echo       Arquivo: %TERNARY%
    echo       Isso pode demorar alguns minutos...
    ollama create bonsai-27b -f Modelfile.bonsai-27b
    if %errorlevel% equ 0 (
        echo [OK] Ternary-Bonsai-27B importado!
    ) else (
        echo [ERR] Falha ao importar
    )
) else (
    echo [WARN] Arquivo nao encontrado:
    echo        %TERNARY%
)
echo.

:: Importar Bonsai-27B (1-bit)
echo [4/4] Importando Bonsai-27B (1-bit)...
set "BONSAI=%~dp0models\gguf\Bonsai-27B-Q1_0.gguf"
if exist "%BONSAI%" (
    echo       Arquivo: %BONSAI%
    echo       Isso pode demorar alguns minutos...
    ollama create bonsai-27b-1bit -f Modelfile.bonsai-27b-1bit
    if %errorlevel% equ 0 (
        echo [OK] Bonsai-27B (1-bit) importado!
    ) else (
        echo [ERR] Falha ao importar
    )
) else (
    echo [WARN] Arquivo nao encontrado:
    echo        %BONSAI%
)
echo.

:menu
echo ==========================================
echo  Modelos Bonsai disponiveis no Ollama:
echo ==========================================
echo.
ollama list | findstr /i "bonsai"
echo.
echo ==========================================
echo  Como usar no DEEP-AUREA:
echo ==========================================
echo.
echo  1. Abra o DEEP-AUREA (START-TOTAL.bat)
echo  2. Va em Configuracoes
echo  3. Mude o Provider para "ollama"
echo  4. Selecione "bonsai-27b" no menu de modelos
echo.
echo  Ou execute diretamente:
echo    ollama run bonsai-27b
echo.
echo ==========================================
pause
