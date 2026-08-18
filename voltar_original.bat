@echo off
cd /d "%~dp0"
set "BASE=%~dp0"

:search
if exist "%BASE%\CHARON_CONTEXT.md" goto :found
if exist "%BASE%\backend\routes\voice_ws.py" goto :found
set "TEMP=%BASE%\.."
if exist "%TEMP%\CHARON_CONTEXT.md" (set "BASE=%TEMP%" & goto :found)
if exist "%TEMP%\backend\routes\voice_ws.py" (set "BASE=%TEMP%" & goto :found)
set "TEMP=%BASE%\..\.."
if exist "%TEMP%\CHARON_CONTEXT.md" (set "BASE=%TEMP%" & goto :found)
if exist "%TEMP%\backend\routes\voice_ws.py" (set "BASE=%TEMP%" & goto :found)
set "TEMP=%BASE%\..\..\.."
if exist "%TEMP%\CHARON_CONTEXT.md" (set "BASE=%TEMP%" & goto :found)
if exist "%TEMP%\backend\routes\voice_ws.py" (set "BASE=%TEMP%" & goto :found)

echo [ERRO] Projeto DEEP-AUREA nao encontrado!
pause
exit /b 1

:found
echo ==========================================
echo  Restaurar nome para: Charon
echo ==========================================
echo.
echo Projeto: %BASE%
echo.

python -c "
import json, os, sys

NEW = 'Charon'
BASE = sys.argv[1]

replacements = [
    ('backend/routes/voice_ws.py', [
        ('Voce e o WBC', 'Voce e o ' + NEW),
        ('Voce e o AUREA', 'Voce e o ' + NEW),
        ('Sou o WBC,', 'Sou o ' + NEW + ','),
        ('Sou o WBC ', 'Sou o ' + NEW + ' '),
        ('Sou o AUREA,', 'Sou o ' + NEW + ','),
        ('Sou o AUREA ', 'Sou o ' + NEW + ' '),
        ('self._voice = \"WBC\"', 'self._voice = \"' + NEW + '\"'),
        ('self._voice = \"AUREA\"', 'self._voice = \"' + NEW + '\"'),
        ('voice: str = \"WBC\"', 'voice: str = \"' + NEW + '\"'),
        ('voice: str = \"AUREA\"', 'voice: str = \"' + NEW + '\"'),
        ('\"default_voice\": \"WBC\"', '\"default_voice\": \"' + NEW.lower() + '\"'),
        ('\"default_voice\": \"wbc\"', '\"default_voice\": \"' + NEW.lower() + '\"'),
        ('\"default_voice\": \"aurea\"', '\"default_voice\": \"' + NEW.lower() + '\"'),
        ('speaker\": \"WBC\"', 'speaker\": \"' + NEW + '\"'),
        ('speaker\": \"AUREA\"', 'speaker\": \"' + NEW + '\"'),
        ('voice\", \"WBC\"', 'voice\", \"' + NEW + '\"'),
        ('voice\", \"wbc\"', 'voice\", \"' + NEW.lower() + '\"'),
        ('voice\", \"AUREA\"', 'voice\", \"' + NEW + '\"'),
        ('voice\", \"aurea\"', 'voice\", \"' + NEW.lower() + '\"'),
    ]),
    ('backend/routes/ws_terminal.py', [
        (\"'WBC:' +\", \"'\" + NEW + \":' +\"),
        (\"'AUREA:' +\", \"'\" + NEW + \":' +\"),
        ('WBC:{workspace_root}', NEW + ':{workspace_root}'),
        ('AUREA:{workspace_root}', NEW + ':{workspace_root}'),
    ]),
    ('backend/routes/terminal.py', [
        ('WBC Agent OS', NEW + ' Agent OS'),
        ('AUREA Agent OS', NEW + ' Agent OS'),
    ]),
    ('frontend/src/components/StatusBar.tsx', [
        ('WBC OFF', NEW + ' OFF'),
        ('WBC ON', NEW + ' ON'),
        ('AUREA OFF', NEW + ' OFF'),
        ('AUREA ON', NEW + ' ON'),
        ('Ligar WBC', 'Ligar ' + NEW),
        ('Ligar AUREA', 'Ligar ' + NEW),
        ('Desligar WBC', 'Desligar ' + NEW),
        ('Desligar AUREA', 'Desligar ' + NEW),
        ('Contexto WBC', 'Contexto ' + NEW),
        ('Contexto AUREA', 'Contexto ' + NEW),
    ]),
    ('frontend/src/components/CharonPanel.tsx', [
        ('\u26a1 WBC', '\u26a1 ' + NEW),
        ('\u26a1 AUREA', '\u26a1 ' + NEW),
        ('WBC ativo', NEW + ' ativo'),
        ('WBC inativo', NEW + ' inativo'),
        ('AUREA ativo', NEW + ' ativo'),
        ('AUREA inativo', NEW + ' inativo'),
        (\"voiceName = 'WBC'\", \"voiceName = '\" + NEW + \"'\"),
        (\"voiceName = 'AUREA'\", \"voiceName = '\" + NEW + \"'\"),
        (\"voiceName = 'Charon'\", \"voiceName = '\" + NEW + \"'\"),
    ]),
    ('frontend/src/components/VoiceHud.tsx', [
        ('>WBC<', '>' + NEW + '<'),
        ('>AUREA<', '>' + NEW + '<'),
        ('>Charon<', '>' + NEW + '<'),
    ]),
    ('frontend/src/components/CharonToolMessage.tsx', [
        ('via WBC', 'via ' + NEW),
        ('via AUREA', 'via ' + NEW),
        ('WBC \u00b7', NEW + ' \u00b7'),
        ('AUREA \u00b7', NEW + ' \u00b7'),
    ]),
    ('frontend/src/components/ChatPanel.tsx', [
        ('/WBC', '/' + NEW),
        ('/AUREA', '/' + NEW),
        ('com o WBC', 'com o ' + NEW),
        ('com o AUREA', 'com o ' + NEW),
    ]),
    ('frontend/src/App.tsx', [
        ('WBC - ASSISTENTE', NEW + ' - ASSISTENTE'),
        ('AUREA - ASSISTENTE', NEW + ' - ASSISTENTE'),
        ('o WBC e o assistente', 'o ' + NEW + ' e o assistente'),
        ('o AUREA e o assistente', 'o ' + NEW + ' e o assistente'),
        ('com o WBC', 'com o ' + NEW),
        ('com o AUREA', 'com o ' + NEW),
        ('painel WBC', 'painel ' + NEW),
        ('painel AUREA', 'painel ' + NEW),
        ('o WBC na barra', 'o ' + NEW + ' na barra'),
        ('o AUREA na barra', 'o ' + NEW + ' na barra'),
        ('o WBC -- ele executa', 'o ' + NEW + ' -- ele executa'),
        ('o AUREA -- ele executa', 'o ' + NEW + ' -- ele executa'),
        ('voiceName=\"WBC\"', 'voiceName=\"' + NEW + '\"'),
        ('voiceName=\"AUREA\"', 'voiceName=\"' + NEW + '\"'),
        (\"voiceName='WBC'\", \"voiceName='\" + NEW + \"'\"),
        (\"voiceName='AUREA'\", \"voiceName='\" + NEW + \"'\"),
        (\"voiceName='Charon'\", \"voiceName='\" + NEW + \"'\"),
        ('voiceName=\"Charon\"', 'voiceName=\"' + NEW + '\"'),
    ]),
]

count = 0
for fpath, reps in replacements:
    full = os.path.join(BASE, fpath)
    if not os.path.exists(full):
        print(f'  [SKIP] {fpath}')
        continue
    content = open(full, 'r', encoding='utf-8').read()
    for old, new in reps:
        content = content.replace(old, new)
    open(full, 'w', encoding='utf-8').write(content)
    print(f'  [OK] {fpath}')
    count += 1

api_file = os.path.join(BASE, 'backend/config/api_keys.json')
if os.path.exists(api_file):
    data = json.load(open(api_file, 'r', encoding='utf-8'))
    data['voice_preset'] = 'charon'
    json.dump(data, open(api_file, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'  [OK] api_keys.json')
    count += 1

print(f'\nPronto! {count} arquivos restaurados para Charon.')
" "%BASE%"

echo.
echo ==========================================
echo  Nome restaurado para: Charon
echo ==========================================
echo.
echo  IMPORTANTE: Reinicie o backend!
echo  STOP-TOTAL.bat depois START-TOTAL.bat
echo.
pause
