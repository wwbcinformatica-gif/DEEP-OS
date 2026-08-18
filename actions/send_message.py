import json
import subprocess
import sys
import time
import webbrowser
import re
import shutil
from datetime import datetime
from pathlib import Path

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.08
    _PYAUTOGUI = True
except ImportError:
    _PYAUTOGUI = False

try:
    import pyperclip
    _PYPERCLIP = True
except ImportError:
    _PYPERCLIP = False


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def _get_os() -> str:
    try:
        cfg = json.loads(
            (_base_dir() / "config" / "api_keys.json").read_text(encoding="utf-8")
        )
        return str(cfg.get("os_system", "windows")).lower().strip()
    except Exception:
        return "windows"


def _require_pyautogui():
    if not _PYAUTOGUI:
        raise RuntimeError("PyAutoGUI não está instalado. Execute: pip install pyautogui")


def _paste_text(text: str) -> None:
    _require_pyautogui()
    paste_hotkey = ("command", "v") if _get_os() == "mac" else ("ctrl", "v")
    if _PYPERCLIP:
        pyperclip.copy(str(text))
        time.sleep(0.12)
        pyautogui.hotkey(*paste_hotkey)
        time.sleep(0.15)
    else:
        pyautogui.write(str(text), interval=0.015)


def _copy_selected_text() -> str:
    _require_pyautogui()
    if not _PYPERCLIP:
        raise RuntimeError("pyperclip é necessário para copiar conversas.")
    hotkey = ("command", "c") if _get_os() == "mac" else ("ctrl", "c")
    pyautogui.hotkey(*hotkey)
    time.sleep(0.4)
    return pyperclip.paste()


def _clear_and_paste(text: str) -> None:
    _require_pyautogui()
    select_all = ("command", "a") if _get_os() == "mac" else ("ctrl", "a")
    pyautogui.hotkey(*select_all)
    time.sleep(0.08)
    pyautogui.press("backspace")
    time.sleep(0.08)
    _paste_text(text)


def _open_app(app_name: str) -> bool:
    _require_pyautogui()
    os_name = _get_os()

    try:
        if os_name == "windows":
            pyautogui.press("win")
            time.sleep(0.5)
            _paste_text(app_name)
            time.sleep(0.8)
            pyautogui.press("enter")
            time.sleep(3.0)
            return True

        if os_name == "mac":
            result = subprocess.run(
                ["open", "-a", app_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                result = subprocess.run(
                    ["open", "-a", f"{app_name}.app"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            time.sleep(3.0)
            return result.returncode == 0

        for launcher in [["gtk-launch", app_name.lower()], [app_name.lower()]]:
            try:
                subprocess.Popen(
                    launcher,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(3.0)
                return True
            except FileNotFoundError:
                continue
        return False

    except Exception as e:
        print(f"[SendMessage] ⚠️ Erro ao abrir {app_name}: {e}")
        return False


def _open_browser_url(url: str) -> bool:
    try:
        result = webbrowser.open(url)
        time.sleep(4.0)
        return bool(result)
    except Exception as e:
        print(f"[SendMessage] ⚠️ Erro ao abrir navegador: {e}")
        return False


def _search_in_app(query: str) -> None:
    _require_pyautogui()
    hotkey = ("command", "f") if _get_os() == "mac" else ("ctrl", "f")
    pyautogui.hotkey(*hotkey)
    time.sleep(0.5)
    _clear_and_paste(query)
    time.sleep(1.0)


def _desktop_send(app_name: str, receiver: str, message: str) -> str:
    if not _open_app(app_name):
        return f"Não foi possível abrir {app_name}."

    _search_in_app(receiver)
    pyautogui.press("enter")
    time.sleep(1.0)
    _paste_text(message)
    time.sleep(0.4)
    pyautogui.press("enter")
    time.sleep(0.8)
    return f"Mensagem enviada para {receiver} via {app_name}."


def _send_whatsapp(receiver: str, message: str) -> str:
    if not _open_app("WhatsApp"):
        return "Não foi possível abrir o WhatsApp."

    try:
        hotkey = ("command", "option", "n") if _get_os() == "mac" else ("ctrl", "alt", "n")
        pyautogui.hotkey(*hotkey)
        time.sleep(1.0)
        _paste_text(receiver)
        time.sleep(1.5)
        pyautogui.press("down")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.2)
        _paste_text(message)
        time.sleep(0.4)
        pyautogui.press("enter")
        time.sleep(0.8)
        return f"Mensagem enviada para {receiver} via WhatsApp."
    except Exception as e:
        return f"Não foi possível enviar pelo WhatsApp: {e}"


def _send_telegram(receiver: str, message: str) -> str:
    if not _open_app("Telegram"):
        return "Não foi possível abrir o Telegram."
    try:
        hotkey = ("command", "k") if _get_os() == "mac" else ("ctrl", "k")
        pyautogui.hotkey(*hotkey)
        time.sleep(0.7)
        _clear_and_paste(receiver)
        time.sleep(1.2)
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(1.2)
        _paste_text(message)
        time.sleep(0.4)
        pyautogui.press("enter")
        time.sleep(0.8)
        return f"Mensagem enviada para {receiver} via Telegram."
    except Exception as e:
        return f"Não foi possível enviar pelo Telegram: {e}"


def _send_signal(receiver: str, message: str) -> str:
    return _desktop_send("Signal", receiver, message)


def _send_discord(receiver: str, message: str) -> str:
    return _desktop_send("Discord", receiver, message)


def _send_instagram(receiver: str, message: str) -> str:
    _require_pyautogui()
    if not _open_browser_url("https://www.instagram.com/direct/new/"):
        return "Não foi possível abrir o Instagram."
    try:
        _paste_text(receiver)
        time.sleep(2.0)
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(1.0)
        for _ in range(4):
            pyautogui.press("tab")
            time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(2.0)
        _paste_text(message)
        pyautogui.press("enter")
        time.sleep(0.8)
        return f"Mensagem enviada para {receiver} via Instagram."
    except Exception as e:
        return f"Não foi possível enviar pelo Instagram: {e}"


def _send_messenger(receiver: str, message: str) -> str:
    _require_pyautogui()
    if not _open_browser_url("https://www.messenger.com/"):
        return "Não foi possível abrir o Messenger."
    try:
        _search_in_app(receiver)
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(1.5)
        _paste_text(message)
        pyautogui.press("enter")
        time.sleep(0.8)
        return f"Mensagem enviada para {receiver} via Messenger."
    except Exception as e:
        return f"Não foi possível enviar pelo Messenger: {e}"


_PLATFORM_MAP = [
    ({"whatsapp", "wp", "wapp"}, _send_whatsapp),
    ({"telegram", "tg"}, _send_telegram),
    ({"instagram", "ig", "insta"}, _send_instagram),
    ({"signal"}, _send_signal),
    ({"discord"}, _send_discord),
    ({"messenger", "facebook", "fb"}, _send_messenger),
]


def _resolve_platform(platform_str: str):
    key = str(platform_str).lower().strip()

    for keywords, handler in _PLATFORM_MAP:
        if any(k == key or k in key for k in keywords):
            return handler

    return lambda r, m: _desktop_send(platform_str.strip().title(), r, m)


def _safe_name(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*]', "_", str(value))
    value = re.sub(r"\s+", " ", value).strip()
    return value[:100] or "conversa"


def _backup_root() -> Path:
    root = _base_dir() / "backups" / "conversations"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _conversation_folder(platform: str, receiver: str) -> Path:
    folder = _backup_root() / _safe_name(platform) / _safe_name(receiver)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _organize_conversation(text: str, platform: str, receiver: str) -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    # Remove excesso de linhas vazias sem destruir a estrutura.
    lines = [line.rstrip() for line in text.split("\n")]
    cleaned = []
    previous_empty = False

    for line in lines:
        empty = not line.strip()
        if empty and previous_empty:
            continue
        cleaned.append(line)
        previous_empty = empty

    body = "\n".join(cleaned).strip()

    return (
        f"============================================================\n"
        f"BACKUP DE CONVERSA\n"
        f"============================================================\n"
        f"PLATAFORMA: {platform}\n"
        f"CONTATO: {receiver}\n"
        f"DATA DO BACKUP: {now}\n"
        f"============================================================\n\n"
        f"{body}\n"
    )


def _save_conversation_text(platform: str, receiver: str, text: str) -> Path:
    folder = _conversation_folder(platform, receiver)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = folder / f"conversa_{timestamp}.txt"

    organized = _organize_conversation(text, platform, receiver)
    path.write_text(organized, encoding="utf-8")

    return path


def _take_screenshot(platform: str, receiver: str) -> Path:
    _require_pyautogui()

    folder = _conversation_folder(platform, receiver)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = folder / f"conversa_{timestamp}.png"

    image = pyautogui.screenshot()
    image.save(path)

    return path


def _copy_visible_conversation() -> str:
    """
    Copia o conteúdo atualmente selecionável na interface.
    O método depende da plataforma e da quantidade de mensagens
    que a interface disponibiliza para seleção.
    """
    _require_pyautogui()

    select_all = ("command", "a") if _get_os() == "mac" else ("ctrl", "a")
    pyautogui.hotkey(*select_all)
    time.sleep(0.3)

    return _copy_selected_text()


def _open_conversation_for_backup(platform: str, receiver: str) -> str:
    """
    Abre a conversa usando o mesmo mecanismo de pesquisa da plataforma.
    """
    platform_key = platform.lower().strip()

    if platform_key in {"whatsapp", "wp", "wapp"}:
        if not _open_app("WhatsApp"):
            raise RuntimeError("Não foi possível abrir o WhatsApp.")

        hotkey = ("command", "option", "n") if _get_os() == "mac" else ("ctrl", "alt", "n")
        pyautogui.hotkey(*hotkey)
        time.sleep(1.0)
        _paste_text(receiver)
        time.sleep(1.5)
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(1.5)
        return "WhatsApp"

    if platform_key in {"telegram", "tg"}:
        if not _open_app("Telegram"):
            raise RuntimeError("Não foi possível abrir o Telegram.")

        hotkey = ("command", "k") if _get_os() == "mac" else ("ctrl", "k")
        pyautogui.hotkey(*hotkey)
        time.sleep(0.7)
        _clear_and_paste(receiver)
        time.sleep(1.2)
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(1.5)
        return "Telegram"

    if platform_key in {"instagram", "ig", "insta"}:
        if not _open_browser_url("https://www.instagram.com/direct/"):
            raise RuntimeError("Não foi possível abrir o Instagram.")

        time.sleep(2.0)
        _search_in_app(receiver)
        pyautogui.press("enter")
        time.sleep(2.0)
        return "Instagram"

    if platform_key in {"messenger", "facebook", "fb"}:
        if not _open_browser_url("https://www.messenger.com/"):
            raise RuntimeError("Não foi possível abrir o Messenger.")

        time.sleep(2.0)
        _search_in_app(receiver)
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(2.0)
        return "Messenger"

    if platform_key == "signal":
        if not _open_app("Signal"):
            raise RuntimeError("Não foi possível abrir o Signal.")

        hotkey = ("command", "k") if _get_os() == "mac" else ("ctrl", "k")
        pyautogui.hotkey(*hotkey)
        time.sleep(0.7)
        _clear_and_paste(receiver)
        time.sleep(1.2)
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(1.5)
        return "Signal"

    if platform_key == "discord":
        if not _open_app("Discord"):
            raise RuntimeError("Não foi possível abrir o Discord.")

        hotkey = ("command", "k") if _get_os() == "mac" else ("ctrl", "k")
        pyautogui.hotkey(*hotkey)
        time.sleep(0.7)
        _clear_and_paste(receiver)
        time.sleep(1.2)
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(1.5)
        return "Discord"

    if not _open_app(platform.title()):
        raise RuntimeError(f"Não foi possível abrir {platform}.")

    time.sleep(1.0)
    _search_in_app(receiver)
    pyautogui.press("enter")
    time.sleep(1.5)
    return platform.title()


def backup_conversation(parameters: dict, response=None, player=None, session_memory=None) -> str:
    """
    Faz backup da conversa visível de um determinado usuário.

    Parâmetros:
      platform: whatsapp/telegram/instagram/messenger/...
      receiver: nome, número ou identificador do contato
      screenshot: true/false
      text: true/false
    """
    params = parameters or {}
    receiver = str(params.get("receiver", "")).strip()
    platform = str(params.get("platform", "whatsapp")).strip()

    if not receiver:
        return "Informe o contato da conversa que deve ser copiada."

    if not _PYAUTOGUI:
        return "PyAutoGUI não está instalado."

    try:
        real_platform = _open_conversation_for_backup(platform, receiver)

        # Dá tempo para a conversa ficar completamente visível.
        time.sleep(1.0)

        folder = _conversation_folder(real_platform, receiver)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        generated = []

        # Captura a tela antes da seleção/cópia.
        screenshot_value = params.get("screenshot", True)
        if screenshot_value:
            screenshot = _take_screenshot(real_platform, receiver)
            generated.append(str(screenshot))

        # Tenta copiar o conteúdo selecionável.
        text_value = params.get("text", True)
        if text_value:
            try:
                copied = _copy_visible_conversation()

                if copied.strip():
                    text_path = _save_conversation_text(
                        real_platform,
                        receiver,
                        copied,
                    )
                    generated.append(str(text_path))
                else:
                    generated.append(
                        "Nenhum texto foi disponibilizado pela interface."
                    )

            except Exception as copy_error:
                generated.append(
                    f"Texto não copiado: {copy_error}"
                )

        # Cria um manifesto simples do backup.
        manifest = folder / f"backup_{timestamp}.json"
        manifest.write_text(
            json.dumps(
                {
                    "platform": real_platform,
                    "receiver": receiver,
                    "created_at": datetime.now().isoformat(),
                    "files": generated,
                    "note": (
                        "O backup foi obtido pela interface gráfica. "
                        "A quantidade de mensagens depende do que a "
                        "plataforma permitiu selecionar/copiar."
                    ),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        generated.append(str(manifest))

        result = (
            f"Backup da conversa com {receiver} concluído.\n"
            f"Pasta: {folder}\n"
            f"Arquivos:\n- "
            + "\n- ".join(generated)
        )

        if player:
            try:
                player.write_log(
                    f"[backup] {real_platform} → {receiver} → {folder}"
                )
            except Exception:
                pass

        return result

    except Exception as e:
        return f"Não foi possível fazer o backup da conversa: {e}"


def copy_conversation(parameters: dict, response=None, player=None, session_memory=None) -> str:
    """
    Abre uma conversa, copia o conteúdo visível e salva em TXT.
    """
    params = dict(parameters or {})
    params["screenshot"] = False
    params["text"] = True

    return backup_conversation(
        params,
        response=response,
        player=player,
        session_memory=session_memory,
    )


def screenshot_conversation(parameters: dict, response=None, player=None, session_memory=None) -> str:
    """
    Abre uma conversa e salva um screenshot.
    """
    params = dict(parameters or {})
    params["screenshot"] = True
    params["text"] = False

    return backup_conversation(
        params,
        response=response,
        player=player,
        session_memory=session_memory,
    )


def send_message(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:

    params = parameters or {}
    receiver = str(params.get("receiver", "")).strip()
    message_text = str(params.get("message_text", "")).strip()
    platform = str(params.get("platform", "whatsapp")).strip()

    if not receiver:
        return "Não foi informado o destinatário."

    if not message_text:
        return "Não foi informado o conteúdo da mensagem."

    if not _PYAUTOGUI:
        return "PyAutoGUI não está instalado — não é possível controlar a área de trabalho."

    preview = message_text[:50] + ("…" if len(message_text) > 50 else "")
    print(f"[SendMessage] 📨 {platform} → {receiver}: {preview}")

    if player:
        try:
            player.write_log(f"[msg] {platform} → {receiver}")
        except Exception:
            pass

    try:
        handler = _resolve_platform(platform)
        result = handler(receiver, message_text)
    except Exception as e:
        result = f"Não foi possível enviar a mensagem: {e}"

    success = (
        "mensagem enviada" in result.lower()
        or "message sent" in result.lower()
    )

    print(f"[SendMessage] {'✅' if success else '❌'} {result}")

    if player:
        try:
            player.write_log(f"[msg] {result}")
        except Exception:
            pass

    return result


# Aliases para o agente poder descobrir as funções com nomes claros.
send = send_message
backup = backup_conversation
copy = copy_conversation
screenshot = screenshot_conversation
