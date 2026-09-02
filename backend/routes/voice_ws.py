"""
DEEP-OS — WebSocket de voz com Gemini Live API.
"""
import asyncio
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("voicews")

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

router = APIRouter()

LIVE_MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"

_root = str(Path(__file__).resolve().parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

GEMINI_VOICES = {
    "charon": "Charon", "puck": "Puck", "kore": "Kore",
    "fenrir": "Fenrir", "leda": "Leda", "orus": "Orus",
    "aoede": "Aoede", "zephyr": "Zephyr",
}


def _resolve_voice(voice: str) -> str:
    """Resolve nome da voz (case-insensitive)."""
    return GEMINI_VOICES.get(voice.lower(), voice)


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
    from actions.download_image import download_image
    from actions.dev_agent import dev_agent
    from actions.computer_control import computer_control
    from actions.game_updater import game_updater
    from actions.flight_finder import flight_finder
    from actions.file_processor import file_processor
    from actions.system_monitor import get_system_status
    from actions.background_monitor import add_monitor, remove_monitor, list_monitors
    _ACTIONS_OK = True
    logger.info("Todas as 20 actions importadas com sucesso")
except ImportError as e:
    logger.warning(f"nem todas as actions foram importadas: {e}")

# ── Imports das Tools do DEEP-OS ──────────────────────────────────────────
_TOOLS_OK = False
try:
    from tools.system_tools import tool_read, tool_write
    from tools.file_edit import tool_file_edit
    from tools.web_fetch import tool_web_fetch
    from tools.explorer import resolve_path
    _TOOLS_OK = True
    print("[VoiceWS] Tools do DEEP-OS importadas com sucesso")
except ImportError as e:
    print(f"[VoiceWS] Aviso: tools do DEEP-OS nao importadas: {e}")

try:
    from memory.config_manager import get_brief_enabled
    _BRIEF_OK = True
except ImportError:
    _BRIEF_OK = False


# ── TOOL DECLARATIONS (3 niveis) ──────────────────────────────────────────────

# BASIC: 18 tools - Estabilidade minima
BASIC_TOOL_DECLARATIONS = [
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
            "required": ["receiver", "message_text"]
        }
    },
    {
        "name": "reminder",
        "description": "Cria lembretes. Use para agendar tarefas, alarmes ou avisos futuros.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "text":    {"type": "STRING", "description": "Texto do lembrete"},
                "time":    {"type": "STRING", "description": "Hora para o lembrete (ex: '14:30', 'em 2 horas')"},
                "date":    {"type": "STRING", "description": "Data (ex: 'amanha', '2026-08-28')"},
                "repeat":  {"type": "STRING", "description": "Repetir: daily, weekly, monthly"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "youtube_video",
        "description": "Busca e abre videos do YouTube. Use quando o usuario quiser assistir, pesquisar ou ouvir musicas no YouTube.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Busca no YouTube"},
                "action": {"type": "STRING", "description": "search (padrao) ou open (abrir video especifico)"},
                "video_id": {"type": "STRING", "description": "ID do video para open"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "screen_process",
        "description": "Captura e processa tela ou camera. Use para ver o que esta na tela, tirar screenshot, ou analisar camera.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "source": {"type": "STRING", "description": "screen (tela) ou camera"},
                "action": {"type": "STRING", "description": "capture (captura), analyze (analisa), record (grava)"}
            },
            "required": ["source"]
        }
    },
    {
        "name": "computer_settings",
        "description": "Configuracoes do sistema: volume, brilho, wifi, bluetooth, bateria, modo aviao, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "Acao a executar"},
                "description": {"type": "STRING", "description": "Descricao em linguagem natural"},
                "value":       {"type": "STRING", "description": "Valor opcional: nivel de volume, texto, etc."}
            },
            "required": ["action"]
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
                "task":   {"type": "STRING", "description": "Tarefa da area de trabalho em linguagem natural"}
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
            "required": ["action", "description"]
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
            "required": ["file_path"]
        }
    },
    {
        "name": "bash",
        "description": "Executa comandos no terminal. Use para rodar qualquer comando do sistema.",
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
        "description": "Le o conteudo de um arquivo ou lista uma pasta.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Caminho do arquivo ou pasta"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "download_image",
        "description": "Baixa uma imagem de uma URL e salva localmente. Retorna o caminho do arquivo. Use quando o usuario quiser baixar, salvar ou copiar uma imagem da internet.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url":      {"type": "STRING", "description": "URL da imagem para baixar"},
                "save_path":{"type": "STRING", "description": "Caminho para salvar (pasta ou arquivo). Vazio = pasta padrao downloads"},
                "filename": {"type": "STRING", "description": "Nome do arquivo (sem extensao). Vazio = nome automatico"}
            },
            "required": ["url"]
        }
    },
]

# MEDIUM: 18 tools - Equilibrio (recomendado)
MEDIUM_TOOL_DECLARATIONS = [
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
            "required": ["receiver", "message_text"]
        }
    },
    {
        "name": "reminder",
        "description": "Cria lembretes. Use para agendar tarefas, alarmes ou avisos futuros.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "text":    {"type": "STRING", "description": "Texto do lembrete"},
                "time":    {"type": "STRING", "description": "Hora para o lembrete (ex: '14:30', 'em 2 horas')"},
                "date":    {"type": "STRING", "description": "Data (ex: 'amanha', '2026-08-28')"},
                "repeat":  {"type": "STRING", "description": "Repetir: daily, weekly, monthly"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "youtube_video",
        "description": "Busca e abre videos do YouTube. Use quando o usuario quiser assistir, pesquisar ou ouvir musicas no YouTube.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Busca no YouTube"},
                "action": {"type": "STRING", "description": "search (padrao) ou open (abrir video especifico)"},
                "video_id": {"type": "STRING", "description": "ID do video para open"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "screen_process",
        "description": "Captura e processa tela ou camera. Use para ver o que esta na tela, tirar screenshot, ou analisar camera.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "source": {"type": "STRING", "description": "screen (tela) ou camera"},
                "action": {"type": "STRING", "description": "capture (captura), analyze (analisa), record (grava)"}
            },
            "required": ["source"]
        }
    },
    {
        "name": "computer_settings",
        "description": "Configuracoes do sistema: volume, brilho, wifi, bluetooth, bateria, modo aviao, etc.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "Acao a executar"},
                "description": {"type": "STRING", "description": "Descricao em linguagem natural"},
                "value":       {"type": "STRING", "description": "Valor opcional: nivel de volume, texto, etc."}
            },
            "required": ["action"]
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
                "task":   {"type": "STRING", "description": "Tarefa da area de trabalho em linguagem natural"}
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
            "required": ["action", "description"]
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
             "required": ["file_path"]
        }
    },
    {
        "name": "bash",
        "description": "Executa comandos no terminal. Use para rodar qualquer comando do sistema.",
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
        "description": "Le o conteudo de um arquivo ou lista uma pasta.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Caminho do arquivo ou pasta"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "download_image",
        "description": "Baixa uma imagem de uma URL e salva localmente. Retorna o caminho do arquivo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url":      {"type": "STRING", "description": "URL da imagem para baixar"},
                "save_path":{"type": "STRING", "description": "Caminho para salvar"},
                "filename": {"type": "STRING", "description": "Nome do arquivo"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "write_file",
        "description": "Cria ou sobrescreve um arquivo.",
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
        "description": "Edita um arquivo fazendo find-and-replace.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Caminho do arquivo"},
                "old_string": {"type": "STRING", "description": "Texto para encontrar"},
                "new_string": {"type": "STRING", "description": "Texto novo"}
            },
            "required": ["path", "old_string", "new_string"]
        }
    },
    {
        "name": "web_fetch",
        "description": "Busca o conteudo de uma URL como texto.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url": {"type": "STRING", "description": "URL para buscar"}
            },
            "required": ["url"]
        }
    },
]

# FULL: 25 tools - Completo (todas as anteriores + extras)
# ── TOOLS EXTRAS (ativas quando charon_toolset: full) ────────────────────────
EXTRA_TOOL_DECLARATIONS = [
    {
        "name": "save_document",
        "description": "Salva um documento organizado em C:\\DEEP-OS\\docs\\.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "Titulo do documento"},
                "content": {"type": "STRING", "description": "Conteudo do documento"},
                "path": {"type": "STRING", "description": "Caminho completo (opcional)"},
                "category": {"type": "STRING", "description": "Categoria: relatorios, notas, codigos"},
                "format": {"type": "STRING", "description": "Formato: md, txt, html, json"}
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "memory_save",
        "description": "Salva informacao na memoria de longo prazo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "namespace": {"type": "STRING", "description": "Categoria: preferences, projects, notes"},
                "key": {"type": "STRING", "description": "Chave unica"},
                "content": {"type": "STRING", "description": "Conteudo para salvar"}
            },
            "required": ["namespace", "key", "content"]
        }
    },
    {
        "name": "memory_recall",
        "description": "Le informacao da memoria de longo prazo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "namespace": {"type": "STRING", "description": "Categoria"},
                "key": {"type": "STRING", "description": "Chave do dado"}
            },
            "required": ["namespace", "key"]
        }
    },
]

_toolset_cache = {"value": None, "mtime": 0.0}


def _get_charon_toolset() -> str:
    """Le config de toolset do config.yaml (com cache)."""
    try:
        cfg_path = Path(__file__).resolve().parent.parent.parent / "config.yaml"
        if cfg_path.exists():
            mtime = cfg_path.stat().st_mtime
            if mtime == _toolset_cache["mtime"] and _toolset_cache["value"]:
                return _toolset_cache["value"]
            import yaml
            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
            value = cfg.get("voice", {}).get("charon_toolset", "basic")
            _toolset_cache["value"] = value
            _toolset_cache["mtime"] = mtime
            return value
    except Exception:
        pass
    return _toolset_cache["value"] or "basic"


def _get_active_tools() -> list:
    """Retorna tools ativas baseado na configuracao."""
    toolset = _get_charon_toolset()
    if toolset == "full":
        print(f"[VoiceWS] Toolset: FULL ({len(MEDIUM_TOOL_DECLARATIONS) + len(EXTRA_TOOL_DECLARATIONS)} tools)")
        return MEDIUM_TOOL_DECLARATIONS + EXTRA_TOOL_DECLARATIONS
    elif toolset == "medium":
        print(f"[VoiceWS] Toolset: MEDIUM ({len(MEDIUM_TOOL_DECLARATIONS)} tools)")
        return MEDIUM_TOOL_DECLARATIONS
    else:
        print(f"[VoiceWS] Toolset: BASIC ({len(BASIC_TOOL_DECLARATIONS)} tools)")
        return BASIC_TOOL_DECLARATIONS


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


_identity_cache = {}
_identity_cache_time = 0

def _load_identity() -> dict:
    """Carrega identity do config.yaml com cache."""
    global _identity_cache, _identity_cache_time
    import time
    now = time.time()
    if _identity_cache and (now - _identity_cache_time) < 5:
        return _identity_cache
    try:
        import yaml
        config_path = Path(__file__).resolve().parent.parent.parent / "config.yaml"
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        result = data.get("identity", {})
        _identity_cache = result
        _identity_cache_time = now
        return result
    except Exception:
        return {}


def _build_system_instruction(voice_name: str = "Charon") -> str:
    project_ctx = _load_project_context()
    context_block = f"\n\n--- CONTEXTO ---\n{project_ctx}" if project_ctx else ""
    toolset = _get_charon_toolset()
    tool_count = len(_get_active_tools())
    
    identity = _load_identity()
    assistant_name = identity.get("assistant_name", "") or voice_name
    user_name = identity.get("user_name", "") or ""
    
    print(f"[VoiceWS] Identity: assistant={assistant_name}, user={user_name or '(vazio)'}, tools={tool_count}")

    base = (
        f"Nome: {assistant_name}. Usuario: {user_name}. "
        f"Portugues brasileiro, direto, util, respostas curtas. "
        f"Use tools sempre ({tool_count} tools, {toolset}). "
        f"Se tool falhar, diga erro. Nao reinicie conversa. Mantenha contexto."
    )

    if toolset == "full":
        base += " Docs: save_document. Cod: bash/read/write/edit."

    return base + context_block


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
        self._briefing_sent = False
        self._receive_task: asyncio.Task | None = None
        self._keepalive_task: asyncio.Task | None = None
        self._last_response_time = asyncio.get_event_loop().time()
        self._last_audio_sent_time = 0
        self._reconnecting = False
        self._interrupted = False
        self._audio_buffer: list[bytes] = []

    async def start(self, voice: str = "Charon"):
        if self._running:
            return False

        t_start = asyncio.get_event_loop().time()
        api_key = _get_gemini_key()
        if not api_key or api_key == "cole_sua_chave_aqui":
            await self.ws.send_json({"type": "error", "message": "GEMINI_API_KEY nao configurada"})
            return False

        self._voice = _resolve_voice(voice)
        await self.ws.send_json({"type": "status", "message": "Conectando ao Gemini..."})

        sys_instr = _build_system_instruction(self._voice)
        t_sys = (asyncio.get_event_loop().time() - t_start) * 1000
        print(f"[VoiceWS] System instruction pronta em {t_sys:.0f}ms ({len(sys_instr)} chars)")

        try:
            self.client = genai.Client(api_key=api_key)
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                output_audio_transcription={},
                input_audio_transcription={},
                system_instruction=sys_instr,
                tools=[types.Tool(function_declarations=_get_active_tools())],
                session_resumption=types.SessionResumptionConfig(),
                context_window_compression=types.ContextWindowCompressionConfig(
                    sliding_window=types.SlidingWindow(),
                ),
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self._voice)
                    )
                ),
            )
            active_tools = _get_active_tools()
            print(f"[VoiceWS] Conectando ao Gemini Live com {len(active_tools)} ferramentas...")
            self._cm = self.client.aio.live.connect(model=LIVE_MODEL, config=config)
            self.session = await asyncio.wait_for(self._cm.__aenter__(), timeout=15)
            t_conn = (asyncio.get_event_loop().time() - t_start) * 1000
            self._running = True
            self._last_response_time = asyncio.get_event_loop().time()
            print(f"[VoiceWS] Conectado em {t_conn:.0f}ms! Voz: {self._voice} | Actions OK: {_ACTIONS_OK}")

            self._receive_task = asyncio.create_task(self._receive_loop())
            self._keepalive_task = asyncio.create_task(self._keepalive_loop())
            if not self._briefing_sent and (not _BRIEF_OK or get_brief_enabled()):
                self._briefing_sent = True
                asyncio.create_task(self._send_startup_briefing())

            await self.ws.send_json({
                "type": "connected",
                "voice": self._voice,
                "preset": voice,
                "tools": len(active_tools),
            })
            return True
        except asyncio.TimeoutError:
            print(f"[VoiceWS] TIMEOUT ao conectar ao Gemini (15s)")
            await self.ws.send_json({"type": "error", "message": "Timeout: Gemini nao respondeu em 15s. Verifique a API key."})
            return False
        except Exception as e:
            print(f"[VoiceWS] ERRO ao conectar: {e}")
            traceback.print_exc()
            await self.ws.send_json({"type": "error", "message": str(e)})
            return False

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

    async def send_audio(self, audio_data: bytes):
        if not self.session or not self._running:
            print("[VoiceWS] send_audio: sessao nao esta pronta")
            return
        try:
            t0 = asyncio.get_event_loop().time()
            await self.session.send_realtime_input(
                media={"data": audio_data, "mime_type": "audio/pcm;rate=16000"}
            )
            elapsed = (asyncio.get_event_loop().time() - t0) * 1000
            if elapsed > 200:
                print(f"[VoiceWS] send_audio lento: {elapsed:.0f}ms ({len(audio_data)} bytes)")
            self._last_audio_sent_time = asyncio.get_event_loop().time()
            self._interrupted = False
        except Exception as e:
            print(f"[VoiceWS] Erro ao enviar audio: {e}")
            if "closed" in str(e).lower() or "disconnect" in str(e).lower():
                print("[VoiceWS] Sessao Gemini parece morta. Tentando reconexao...")
                try:
                    await self.ws.send_json({"type": "error", "message": "Sessao Gemini encerrada. Reconectando..."})
                except Exception:
                    pass
                asyncio.create_task(self._reconnect())

    async def _execute_tool(self, fc) -> types.FunctionResponse:
        name = fc.name
        args = dict(fc.args or {})
        t0 = asyncio.get_event_loop().time()
        print(f"[VoiceWS] Tool call: {name} {args}")

        # Notifica frontend que esta processando
        try:
            await self.ws.send_json({"type": "transcript", "speaker": "Charon", "text": f"Processando {name}..."})
        except Exception:
            pass

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
                # code_helper precisa de file_path ou code
                if not args.get("file_path") and not args.get("code"):
                    result = "Para usar code_helper, forneça: file_path (caminho do arquivo) OU code (codigo para executar). Exemplo: code_helper action='run' file_path='C:\\teste.py'"
                else:
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

            elif name == "download_image":
                url = args.get("url", "")
                save_path = args.get("save_path", "")
                filename = args.get("filename", "")
                r = await loop.run_in_executor(None, lambda: download_image(url=url, save_path=save_path, filename=filename))
                result = r or "Done."

            # ── NOVAS FERRAMENTAS (DEEP-OS Tools) ─────────────────────────────
            elif name == "bash":
                import subprocess
                cmd = args.get("command", "")
                workdir = args.get("workdir", None)
                # Notifica frontend que esta processando
                try:
                    await self.ws.send_json({"type": "transcript", "speaker": "Charon", "text": "Executando comando..."})
                except Exception:
                    pass
                try:
                    r = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=30,
                        cwd=workdir
                    )
                    result = r.stdout[:2000] if r.returncode == 0 else f"Erro: {r.stderr[:2000]}"
                except subprocess.TimeoutExpired:
                    result = "Timeout: comando demorou mais de 30 segundos"
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

            elif name == "save_document":
                title = args.get("title", "documento")
                content = args.get("content", "")
                custom_path = args.get("path", "").strip()
                category = args.get("category", "notas")
                fmt = args.get("format", "md").lower().strip()
                # Sanitiza o titulo para usar como nome de arquivo
                safe_title = "".join(c if c.isalnum() or c in " _-" else "" for c in title)
                safe_title = safe_title.strip().replace(" ", "_")[:60]
                # Mapeia formato para extensao
                ext_map = {"md": ".md", "txt": ".txt", "doc": ".doc", "html": ".html", "json": ".json"}
                ext = ext_map.get(fmt, ".md")
                # Determina o caminho final
                if custom_path:
                    # Usuario pediu caminho especifico
                    filepath = Path(custom_path)
                    if not filepath.suffix:
                        filepath = filepath.with_suffix(ext)
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Caminho padrao organizado
                    from datetime import datetime as _dt
                    today = _dt.now()
                    docs_dir = Path("C:/DEEP-OS/docs") / category
                    docs_dir.mkdir(parents=True, exist_ok=True)
                    filename = f"{today.strftime('%Y%m%d')}_{safe_title}{ext}"
                    filepath = docs_dir / filename
                # Monta conteudo formatado
                from datetime import datetime as _dt
                today = _dt.now()
                header_md = f"# {title}\n\n"
                if category != "notas":
                    header_md += f"> Categoria: {category.title()}\n"
                header_md += f"> Criado em: {today.strftime('%d/%m/%Y %H:%M')}\n\n---\n\n"
                if fmt == "json":
                    import json as _json
                    doc_data = {"title": title, "category": category, "created": today.isoformat(), "content": content}
                    final_content = _json.dumps(doc_data, ensure_ascii=False, indent=2)
                elif fmt == "html":
                    lines_html = content.replace("\n", "<br>\n")
                    final_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>{title}</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; }}
h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
.meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
hr {{ border: 1px solid #eee; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="meta">Categoria: {category.title()} | Criado: {today.strftime('%d/%m/%Y %H:%M')}</div>
<hr>
{lines_html}
</body>
</html>"""
                elif fmt == "doc":
                    lines_doc = content.replace("\n", "<br>\n")
                    final_content = f"<html><head><meta charset='UTF-8'><title>{title}</title></head><body><h1>{title}</h1><hr>{lines_doc}</body></html>"
                elif fmt == "txt":
                    final_content = f"{title}\n{'='*len(title)}\n\n{content}"
                else:  # md
                    final_content = header_md + content
                filepath.write_text(final_content, encoding="utf-8")
                result = f"Documento salvo em: {filepath}"
                print(f"[VoiceWS] Documento salvo ({fmt}): {filepath}")

            # ── Tools extras (full toolset) ──────────────────────────────────────
            elif name == "bash":
                import subprocess
                cmd = args.get("command", "")
                workdir = args.get("workdir", None)
                try:
                    await self.ws.send_json({"type": "transcript", "speaker": "Charon", "text": "Executando comando..."})
                except Exception:
                    pass
                try:
                    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=workdir)
                    result = r.stdout[:2000] if r.returncode == 0 else f"Erro: {r.stderr[:2000]}"
                except subprocess.TimeoutExpired:
                    result = "Timeout: comando demorou mais de 30 segundos"
                except Exception as e:
                    result = f"Erro: {e}"

            elif name == "file_edit":
                from tools.file_edit import tool_file_edit
                path = args.get("path", "")
                old = args.get("old_string", "")
                new = args.get("new_string", "")
                r = await tool_file_edit(path, old, new)
                result = r.get("message", str(r))

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
                mem[ns][key] = {"value": content, "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                save_memory(mem)
                result = f"Salvo em {ns}/{key}"

            elif name == "memory_recall":
                from memory.memory_manager import load_memory
                ns = args.get("namespace", "notes")
                key = args.get("key", "")
                mem = load_memory()
                entry = mem.get(ns, {}).get(key, {})
                result = entry.get("value", f"Nenhum dado em {ns}/{key}")

            else:
                result = f"Unknown tool: {name}"

        except Exception as e:
            result = f"Tool '{name}' failed: {e}"
            traceback.print_exc()

        elapsed = (asyncio.get_event_loop().time() - t0) * 1000
        print(f"[VoiceWS] Tool result: {name} -> {str(result)[:100]} ({elapsed:.0f}ms)")

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
        await asyncio.sleep(2)
        if not self.session or not self._running:
            return

        time_str = datetime.now().strftime("%H:%M")
        hour = datetime.now().hour
        greeting = "Bom dia" if hour < 12 else ("Boa tarde" if hour < 18 else "Boa noite")

        identity = _load_identity()
        assistant_name = identity.get("assistant_name", "") or self._voice
        user_name = identity.get("user_name", "") or ""

        saudacao = f"{greeting}, {user_name}. " if user_name else f"{greeting}. "
        p1 = (
            f"{saudacao}Sao {time_str}. "
            f"Sou o {assistant_name}, seu assistente de voz. "
            f"Como posso ajudar?"
        )

        print(f"[VoiceWS] Enviando briefing: {p1}")
        self._turn_done_event.clear()
        try:
            await self.session.send_client_content(
                turns={"parts": [{"text": p1}]},
                turn_complete=True,
            )
        except Exception as e:
            print(f"[VoiceWS] Erro ao enviar briefing: {e}")

    async def _handle_response(self, response) -> None:
        if not self._running:
            return

        # Log detalhado do que foi recebido
        if response.server_content:
            sc = response.server_content
            has_data = bool(response.data)
            has_tool = bool(response.tool_call)
            has_turn_complete = bool(sc.turn_complete) if sc else False
            now = asyncio.get_event_loop().time()
            delay_ms = (now - self._last_response_time) * 1000
            print(f"[VoiceWS] Recebido: data={has_data}, tool={has_tool}, turn_complete={has_turn_complete} (delay={delay_ms:.0f}ms)")

        if response.data:
            if self._interrupted:
                pass  # discard old audio only
            else:
                try:
                    await self.ws.send_bytes(response.data)
                except Exception as e:
                    print(f"[VoiceWS] Erro ao enviar audio (ignorado): {e}")

        if response.server_content:
            sc = response.server_content

            # Skip OLD transcriptions (user already speaking new message)
            # but KEEP turn_complete to reset state
            if self._interrupted:
                if sc.turn_complete:
                    self._interrupted = False
                return

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
                try:
                    await self.ws.send_json({"type": "status", "message": f"Executando {fc.name}..."})
                except Exception:
                    pass
                try:
                    fr = await asyncio.wait_for(self._execute_tool(fc), timeout=20)
                except asyncio.TimeoutError:
                    print(f"[VoiceWS] Tool {fc.name} timeout (20s)")
                    fr = types.FunctionResponse(
                        id=fc.id, name=fc.name,
                        response={"result": f"Timeout: {fc.name} demorou mais de 20 segundos."}
                    )
                except Exception as e:
                    print(f"[VoiceWS] Tool {fc.name} erro: {e}")
                    fr = types.FunctionResponse(
                        id=fc.id, name=fc.name,
                        response={"result": f"Erro ao executar {fc.name}: {str(e)[:200]}"}
                    )
                fn_responses.append(fr)
            try:
                await self.session.send_tool_response(function_responses=fn_responses)
            except Exception as e:
                print(f"[VoiceWS] Erro ao enviar tool_response: {e}")

    async def _receive_loop(self):
        """Escuta respostas do Gemini continuamente."""
        while self._running:
            try:
                async for response in self.session.receive():
                    if not self._running:
                        return
                    self._last_response_time = asyncio.get_event_loop().time()
                    try:
                        await self._handle_response(response)
                    except Exception as e:
                        print(f"[VoiceWS] Erro no _handle_response: {e}")
                        traceback.print_exc()
            except asyncio.CancelledError:
                return
            except Exception as e:
                if not self._running:
                    return
                print(f"[VoiceWS] Receive erro: {e}")
                traceback.print_exc()
                if self._running:
                    asyncio.create_task(self._safe_reconnect())

    def _ensure_receive_loop(self):
        """Reinicia receive se parou (erro de conexao)."""
        if self._receive_task is None or self._receive_task.done():
            if self._running and self.session:
                self._receive_task = asyncio.create_task(self._receive_loop())

    async def _keepalive_loop(self):
        """Verifica se a sessao esta viva e reconecta automaticamente."""
        ping_count = 0
        while self._running:
            try:
                await asyncio.sleep(15)
                if not self._running or not self.session:
                    return

                # Verifica se a receive task ainda esta rodando
                if self._receive_task and self._receive_task.done():
                    print("[VoiceWS] Receive task morta! Tentando reconexao...")
                    await self._reconnect()
                    continue

                # Watchdog: se nao recebe nada por 60s, forca reconexao
                now = asyncio.get_event_loop().time()
                silence_duration = now - self._last_response_time
                if silence_duration > 60:
                    print(f"[VoiceWS] Watchdog: {silence_duration:.0f}s sem resposta. Forcando reconexao...")
                    await self._reconnect()
                    continue

                # Envia ping a cada 45 segundos para manter sessao ativa
                ping_count += 1
                if ping_count >= 3:  # 3 * 15s = 45s
                    ping_count = 0
                    try:
                        silence = b'\x00' * 480  # 15ms de silencio (16kHz 16bit mono)
                        await self.session.send_realtime_input(
                            media={"data": silence, "mime_type": "audio/pcm;rate=16000"}
                        )
                    except Exception as e:
                        print(f"[VoiceWS] Ping falhou, reconectando... ({e})")
                        await self._reconnect()

            except asyncio.CancelledError:
                return
            except Exception as e:
                if self._running:
                    print(f"[VoiceWS] Keepalive erro: {e}")

    async def _safe_reconnect(self):
        """Reconnect seguro — não bloqueia a receive_loop."""
        await asyncio.sleep(1)
        if self._reconnecting:
            return
        await self._reconnect()

    async def _reconnect(self):
        """Reconecta ao Gemini Live quando a sessao expira."""
        if not self._running or self._reconnecting:
            return
        self._reconnecting = True
        try:
            # Cancela tasks antigas
            if self._receive_task and not self._receive_task.done():
                self._receive_task.cancel()
            if self._keepalive_task and not self._keepalive_task.done():
                self._keepalive_task.cancel()

            # Fecha sessao antiga (com timeout para nao travar)
            if self.session:
                try:
                    await asyncio.wait_for(self.session.close(), timeout=5)
                except Exception:
                    pass
            if self._cm:
                try:
                    await asyncio.wait_for(self._cm.__aexit__(None, None, None), timeout=5)
                except Exception:
                    pass
                self._cm = None
            self.session = None

            await asyncio.sleep(2)  # Espera antes de reconectar

            # Client novo a cada reconexao — evita estado stale
            api_key = _get_gemini_key()
            if not api_key or api_key == "cole_sua_chave_aqui":
                print("[VoiceWS] API key nao configurada")
                return

            self.client = genai.Client(api_key=api_key)
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                output_audio_transcription={},
                input_audio_transcription={},
                system_instruction=_build_system_instruction(self._voice),
                tools=[types.Tool(function_declarations=_get_active_tools())],
                session_resumption=types.SessionResumptionConfig(),
                context_window_compression=types.ContextWindowCompressionConfig(
                    sliding_window=types.SlidingWindow(),
                ),
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self._voice)
                    )
                ),
            )
            self._cm = self.client.aio.live.connect(model=LIVE_MODEL, config=config)
            self.session = await self._cm.__aenter__()
            self._last_response_time = asyncio.get_event_loop().time()
            print(f"[VoiceWS] Reconectado! Voz: {self._voice}")

            # Reinicia tasks
            self._receive_task = asyncio.create_task(self._receive_loop())
            self._keepalive_task = asyncio.create_task(self._keepalive_loop())

            # Notifica frontend
            try:
                await self.ws.send_json({"type": "connected", "voice": self._voice, "tools": len(_get_active_tools())})
            except Exception:
                pass
            self._reconnecting = False

        except Exception as e:
            self._reconnecting = False
            print(f"[VoiceWS] Falha na reconexao: {e}")
            traceback.print_exc()
            self._running = False
            try:
                await self.ws.send_json({"type": "error", "message": f"Falha na reconexao: {str(e)[:200]}"})
                await self.ws.send_json({"type": "disconnected"})
            except Exception:
                pass

    async def stop(self):
        self._running = False
        if self._keepalive_task and not self._keepalive_task.done():
            self._keepalive_task.cancel()
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
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


async def disconnect_all_voice_sessions():
    """Desconecta todas as sessoes de voz ativas (usado quando identity muda)."""
    for sid, session in list(_sessions.items()):
        if session._running:
            try:
                await session.stop()
            except Exception:
                pass
    _sessions.clear()


@router.post("/voice/disconnect-all")
async def api_disconnect_all_voice():
    """Endpoint para forçar desconexão de todas as sessoes Charon."""
    await disconnect_all_voice_sessions()
    return {"status": "disconnected"}


@router.websocket("/ws/voice")
async def voice_websocket(ws: WebSocket):
    await ws.accept()
    session = VoiceSession(ws)
    sid = f"voice_{id(ws)}"
    _sessions[sid] = session
    _audio_buffer: list[bytes] = []

    try:
        while True:
            msg = await ws.receive()

            if "bytes" in msg and msg["bytes"]:
                if session._running and session.session:
                    session._interrupted = False
                    await session.send_audio(msg["bytes"])
                else:
                    _audio_buffer.append(msg["bytes"])
                    # Limita buffer a 3 segundos (48kHz/3 = 16kHz, 16bit = 32000 bytes/s)
                    if len(_audio_buffer) > 48:
                        _audio_buffer = _audio_buffer[-48:]
                continue

            if "text" in msg and msg["text"]:
                data = json.loads(msg["text"])
                msg_type = data.get("type", "")

                if msg_type == "start":
                    for old_sid, old_session in list(_sessions.items()):
                        if old_sid != sid and old_session._running:
                            await old_session.stop()
                            _sessions.pop(old_sid, None)
                    identity = _load_identity()
                    voice_from_config = identity.get("voice", "Charon") or "Charon"
                    started = await session.start(voice=voice_from_config)
                    # Envia áudio acumulado no buffer
                    if started and _audio_buffer:
                        print(f"[VoiceWS] Enviando {len(_audio_buffer)} chunks do buffer")
                        for chunk in _audio_buffer:
                            if session._running and session.session:
                                await session.send_audio(chunk)
                        _audio_buffer.clear()

                elif msg_type == "text":
                    if data.get("text") and session.session:
                        try:
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
                            )
                        except Exception:
                            pass

                elif msg_type == "stop":
                    break

                elif msg_type == "interrupt":
                    session._interrupted = True
                    if session.session and session._running:
                        try:
                            await session.session.send_realtime_input(
                                audio={"data": b"", "mime_type": "audio/pcm;rate=16000"},
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
    from core.skill_loader import get_skill_count
    toolset = _get_charon_toolset()
    return {
        "available": bool(key and key != "cole_sua_chave_aqui"),
        "default_voice": "charon",
        "toolset": toolset,
        "tools": len(_get_active_tools()),
        "actions_loaded": _ACTIONS_OK,
        "skills": get_skill_count(),
    }
