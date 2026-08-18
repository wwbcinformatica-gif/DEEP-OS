<<<<<<< HEAD
﻿"""
WBC — WebSocket de voz com Gemini Live API.
Todas as 20 ferramentas do WBC-Mark-L portadas para voice.
=======
"""
WBC — WebSocket de voz com Gemini Live API.
33 ferramentas completas: Mark-L + DEEP-AUREA Tools.
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
"""
import asyncio
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

router = APIRouter()

LIVE_MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"

_root = str(Path(__file__).resolve().parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

GEMINI_VOICES = {
    "charon": "Charon", "puck": "Puck", "sage": "Sage",
    "achird": "Achird", "kore": "Kore", "fenrir": "Fenrir",
    "leda": "Leda", "orus": "Orus",
}


def _get_gemini_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if key and key != "cole_sua_chave_aqui":
        return key
    try:
        cfg_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
        if cfg_path.exists():
            return json.loads(cfg_path.read_text(encoding="utf-8")).get("gemini_api_key", "")
    except Exception:
        pass
    return ""


# ── Imports das Actions ───────────────────────────────────────────────────────
_ACTIONS_OK = False
try:
    from actions.open_app import open_app
    from actions.web_search import web_search as web_search_action
    from actions.weather_report import weather_action
    from actions.send_message import send_message
    from actions.reminder import reminder
    from actions.youtube_video import youtube_video
    from actions.screen_processor import _capture_camera, _capture_screen
    from actions.computer_settings import computer_settings
    from actions.browser_control import browser_control
    from actions.file_controller import file_controller
    from actions.desktop import desktop_control
    from actions.code_helper import code_helper
    from actions.dev_agent import dev_agent
    from actions.computer_control import computer_control
    from actions.game_updater import game_updater
    from actions.flight_finder import flight_finder
    from actions.file_processor import file_processor
    from actions.system_monitor import get_system_status
    from actions.background_monitor import add_monitor, remove_monitor, list_monitors
    _ACTIONS_OK = True
    print("[VoiceWS] Todas as 20 actions importadas com sucesso")
except ImportError as e:
    print(f"[VoiceWS] Aviso: nem todas as actions foram importadas: {e}")

<<<<<<< HEAD
=======
# ── Imports das Tools do DEEP-AUREA ──────────────────────────────────────────
_TOOLS_OK = False
try:
    from tools.system_tools import tool_read, tool_write
    from tools.file_edit import tool_file_edit
    from tools.web_fetch import tool_web_fetch
    from tools.explorer import resolve_path
    _TOOLS_OK = True
    print("[VoiceWS] Tools do DEEP-AUREA importadas com sucesso")
except ImportError as e:
    print(f"[VoiceWS] Aviso: tools do DEEP-AUREA nao importadas: {e}")

try:
    from memory.config_manager import get_brief_enabled
    _BRIEF_OK = True
except ImportError:
    _BRIEF_OK = False

>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)

# ── TOOL DECLARATIONS (20 ferramentas) ────────────────────────────────────────
TOOL_DECLARATIONS = [
    {
        "name": "open_app",
        "description": "Abre qualquer aplicativo no computador. Use quando o usuario pedir para abrir, iniciar ou lancar qualquer app, site ou programa.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {"type": "STRING", "description": "Nome do aplicativo (ex: 'WhatsApp', 'Chrome', 'Spotify')"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "web_search",
        "description": "Busca na web. Use para qualquer pergunta sobre fatos atuais, eventos, precos ou topicos. Modos: search (padrao), news (noticias), research (profundo), price (preco), compare (comparacao).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query":  {"type": "STRING", "description": "Consulta de busca"},
                "mode":   {"type": "STRING", "description": "search | news | research | price | compare"},
                "items":  {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Itens para comparar (modo compare)"},
                "aspect": {"type": "STRING", "description": "Aspecto da comparacao: price | specs | reviews | features"},
            },
            "required": ["query"]
        }
    },
    {
        "name": "system_status",
        "description": "Retorna metricas do sistema em tempo real: uso de CPU, RAM, GPU, temperatura, uptime e numero de processos.",
        "parameters": {"type": "OBJECT", "properties": {}}
    },
    {
        "name": "weather_report",
        "description": "Retorna o relatorio do tempo para uma cidade.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "Nome da cidade"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "send_message",
        "description": "Envia uma mensagem de texto via WhatsApp, Telegram ou outra plataforma.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "receiver":     {"type": "STRING", "description": "Nome do destinatario"},
                "message_text": {"type": "STRING", "description": "Texto da mensagem"},
                "platform":     {"type": "STRING", "description": "Plataforma: WhatsApp, Telegram, etc."}
            },
            "required": ["receiver", "message_text", "platform"]
        }
    },
    {
        "name": "reminder",
        "description": "Agenda um lembrete.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "date":    {"type": "STRING", "description": "Data no formato YYYY-MM-DD"},
                "time":    {"type": "STRING", "description": "Hora no formato HH:MM (24h)"},
                "message": {"type": "STRING", "description": "Texto do lembrete"}
            },
            "required": ["date", "time", "message"]
        }
    },
    {
        "name": "youtube_video",
        "description": "Controla YouTube: reproduzir videos, resumir, obter info ou mostrar trending.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "play | summarize | get_info | trending"},
                "query":  {"type": "STRING", "description": "Busca para play"},
                "save":   {"type": "BOOLEAN", "description": "Salvar resumo no Notepad"},
                "region": {"type": "STRING", "description": "Codigo do pais para trending (ex: BR, US)"},
                "url":    {"type": "STRING", "description": "URL do video para get_info"},
            },
            "required": []
        }
    },
    {
        "name": "screen_process",
        "description": "Captura a tela ou webcam e analisa. Use quando o usuario perguntar o que esta na tela ou quiser que voce veja algo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "angle": {"type": "STRING", "description": "screen para capturar display, camera para webcam"},
                "text":  {"type": "STRING", "description": "Pergunta ou instrucao sobre a imagem"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "close_camera",
        "description": "Fecha a visao da camera.",
        "parameters": {"type": "OBJECT", "properties": {}}
    },
    {
        "name": "computer_settings",
        "description": "Controla o computador: volume, brilho, atalhos de teclado, fechar apps, fullscreen, WiFi, reiniciar, desligar, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "Acao a executar"},
                "description": {"type": "STRING", "description": "Descricao em linguagem natural"},
                "value":       {"type": "STRING", "description": "Valor opcional: nivel de volume, texto, etc."}
            },
            "required": []
        }
    },
    {
        "name": "browser_control",
        "description": "Controla navegadores web: abrir sites, buscar, clicar, preencher, scroll, screenshot, navegacao.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":    {"type": "STRING", "description": "go_to | search | click | type | scroll | fill_form | screenshot | back | forward | reload | close"},
                "browser":   {"type": "STRING", "description": "chrome | edge | firefox | opera | brave"},
                "url":       {"type": "STRING", "description": "URL para go_to"},
                "query":     {"type": "STRING", "description": "Busca para search"},
                "selector":  {"type": "STRING", "description": "CSS selector para click/type"},
                "text":      {"type": "STRING", "description": "Texto para digitar ou clicar"},
                "direction": {"type": "STRING", "description": "up | down para scroll"},
                "amount":    {"type": "INTEGER", "description": "Quantidade de scroll (default: 500)"},
                "key":       {"type": "STRING", "description": "Tecla para press (ex: Enter, F5)"},
                "path":      {"type": "STRING", "description": "Caminho para salvar screenshot"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "file_controller",
        "description": "Gerencia arquivos e pastas: listar, criar, deletar, mover, copiar, renomear, ler, escrever, buscar, abrir arquivos (imagens, documentos, pdf, html, txt, xml, doc, etc) com o aplicativo padrao, espaco em disco.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "list | create_file | create_folder | delete | move | copy | rename | read | write | find | largest | disk_usage | info | open"},
                "path":        {"type": "STRING", "description": "Caminho do arquivo/pasta ou atalho: desktop, downloads, documents, home. Para abrir use o caminho completo ou atalho + name"},
                "destination": {"type": "STRING", "description": "Destino para move/copy"},
                "new_name":    {"type": "STRING", "description": "Novo nome para rename"},
                "content":     {"type": "STRING", "description": "Conteudo para create_file/write"},
                "name":        {"type": "STRING", "description": "Nome do arquivo para buscar ou abrir"},
                "extension":   {"type": "STRING", "description": "Extensao para buscar (ex: .pdf)"},
                "count":       {"type": "INTEGER", "description": "Numero de resultados para largest"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "desktop_control",
        "description": "Controla a area de trabalho: papel de parede, organizar, limpar, listar, estatisticas.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "wallpaper | wallpaper_url | organize | clean | list | stats | task"},
                "path":   {"type": "STRING", "description": "Caminho da imagem para wallpaper"},
                "url":    {"type": "STRING", "description": "URL da imagem para wallpaper_url"},
                "mode":   {"type": "STRING", "description": "by_type ou by_date para organize"},
                "task":   {"type": "STRING", "description": "Tarefa da area de trabalho em linguagem natural"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "code_helper",
        "description": "Escreve, edita, explica, executa ou compila arquivos de codigo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "write | edit | explain | run | build | auto"},
                "description": {"type": "STRING", "description": "O que o codigo deve fazer ou que mudanca fazer"},
                "language":    {"type": "STRING", "description": "Linguagem de programacao (default: python)"},
                "output_path": {"type": "STRING", "description": "Onde salvar o arquivo"},
                "file_path":   {"type": "STRING", "description": "Caminho de arquivo existente"},
                "code":        {"type": "STRING", "description": "Codigo bruto para explain"},
                "args":        {"type": "STRING", "description": "Argumentos CLI para run/build"},
                "timeout":     {"type": "INTEGER", "description": "Timeout em segundos (default: 30)"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "dev_agent",
        "description": "Cria projetos completos multi-arquivo do zero: planeja, escreve arquivos, instala deps, executa e corrige erros.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "description":  {"type": "STRING", "description": "O que o projeto deve fazer"},
                "language":     {"type": "STRING", "description": "Linguagem (default: python)"},
                "project_name": {"type": "STRING", "description": "Nome da pasta do projeto"},
                "timeout":      {"type": "INTEGER", "description": "Timeout de execucao em segundos (default: 30)"},
            },
            "required": ["description"]
        }
    },
    {
        "name": "computer_control",
        "description": "Controle direto do computador: digitar, clicar, atalhos, scroll, mover mouse, screenshots, encontrar elementos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "type | click | double_click | right_click | hotkey | press | scroll | move | copy | paste | screenshot | wait | focus_window | screen_find | screen_click"},
                "text":        {"type": "STRING", "description": "Texto para digitar ou colar"},
                "x":           {"type": "INTEGER", "description": "Coordenada X"},
                "y":           {"type": "INTEGER", "description": "Coordenada Y"},
                "keys":        {"type": "STRING", "description": "Combinacao de teclas (ex: ctrl+c)"},
                "key":         {"type": "STRING", "description": "Tecla unica (ex: enter)"},
                "direction":   {"type": "STRING", "description": "up | down | left | right"},
                "amount":      {"type": "INTEGER", "description": "Quantidade de scroll (default: 3)"},
                "seconds":     {"type": "NUMBER",  "description": "Segundos para wait"},
                "title":       {"type": "STRING",  "description": "Titulo da janela para focus_window"},
                "description": {"type": "STRING",  "description": "Descricao do elemento para screen_find/screen_click"},
                "path":        {"type": "STRING",  "description": "Caminho para salvar screenshot"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "game_updater",
        "description": "Ferramenta para Steam/Epic Games: instalar, baixar, atualizar, listar jogos, status de download.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":    {"type": "STRING",  "description": "update | install | list | download_status | schedule | cancel_schedule | schedule_status"},
                "platform":  {"type": "STRING",  "description": "steam | epic | both (default: both)"},
                "game_name": {"type": "STRING",  "description": "Nome do jogo"},
                "app_id":    {"type": "STRING",  "description": "Steam AppID para install"},
                "hour":      {"type": "INTEGER", "description": "Hora para update agendado 0-23 (default: 3)"},
                "minute":    {"type": "INTEGER", "description": "Minuto para update agendado 0-59 (default: 0)"},
                "shutdown_when_done": {"type": "BOOLEAN", "description": "Desligar PC quando download finalizar"},
            },
            "required": []
        }
    },
    {
        "name": "flight_finder",
        "description": "Busca passagens de aviao no Google Flights. Use quando o usuario quiser comprar voos, buscar passagens, ver precos de voos, ou planejar viagem de aviao. SEMPRE use esta ferramenta para qualquer coisa relacionada a voos ou passagens aereas.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "origin":      {"type": "STRING",  "description": "Cidade ou aeroporto de origem (ex: Sao Paulo, GRU, Rio de Janeiro)"},
                "destination": {"type": "STRING",  "description": "Cidade ou aeroporto de destino (ex: Paris, CDG, Madrid)"},
                "date":        {"type": "STRING",  "description": "Data de saida (ex: 2026-09-15, 15 de setembro)"},
                "return_date": {"type": "STRING",  "description": "Data de volta para ida e volta (opcional)"},
                "passengers":  {"type": "INTEGER", "description": "Numero de passageiros (default: 1)"},
                "cabin":       {"type": "STRING",  "description": "Classe: economy | premium | business | first"},
                "save":        {"type": "BOOLEAN", "description": "Salvar resultado no Notepad"},
            },
            "required": ["origin", "destination", "date"]
        }
    },
    {
        "name": "manage_monitor",
        "description": "Adiciona, remove ou lista topicos de monitoramento em background.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "add | remove | list"},
                "topic":  {"type": "STRING", "description": "Topico para monitorar ou parar de monitorar"},
            },
            "required": ["action"]
        }
    },
    {
        "name": "file_processor",
        "description": "Processa arquivos: imagens, PDFs, Word, CSV, JSON, codigo, audio, video, archives. Use quando o usuario quiser processar um arquivo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path":   {"type": "STRING", "description": "Caminho completo do arquivo"},
                "action":      {"type": "STRING", "description": "Acao: describe | ocr | summarize | extract_text | analyze | explain | review | fix | run | transcribe | info"},
                "instruction": {"type": "STRING", "description": "Instrucao livre adicional"},
                "format":      {"type": "STRING", "description": "Formato de destino para conversao"},
                "save":        {"type": "BOOLEAN", "description": "Salvar resultado em arquivo"},
            },
            "required": []
        }
    },
<<<<<<< HEAD
=======
    # ── NOVAS FERRAMENTAS (DEEP-AUREA Tools) ──────────────────────────────────
    {
        "name": "bash",
        "description": "Executa comandos no terminal. Use para rodar qualquer comando do sistema: git, npm, python, dir, cd, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "command": {"type": "STRING", "description": "Comando para executar"},
                "workdir": {"type": "STRING", "description": "Diretorio de trabalho (opcional)"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Le o conteudo de um arquivo ou lista o conteudo de uma pasta. Use para ler codigo, configuracoes, ou qualquer arquivo de texto.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Caminho do arquivo ou pasta"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Cria ou sobrescreve um arquivo. Use para salvar codigo, configuracoes, ou qualquer texto.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Caminho do arquivo"},
                "content": {"type": "STRING", "description": "Conteudo para escrever"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "file_edit",
        "description": "Edita um arquivo fazendo find-and-replace. Precisa do texto exato para encontrar e o texto novo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Caminho do arquivo"},
                "old_string": {"type": "STRING", "description": "Texto para encontrar"},
                "new_string": {"type": "STRING", "description": "Texto novo para substituir"}
            },
            "required": ["path", "old_string", "new_string"]
        }
    },
    {
        "name": "execute_python",
        "description": "Executa codigo Python. Use para testar scripts, processar dados, ou qualquer tarefa Python.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "code": {"type": "STRING", "description": "Codigo Python para executar"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "find_file",
        "description": "Busca arquivos por nome em qualquer unidade. Use para encontrar musicas, videos, documentos, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING", "description": "Nome ou parte do nome do arquivo"},
                "drive": {"type": "STRING", "description": "Unidade (C:, D:). Vazio = todas as unidades"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "glob_search",
        "description": "Busca arquivos por padrao glob (*.py, *.mp3, src/**/*.ts). Mais rapido que find_file para padroes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "pattern": {"type": "STRING", "description": "Padrao glob (*.py, **/*.js)"},
                "path": {"type": "STRING", "description": "Caminho base (opcional)"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "text_search",
        "description": "Busca texto dentro de arquivos usando regex. Use para encontrar funcoes, variaveis, erros, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "pattern": {"type": "STRING", "description": "Texto ou regex para buscar"},
                "path": {"type": "STRING", "description": "Diretorio (opcional, default: projeto atual)"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "open_program",
        "description": "Abre um programa buscando em Program Files, AppData e PATH. Mais robusto que open_app.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {"type": "STRING", "description": "Nome do programa"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "close_program",
        "description": "Fecha um processo pelo nome. Use para fechar programas travados ou indesejados.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "process_name": {"type": "STRING", "description": "Nome do processo (ex: notepad.exe)"}
            },
            "required": ["process_name"]
        }
    },
    {
        "name": "web_fetch",
        "description": "Busca o conteudo de uma URL e retorna como texto. Use para ler artigos, documentacao, APIs, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url": {"type": "STRING", "description": "URL para buscar"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "memory_save",
        "description": "Salva informacao na memoria de longo prazo. Use para lembrar preferencias, dados importantes, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "namespace": {"type": "STRING", "description": "Categoria: preferences, projects, notes, identity"},
                "key": {"type": "STRING", "description": "Chave unica para o dado"},
                "content": {"type": "STRING", "description": "Conteudo para salvar"}
            },
            "required": ["namespace", "key", "content"]
        }
    },
    {
        "name": "memory_recall",
        "description": "Le informacao da memoria de longo prazo. Use para lembrar o que o usuario ja disse ou configurou.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "namespace": {"type": "STRING", "description": "Categoria: preferences, projects, notes, identity"},
                "key": {"type": "STRING", "description": "Chave do dado"}
            },
            "required": ["namespace", "key"]
        }
    },
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
]


# ── System Instruction ────────────────────────────────────────────────────────
_PROJECT_CONTEXT_CACHE: dict = {"mtime": 0.0, "text": ""}


def _load_project_context() -> str:
    """Carrega o CHARON_CONTEXT.md (conhecimento do projeto + desenvolvedor)."""
    try:
        ctx_path = Path(__file__).resolve().parent.parent.parent / "CHARON_CONTEXT.md"
        mtime = ctx_path.stat().st_mtime if ctx_path.exists() else 0.0
        if mtime != _PROJECT_CONTEXT_CACHE["mtime"]:
            _PROJECT_CONTEXT_CACHE["mtime"] = mtime
            _PROJECT_CONTEXT_CACHE["text"] = ctx_path.read_text(encoding="utf-8")
        return _PROJECT_CONTEXT_CACHE["text"]
    except Exception:
        return ""


def _build_system_instruction() -> str:
    project_ctx = _load_project_context()
    context_block = f"\n\n--- CONTEXTO DO PROJETO (use estas informacoes) ---\n{project_ctx}" if project_ctx else ""

    return (
        "Voce e o Charon, assistente de voz do Wilson. "
        "Fale em portugues brasileiro. Seja direto e util. "
<<<<<<< HEAD
        "O usuario e o Wilson Barbosa Coimbra, o desenvolvedor do projeto. "
        "Voce tem acesso a 20 ferramentas para controlar o computador, "
        "buscar na web, gerenciar arquivos, abrir apps, e muito mais. "
        "Use as ferramentas SEMPRE que o usuario pedir. "
        "Nunca invente resultados — execute as ferramentas de verdade. "
        "Se o usuario pedir para abrir um app, use open_app. "
        "Se o usuario pedir para pesquisar, use web_search. "
        "Responda de forma concisa e natural. "
        "Length: short."
=======
        "O usuario e o Wilson Barbosa Coimbra, desenvolvedor do projeto DEEP-AUREA. "
        "Projeto em C:\\DEEP-AUREA. Use caminhos absolutos sempre. "
        "Voce tem 33 ferramentas. Use SEMPRE que o usuario pedir. "
        "Nunca invente resultados. "
        "Responda de forma concisa e natural. "
        "--- DICAS DE USO DAS FERRAMENTAS --- "
        "Para abrir apps: use open_app (ex: open_app app_name='notepad'). "
        "Para configurações do sistema: use computer_settings action='open_settings'. "
        "Para tarefas do sistema: use computer_settings (volume, brilho, wifi, etc). "
        "Para navegador: use browser_control action='search' query='...'. "
        "Para arquivos: use file_controller ou read_file/write_file. "
        "Para código: use bash ou execute_python. "
        "SEMPRE execute as acoes. Nao recuse pedidos. "
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
        f"{context_block}"
    )


# ── VoiceSession ──────────────────────────────────────────────────────────────
class VoiceSession:
    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.client = None
        self.session = None
        self._cm = None
        self._running = False
        self._voice = "Charon"
        self._turn_done_event = asyncio.Event()
<<<<<<< HEAD
=======
        self._briefing_sent = False
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)

    async def start(self, voice: str = "Charon"):
        if self._running:
            return False

        api_key = _get_gemini_key()
        if not api_key or api_key == "cole_sua_chave_aqui":
            await self.ws.send_json({"type": "error", "message": "GEMINI_API_KEY nao configurada"})
            return False

        self._voice = GEMINI_VOICES.get(voice, voice)
        sys_instr = _build_system_instruction()

        try:
            self.client = genai.Client(api_key=api_key)
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                output_audio_transcription={},
                input_audio_transcription={},
                system_instruction=sys_instr,
                tools=[types.Tool(function_declarations=TOOL_DECLARATIONS)],
                session_resumption=types.SessionResumptionConfig(),
                speech_config=types.SpeechConfig(
<<<<<<< HEAD
=======
                    language_code="pt-BR",
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self._voice)
                    )
                ),
            )
            print(f"[VoiceWS] Conectando ao Gemini Live com {len(TOOL_DECLARATIONS)} ferramentas...")
            self._cm = self.client.aio.live.connect(model=LIVE_MODEL, config=config)
            self.session = await self._cm.__aenter__()
            self._running = True
            print(f"[VoiceWS] Conectado! Voz: {self._voice} | Actions OK: {_ACTIONS_OK}")

            asyncio.create_task(self._receive_loop())
<<<<<<< HEAD
            asyncio.create_task(self._send_startup_briefing())
=======
            if not self._briefing_sent and (not _BRIEF_OK or get_brief_enabled()):
                self._briefing_sent = True
                asyncio.create_task(self._send_startup_briefing())
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)

            await self.ws.send_json({
                "type": "connected",
                "voice": self._voice,
                "preset": voice,
                "tools": len(TOOL_DECLARATIONS),
            })
            return True
        except Exception as e:
            print(f"[VoiceWS] ERRO ao conectar: {e}")
            traceback.print_exc()
            await self.ws.send_json({"type": "error", "message": str(e)})
            return False

<<<<<<< HEAD
=======
    async def send_text_chunked(self, text: str):
        MAX_CHUNK = 2000
        if len(text) <= MAX_CHUNK:
            await self.session.send_client_content(
                turns={"parts": [{"text": text}]}, turn_complete=True
            )
            return
        paragraphs = text.split("\n\n")
        chunks = []
        current = ''
        for para in paragraphs:
            if len(current) + len(para) + 2 > MAX_CHUNK:
                if current:
                    chunks.append(current)
                current = para
            else:
                current = current + "\n\n" + para if current else para
        if current:
            chunks.append(current)
        for i, chunk in enumerate(chunks):
            if not self._running:
                break
            await self.session.send_client_content(
                turns={"parts": [{"text": chunk}]},
                turn_complete=(i == len(chunks) - 1)
            )
            if i < len(chunks) - 1:
                await asyncio.sleep(0.2)

>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
    async def send_audio(self, audio_data: bytes):
        if not self.session or not self._running:
            return
        try:
            await self.session.send_realtime_input(
<<<<<<< HEAD
                media={"data": audio_data, "mime_type": "audio/pcm;rate=16000"}
=======
                media={"data": audio_data, "mime_type": "audio/pcm"}
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
            )
        except Exception:
            pass

    async def _execute_tool(self, fc) -> types.FunctionResponse:
        name = fc.name
        args = dict(fc.args or {})
        print(f"[VoiceWS] Tool call: {name} {args}")

        loop = asyncio.get_event_loop()
        result = "Done."

        try:
            if name == "open_app":
                r = await loop.run_in_executor(None, lambda: open_app(parameters=args, response=None, player=None))
                result = r or f"Opened {args.get('app_name')}."

            elif name == "web_search":
                r = await loop.run_in_executor(None, lambda: web_search_action(parameters=args, player=None))
                result = r or "Done."

            elif name == "system_status":
                r = await loop.run_in_executor(None, get_system_status)
                result = str(r)

            elif name == "weather_report":
                r = await loop.run_in_executor(None, lambda: weather_action(parameters=args, player=None))
                result = r or "Weather delivered."

            elif name == "send_message":
                r = await loop.run_in_executor(None, lambda: send_message(parameters=args, response=None, player=None, session_memory=None))
                result = r or f"Message sent to {args.get('receiver')}."

            elif name == "reminder":
                r = await loop.run_in_executor(None, lambda: reminder(parameters=args, response=None, player=None))
                result = r or "Reminder set."

            elif name == "youtube_video":
                r = await loop.run_in_executor(None, lambda: youtube_video(parameters=args, response=None, player=None))
                result = r or "Done."

            elif name == "screen_process":
                angle = args.get("angle", "screen").lower()
                if angle == "camera":
                    img_b, mime_t = await loop.run_in_executor(None, _capture_camera)
                    result = f"Camera captured: {len(img_b)} bytes. Image sent for analysis."
                else:
                    img_b, mime_t = await loop.run_in_executor(None, _capture_screen)
                    result = f"Screen captured: {len(img_b)} bytes. Image sent for analysis."

            elif name == "close_camera":
                result = "Camera closed."

            elif name == "computer_settings":
                r = await loop.run_in_executor(None, lambda: computer_settings(parameters=args, response=None, player=None))
                result = r or "Done."

            elif name == "browser_control":
                r = await loop.run_in_executor(None, lambda: browser_control(parameters=args, player=None))
                result = r or "Done."

            elif name == "file_controller":
                r = await loop.run_in_executor(None, lambda: file_controller(parameters=args, player=None))
                result = r or "Done."

            elif name == "desktop_control":
                r = await loop.run_in_executor(None, lambda: desktop_control(parameters=args, player=None))
                result = r or "Done."

            elif name == "code_helper":
                r = await loop.run_in_executor(None, lambda: code_helper(parameters=args, player=None, speak=None))
                result = r or "Done."

            elif name == "dev_agent":
                r = await loop.run_in_executor(None, lambda: dev_agent(parameters=args, player=None, speak=None))
                result = r or "Done."

            elif name == "computer_control":
                r = await loop.run_in_executor(None, lambda: computer_control(parameters=args, player=None))
                result = r or "Done."

            elif name == "game_updater":
                r = await loop.run_in_executor(None, lambda: game_updater(parameters=args, player=None, speak=None))
                result = r or "Done."

            elif name == "flight_finder":
                r = await loop.run_in_executor(None, lambda: flight_finder(parameters=args, player=None))
                result = r or "Done."

            elif name == "manage_monitor":
                action = args.get("action", "").lower().strip()
                topic = args.get("topic", "").strip()
                if action == "add" and topic:
                    result = await asyncio.to_thread(add_monitor, topic)
                elif action == "remove" and topic:
                    result = await asyncio.to_thread(remove_monitor, topic)
                elif action == "list":
                    topics = await asyncio.to_thread(list_monitors)
                    result = ("Monitoring: " + ", ".join(topics)) if topics else "No topics monitored."
                else:
                    result = "Specify action (add/remove/list) and a topic."

            elif name == "file_processor":
                r = await loop.run_in_executor(None, lambda: file_processor(parameters=args, player=None, speak=None))
                result = r or "Done."

<<<<<<< HEAD
=======
            # ── NOVAS FERRAMENTAS (DEEP-AUREA Tools) ─────────────────────────────
            elif name == "bash":
                import subprocess
                cmd = args.get("command", "")
                workdir = args.get("workdir", None)
                try:
                    r = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=60,
                        cwd=workdir
                    )
                    result = r.stdout if r.returncode == 0 else f"Erro: {r.stderr}"
                except subprocess.TimeoutExpired:
                    result = "Timeout: comando demorou mais de 60 segundos"
                except Exception as e:
                    result = f"Erro ao executar comando: {e}"

            elif name == "read_file":
                from tools.system_tools import tool_read as _tool_read
                path = args.get("path", "")
                r = await _tool_read(path)
                if "error" in r:
                    result = r["error"]
                elif r.get("type") == "directory":
                    items = [i["name"] for i in r.get("items", [])[:50]]
                    result = f"Pasta: {r.get('name', path)}\nItens: {len(items)}\n" + "\n".join(items)
                else:
                    result = r.get("content", str(r))

            elif name == "write_file":
                from tools.system_tools import tool_write as _tool_write
                path = args.get("path", "")
                content = args.get("content", "")
                r = await _tool_write(path, content)
                result = f"Arquivo salvo: {r.get('path', path)}" if r.get("status") == "ok" else str(r)

            elif name == "file_edit":
                from tools.file_edit import tool_file_edit
                path = args.get("path", "")
                old = args.get("old_string", "")
                new = args.get("new_string", "")
                r = await tool_file_edit(path, old, new)
                result = r.get("message", str(r))

            elif name == "execute_python":
                import subprocess
                code = args.get("code", "")
                try:
                    r = subprocess.run(
                        ["python", "-c", code],
                        capture_output=True, text=True, timeout=30
                    )
                    result = r.stdout if r.returncode == 0 else f"Erro: {r.stderr}"
                except subprocess.TimeoutExpired:
                    result = "Timeout: codigo demorou mais de 30 segundos"
                except Exception as e:
                    result = f"Erro: {e}"

            elif name == "find_file":
                import subprocess
                name = args.get("name", "")
                drive = args.get("drive", "C:")
                try:
                    r = subprocess.run(
                        f'where /R {drive}\\ {name} 2>nul',
                        shell=True, capture_output=True, text=True, timeout=30
                    )
                    result = r.stdout[:3000] if r.returncode == 0 else f"Nenhum arquivo encontrado: {name}"
                except Exception as e:
                    result = f"Erro na busca: {e}"

            elif name == "glob_search":
                import subprocess
                pattern = args.get("pattern", "*")
                path = args.get("path", ".")
                try:
                    r = subprocess.run(
                        f'Get-ChildItem -Path "{path}" -Filter "{pattern}" -Recurse -File | Select-Object -First 50 FullName',
                        shell=True, capture_output=True, text=True, timeout=30
                    )
                    result = r.stdout[:3000] if r.stdout.strip() else f"Nenhum arquivo com padrao: {pattern}"
                except Exception as e:
                    result = f"Erro na busca: {e}"

            elif name == "text_search":
                import subprocess
                pattern = args.get("pattern", "")
                path = args.get("path", ".")
                try:
                    r = subprocess.run(
                        f'Select-String -Path "{path}\\*" -Pattern "{pattern}" -Recurse | Select-Object -First 30',
                        shell=True, capture_output=True, text=True, timeout=30
                    )
                    result = r.stdout[:3000] if r.stdout.strip() else f"Nenhum resultado para: {pattern}"
                except Exception as e:
                    result = f"Erro na busca: {e}"

            elif name == "open_program":
                r = await loop.run_in_executor(None, lambda: open_app(parameters={"app_name": args.get("app_name", "")}, response=None, player=None))
                result = r or f"Programa aberto: {args.get('app_name')}"

            elif name == "close_program":
                import subprocess
                proc = args.get("process_name", "")
                try:
                    r = subprocess.run(
                        f"taskkill /F /IM {proc}",
                        shell=True, capture_output=True, text=True, timeout=10
                    )
                    result = f"Processo {proc} finalizado" if r.returncode == 0 else f"Erro: {r.stderr}"
                except Exception as e:
                    result = f"Erro ao fechar processo: {e}"

            elif name == "web_fetch":
                from tools.web_fetch import tool_web_fetch
                url = args.get("url", "")
                r = await tool_web_fetch(url)
                result = r.get("content", str(r))[:3000]

            elif name == "memory_save":
                from memory.memory_manager import load_memory, save_memory
                ns = args.get("namespace", "notes")
                key = args.get("key", "")
                content = args.get("content", "")
                mem = load_memory()
                if ns not in mem:
                    mem[ns] = {}
                mem[ns][key] = {
                    "value": content,
                    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_memory(mem)
                result = f"Salvo em {ns}/{key}"

            elif name == "memory_recall":
                from memory.memory_manager import load_memory
                ns = args.get("namespace", "notes")
                key = args.get("key", "")
                mem = load_memory()
                entry = mem.get(ns, {}).get(key, {})
                result = entry.get("value", f"Nenhum dado encontrado em {ns}/{key}")

>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
            else:
                result = f"Unknown tool: {name}"

        except Exception as e:
            result = f"Tool '{name}' failed: {e}"
            traceback.print_exc()

        print(f"[VoiceWS] Tool result: {name} -> {str(result)[:100]}")

        # Envia o resultado da tool para o frontend exibir no chat
        try:
            await self.ws.send_json({
                "type": "tool_result",
                "tool": name,
                "result": str(result)[:2000],
            })
        except Exception:
            pass

        return types.FunctionResponse(id=fc.id, name=name, response={"result": result})

    async def _send_startup_briefing(self):
<<<<<<< HEAD
        await asyncio.sleep(0.3)
=======
        await asyncio.sleep(1)
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
        if not self.session or not self._running:
            return

        time_str = datetime.now().strftime("%H:%M")
        hour = datetime.now().hour
        greeting = "Bom dia" if hour < 12 else ("Boa tarde" if hour < 18 else "Boa noite")

        p1 = (
            f"{greeting}. Sao {time_str}. "
            f"Sou o Charon, seu assistente de voz. "
            f"Como posso ajudar?"
        )

        self._turn_done_event.clear()
        try:
            await self.session.send_client_content(
                turns={"parts": [{"text": p1}]},
                turn_complete=True,
            )
        except Exception:
            pass

    async def _handle_response(self, response) -> None:
        if not self._running:
            return

        if response.data:
            try:
                await self.ws.send_bytes(response.data)
            except Exception as e:
                print(f"[VoiceWS] Erro ao enviar audio: {e}")
                self._running = False
                return

        if response.server_content:
            sc = response.server_content
            if sc.input_transcription and sc.input_transcription.text:
                try:
                    await self.ws.send_json({
                        "type": "transcript",
                        "speaker": "user",
                        "text": sc.input_transcription.text,
                    })
                except Exception:
                    pass
            if sc.output_transcription and sc.output_transcription.text:
                try:
                    await self.ws.send_json({
                        "type": "transcript",
                        "speaker": "Charon",
                        "text": sc.output_transcription.text,
                    })
                except Exception:
                    pass
            if sc.turn_complete:
                self._turn_done_event.set()
                try:
                    await self.ws.send_json({"type": "turn_complete"})
                except Exception:
                    pass

        if response.tool_call:
            fn_responses = []
            for fc in response.tool_call.function_calls:
                print(f"[VoiceWS] Executando tool: {fc.name}")
                fr = await self._execute_tool(fc)
                fn_responses.append(fr)
            try:
                await self.session.send_tool_response(
                    function_responses=fn_responses
                )
            except Exception as e:
                print(f"[VoiceWS] Erro ao enviar tool_response: {e}")

    async def _receive_loop(self):
        print("[VoiceWS] Receive loop iniciado")
        try:
            while self._running:
                async for response in self.session.receive():
                    if not self._running:
                        break
                    await self._handle_response(response)

        except Exception as e:
            print(f"[VoiceWS] Receive loop erro: {e}")
            traceback.print_exc()
            # Reconexão automática quando a sessão do Gemini cai (ex: 1006 abnormal closure)
            if self._running:
                print("[VoiceWS] Tentando reconectar ao Gemini Live...")
                try:
                    await self.ws.send_json({"type": "error", "message": "Conexao caiu, reconectando..."})
                except Exception:
                    pass
                for attempt in range(5):
                    if not self._running:
                        return
                    await asyncio.sleep(2 * (attempt + 1))
                    try:
                        if self.session:
                            try:
                                await self.session.close()
                            except Exception:
                                pass
                        if self._cm:
                            try:
                                await self._cm.__aexit__(None, None, None)
                            except Exception:
                                pass
                            self._cm = None
                        self._cm = self.client.aio.live.connect(
                            model=LIVE_MODEL,
                            config=types.LiveConnectConfig(
                                response_modalities=["AUDIO"],
                                output_audio_transcription={},
                                input_audio_transcription={},
                                system_instruction=_build_system_instruction(),
                                tools=[types.Tool(function_declarations=TOOL_DECLARATIONS)],
                                session_resumption=types.SessionResumptionConfig(),
                                speech_config=types.SpeechConfig(
<<<<<<< HEAD
=======
                                    language_code="pt-BR",
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
                                    voice_config=types.VoiceConfig(
                                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self._voice)
                                    )
                                ),
                            ),
                        )
                        self.session = await self._cm.__aenter__()
                        self._running = True
                        print(f"[VoiceWS] Reconectado (tentativa {attempt + 1})")
                        await self.ws.send_json({"type": "connected", "voice": self._voice, "preset": self._voice, "tools": len(TOOL_DECLARATIONS)})
<<<<<<< HEAD
                        asyncio.create_task(self._send_startup_briefing())
=======
                        if not self._briefing_sent and (not _BRIEF_OK or get_brief_enabled()):
                            self._briefing_sent = True
                            asyncio.create_task(self._send_startup_briefing())
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
                        # Volta a receber mensagens
                        while self._running:
                            async for response in self.session.receive():
                                if not self._running:
                                    break
                                await self._handle_response(response)
                        return
                    except Exception as re:
                        print(f"[VoiceWS] Falha na reconexao (tentativa {attempt + 1}): {re}")
                self._running = False

    async def stop(self):
        self._running = False
        if self.session:
            try:
                await self.session.close()
            except Exception:
                pass
        if self._cm:
            try:
                await self._cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._cm = None
        self.session = None
        try:
            await self.ws.send_json({"type": "disconnected"})
        except Exception:
            pass


_sessions: dict = {}


@router.websocket("/ws/voice")
async def voice_websocket(ws: WebSocket):
    await ws.accept()
    session = VoiceSession(ws)
    sid = f"voice_{id(ws)}"
    _sessions[sid] = session

    try:
        while True:
            msg = await ws.receive()

            if "bytes" in msg and msg["bytes"]:
                await session.send_audio(msg["bytes"])
                continue

            if "text" in msg and msg["text"]:
                data = json.loads(msg["text"])
                msg_type = data.get("type", "")

                if msg_type == "start":
                    for old_sid, old_session in list(_sessions.items()):
                        if old_sid != sid and old_session._running:
                            await old_session.stop()
                            _sessions.pop(old_sid, None)
                    await session.start(voice=data.get("voice", "Charon"))

                elif msg_type == "text":
                    if data.get("text") and session.session:
                        try:
<<<<<<< HEAD
                            await session.session.send_client_content(
                                turns={"parts": [{"text": data["text"]}]}, turn_complete=True
=======
                            # Injeta skills relevantes na mensagem
                            from core.skill_loader import get_charon_skills_context
                            user_text = data["text"]
                            skills_ctx = get_charon_skills_context(user_text)
                            if skills_ctx:
                                full_text = f"{skills_ctx}\n\nUsuario: {user_text}"
                            else:
                                full_text = user_text
                            await session.session.send_client_content(
                                turns={"parts": [{"text": full_text}]}, turn_complete=True
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
                            )
                        except Exception:
                            pass

                elif msg_type == "stop":
                    break

                elif msg_type == "interrupt":
                    if session.session and session._running:
                        try:
                            await session.session.send_realtime_input(
<<<<<<< HEAD
                                audio={"data": b"", "mime_type": "audio/pcm;rate=16000"},
=======
                                audio={"data": b"", "mime_type": "audio/pcm"},
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
                                interrupt=True,
                            )
                        except Exception:
                            pass
                    session._turn_done_event.set()

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await session.stop()
        _sessions.pop(sid, None)


@router.get("/api/voice/status")
async def voice_status():
    key = _get_gemini_key()
<<<<<<< HEAD
=======
    from core.skill_loader import get_skill_count
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
    return {
        "available": bool(key and key != "cole_sua_chave_aqui"),
        "default_voice": "charon",
        "tools": len(TOOL_DECLARATIONS),
        "actions_loaded": _ACTIONS_OK,
<<<<<<< HEAD
=======
        "skills": get_skill_count(),
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
    }
