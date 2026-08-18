"""
Teste completo das ferramentas do Charon (Deep-Aurea)
Verifica: imports, tool declarations, execute_tool, e atalhos de teclado
"""
import sys
import os
from pathlib import Path

# Configurar path
_root = str(Path(__file__).resolve().parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

print("=" * 70)
print("TESTE COMPLETO DAS FERRAMENTAS DO CHARON")
print("=" * 70)

# ── 1. Verificar imports das actions ──
print("\n[1] Verificando imports das actions...")
results = {}

try:
    from actions.open_app import open_app
    results["open_app"] = "OK"
except Exception as e:
    results["open_app"] = f"ERRO: {e}"

try:
    from actions.web_search import web_search as web_search_action
    results["web_search"] = "OK"
except Exception as e:
    results["web_search"] = f"ERRO: {e}"

try:
    from actions.weather_report import weather_action
    results["weather_report"] = "OK"
except Exception as e:
    results["weather_report"] = f"ERRO: {e}"

try:
    from actions.send_message import send_message
    results["send_message"] = "OK"
except Exception as e:
    results["send_message"] = f"ERRO: {e}"

try:
    from actions.reminder import reminder
    results["reminder"] = "OK"
except Exception as e:
    results["reminder"] = f"ERRO: {e}"

try:
    from actions.youtube_video import youtube_video
    results["youtube_video"] = "OK"
except Exception as e:
    results["youtube_video"] = f"ERRO: {e}"

try:
    from actions.screen_processor import _capture_camera, _capture_screen
    results["screen_process"] = "OK"
except Exception as e:
    results["screen_process"] = f"ERRO: {e}"

try:
    from actions.computer_settings import computer_settings
    results["computer_settings"] = "OK"
except Exception as e:
    results["computer_settings"] = f"ERRO: {e}"

try:
    from actions.browser_control import browser_control
    results["browser_control"] = "OK"
except Exception as e:
    results["browser_control"] = f"ERRO: {e}"

try:
    from actions.file_controller import file_controller
    results["file_controller"] = "OK"
except Exception as e:
    results["file_controller"] = f"ERRO: {e}"

try:
    from actions.desktop import desktop_control
    results["desktop_control"] = "OK"
except Exception as e:
    results["desktop_control"] = f"ERRO: {e}"

try:
    from actions.code_helper import code_helper
    results["code_helper"] = "OK"
except Exception as e:
    results["code_helper"] = f"ERRO: {e}"

try:
    from actions.dev_agent import dev_agent
    results["dev_agent"] = "OK"
except Exception as e:
    results["dev_agent"] = f"ERRO: {e}"

try:
    from actions.computer_control import computer_control
    results["computer_control"] = "OK"
except Exception as e:
    results["computer_control"] = f"ERRO: {e}"

try:
    from actions.game_updater import game_updater
    results["game_updater"] = "OK"
except Exception as e:
    results["game_updater"] = f"ERRO: {e}"

try:
    from actions.flight_finder import flight_finder
    results["flight_finder"] = "OK"
except Exception as e:
    results["flight_finder"] = f"ERRO: {e}"

try:
    from actions.file_processor import file_processor
    results["file_processor"] = "OK"
except Exception as e:
    results["file_processor"] = f"ERRO: {e}"

try:
    from actions.system_monitor import get_system_status
    results["system_status"] = "OK"
except Exception as e:
    results["system_status"] = f"ERRO: {e}"

try:
    from actions.background_monitor import add_monitor, remove_monitor, list_monitors
    results["manage_monitor"] = "OK"
except Exception as e:
    results["manage_monitor"] = f"ERRO: {e}"

print("\nResultado dos imports:")
for tool, status in sorted(results.items()):
    icon = "[OK]" if "OK" in status else "[ERRO]"
    print(f"  {icon} {tool}: {status}")

ok_count = sum(1 for s in results.values() if "OK" in s)
total = len(results)
print(f"\nTotal: {ok_count}/{total} imports OK")

# ── 2. Verificar tool declarations do voice_ws.py ──
print("\n[2] Verificando TOOL_DECLARATIONS...")
try:
    from backend.routes.voice_ws import TOOL_DECLARATIONS
    print(f"  [OK] TOOL_DECLARATIONS importado: {len(TOOL_DECLARATIONS)} ferramentas")
    
    tool_names = [t["name"] for t in TOOL_DECLARATIONS]
    expected = [
        "open_app", "web_search", "system_status", "weather_report",
        "send_message", "reminder", "youtube_video", "screen_process",
        "close_camera", "computer_settings", "browser_control",
        "file_controller", "desktop_control", "code_helper", "dev_agent",
        "computer_control", "game_updater", "flight_finder",
        "manage_monitor", "file_processor"
    ]
    
    missing = [t for t in expected if t not in tool_names]
    extra = [t for t in tool_names if t not in expected]
    
    if missing:
        print(f"  [ERRO] Ferramentas faltando: {missing}")
    if extra:
        print(f"  [AVISO] Ferramentas extras: {extra}")
    if not missing and not extra:
        print(f"  [OK] Todas as {len(expected)} ferramentas declaradas corretamente")
        
except Exception as e:
    print(f"  [ERRO] Erro ao importar TOOL_DECLARATIONS: {e}")

# ── 3. Verificar browser_control (atalho Shift+W) ──
print("\n[3] Verificando browser_control (atalho Shift+W)...")
try:
    from actions.browser_control import _close_native_tabs
    import inspect
    source = inspect.getsource(_close_native_tabs)
    
    if "shift" in source.lower():
        print("  [OK] Funcao _close_native_tabs encontrada com atalho shift")
        # Verificar se ha problemas conhecidos
        if "ctrl+shift+w" in source.lower():
            print("  [AVISO] ATENCAO: Ctrl+Shift+W pode conflitar com atalhos do sistema")
            print("     Recomendacao: Usar apenas Ctrl+W para fechar aba ativa")
    else:
        print("  [AVISO] Funcao nao usa atalho shift")
        
except Exception as e:
    print(f"  [ERRO] Erro ao verificar browser_control: {e}")

# ── 4. Testar file_controller ──
print("\n[4] Testando file_controller...")
try:
    from actions.file_controller import file_controller, list_files, create_folder
    
    # Teste list_files
    result = list_files("desktop", tts_friendly=True)
    if "Pasta" in result or "Directory" in result or "empty" in result.lower():
        print(f"  [OK] list_files funcionando: {result[:80]}...")
    else:
        print(f"  [AVISO] list_files retornou: {result[:80]}...")
        
except Exception as e:
    print(f"  [ERRO] Erro ao testar file_controller: {e}")

# ── 5. Testar computer_control ──
print("\n[5] Testando computer_control...")
try:
    from actions.computer_control import computer_control, _require_pyautogui
    
    # Verificar se pyautogui está disponível
    try:
        _require_pyautogui()
        print("  [OK] PyAutoGUI disponivel")
    except RuntimeError:
        print("  [AVISO] PyAutoGUI nao instalado (necessario para acoes de teclado/mouse)")
        
except Exception as e:
    print(f"  [ERRO] Erro ao testar computer_control: {e}")

# ── 6. Verificar dependências ──
print("\n[6] Verificando dependencias...")
deps = {
    "psutil": "system_monitor",
    "send2trash": "file_controller (delete)",
    "pyautogui": "computer_control",
    "pyperclip": "computer_control (clipboard)",
}

for pkg, usage in deps.items():
    try:
        __import__(pkg)
        print(f"  [OK] {pkg} ({usage})")
    except ImportError:
        print(f"  [ERRO] {pkg} nao instalado ({usage})")

# ── 7. Verificar permissions ──
print("\n[7] Verificando sistema de permissoes...")
try:
    from core.permissions import is_full_access, get_category_perm
    full_access = is_full_access()
    print(f"  [OK] Permissoes importadas | full_access: {full_access}")
    
    for cat in ["file_controller", "computer_control", "browser_control"]:
        perm = get_category_perm(cat)
        print(f"     {cat}: {perm}")
        
except Exception as e:
    print(f"  [AVISO] Sistema de permissoes: {e}")

# ── Resumo ──
print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"  Imports: {ok_count}/{total} OK")
print(f"  Ferramentas declaradas: {len(TOOL_DECLARATIONS) if 'TOOL_DECLARATIONS' in dir() else 0}/20")
print("\nProblemas conhecidos:")
print("  1. Ctrl+Shift+W (fechar todas as abas) pode conflitar com atalhos do Windows")
print("  2. PyAutoGUI necessário para ações de teclado/mouse")
print("  3. Permissões podem bloquear acesso a certos diretórios")
