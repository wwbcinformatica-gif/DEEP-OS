@echo off
chcp 65001 >nul 2>&1
title Limpar Memoria - DEEP-AUREA
color 0A

echo ========================================
echo   LIMPAR MEMORIA - DEEP-AUREA
echo ========================================
echo.

:: Mostra uso de memoria antes
echo [ANTES] Uso de memoria:
powershell -NoProfile -Command "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 Name, @{N='MB';E={[math]::Round($_.WorkingSet64/1MB)}} | Format-Table -AutoSize"
echo.

:: Para o llama-server (maior consumidor)
echo [1/4] Parando llama-server...
taskkill /f /im llama-server.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo       ✓ llama-server encerrado
) else (
    echo       - llama-server nao estava rodando
)

:: Para processos Node.js do DEEP-AUREA (frontend dev server)
echo [2/4] Parando processos Node.js...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq node.exe" ^| findstr /i "node.exe"') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo       ✓ processos Node encerrados

:: Limpa cache do Windows
echo [3/4] Limpando cache do Windows...
del /q /s "%TEMP%\*" >nul 2>&1
del /q /s "C:\Windows\Temp\*" >nul 2>&1
echo       ✓ temporarios limpos

:: Forca compactacao de memoria
echo [4/4] Compactando memoria...
powershell -NoProfile -Command "
    $procs = Get-Process | Where-Object {$_.WorkingSet64 -gt 50MB -and $_.Name -notin @('explorer','dwm','csrss','svchost','System','Registry','Idle')}
    foreach ($p in $procs) {
        try {
            $p.Dispose()
        } catch {}
    }
"
echo       ✓ cache liberado

echo.
echo ========================================
echo [DEPOIS] Uso de memoria:
echo ========================================
powershell -NoProfile -Command "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 Name, @{N='MB';E={[math]::Round($_.WorkingSet64/1MB)}} | Format-Table -AutoSize"

echo.
echo ========================================
echo   Limpeza concluida!
echo ========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
