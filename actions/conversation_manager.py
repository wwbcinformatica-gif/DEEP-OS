"""
conversation_manager.py

Gerenciador de conversas para o agente WBC.

Funções:
- enviar mensagem
- copiar conversa visível
- salvar conversa em TXT
- capturar screenshot
- fazer backup organizado

Observação:
Este módulo trabalha pela interface gráfica (PyAutoGUI).
Ele NÃO acessa bancos de dados privados das plataformas.
A quantidade de mensagens copiadas depende do conteúdo que
a própria interface disponibiliza para seleção.
"""

from pathlib import Path
import importlib.util


_THIS_DIR = Path(__file__).resolve().parent
_SEND_MESSAGE = _THIS_DIR / "send_message.py"

_spec = importlib.util.spec_from_file_location(
    "send_message_module",
    _SEND_MESSAGE,
)

if _spec is None or _spec.loader is None:
    raise ImportError(f"Não foi possível carregar {_SEND_MESSAGE}")

_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)


send_message = _module.send_message
copy_conversation = _module.copy_conversation
screenshot_conversation = _module.screenshot_conversation
backup_conversation = _module.backup_conversation


def execute(action: str, parameters: dict, response=None, player=None, session_memory=None):
    """
    Interface única para o agente.

    action:
      send
      copy
      screenshot
      backup
    """

    action = str(action or "").lower().strip()

    if action == "send":
        return send_message(
            parameters,
            response=response,
            player=player,
            session_memory=session_memory,
        )

    if action == "copy":
        return copy_conversation(
            parameters,
            response=response,
            player=player,
            session_memory=session_memory,
        )

    if action == "screenshot":
        return screenshot_conversation(
            parameters,
            response=response,
            player=player,
            session_memory=session_memory,
        )

    if action == "backup":
        return backup_conversation(
            parameters,
            response=response,
            player=player,
            session_memory=session_memory,
        )

    return (
        f"Ação de conversa desconhecida: {action}. "
        f"Use: send, copy, screenshot ou backup."
    )
