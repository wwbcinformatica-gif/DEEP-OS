@echo off
title DEEP-AUREA - ENCERRANDO SISTEMA TOTAL
echo ===================================================
echo [DEEP-AUREA] FORCANDO ENCERRAMENTO DO SISTEMA
echo ===================================================
echo.

echo [1/4] Finalizando processos do Python (Backend e Agentes)...
taskkill /F /IM python.exe /T 2>nul

echo [2/4] Finalizando instÃ¢ncias do Node/Vite (Frontend)...
taskkill /F /IM node.exe /T 2>nul

echo [3/4] Finalizando processos do Ollama (Modelos Locais)...
taskkill /F /IM ollama.exe /T 2>nul
taskkill /F /IM "ollama app.exe" /T 2>nul

echo [4/4] Limpando conexÃµes presas na porta 8001 e 5175...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5175') do taskkill /F /PID %%a 2>nul

echo.
echo [EXTRA] Fechando janelas de comando estaticas e ociosas...
:: Fecha prompts que tenham tÃ­tulos conhecidos ou que ficaram Ã³rfÃ£os
taskkill /F /FI "WINDOWTITLE eq ollama*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Ollama*" 2>nul
taskkill /F /FI "WINDOWTITLE eq FRONTEND*" 2>nul
taskkill /F /FI "WINDOWTITLE eq BACKEND*" 2>nul
taskkill /F /FI "STATUS eq NOT RESPONDING" 2>nul

echo.
echo ===================================================
echo [OK] Sistema totalmente limpo e pronto para o START!
echo ===================================================
echo.
pause
