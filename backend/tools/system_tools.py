import io
import re
import subprocess
import sys
import textwrap
from pathlib import Path

from core.config import get_base_dir

ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b\[?\??[0-9;]*[a-zA-Z]')

def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub('', text)


async def tool_read(path: str, root: str = "") -> dict:
    from tools.explorer import resolve_path
    target = resolve_path(path, root)
    if not target.exists():
        return {"error": "Arquivo/diretorio nao encontrado"}
    if target.is_dir():
        items = [
            {"name": c.name, "type": "directory" if c.is_dir() else "file"}
            for c in sorted(target.iterdir()) if not c.name.startswith(".")
        ]
        return {"type": "directory", "items": items}

    # Arquivos binarios que nao podem ser lidos como texto
    ext = target.suffix.lower()
    binary_exts = {'.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
                   '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
                   '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.webp', '.svg',
                   '.mp3', '.mp4', '.wav', '.avi', '.mkv', '.flac', '.ogg',
                   '.zip', '.rar', '.7z', '.tar', '.gz',
                   '.db', '.sqlite', '.sqlite3'}

    if ext in binary_exts:
        # Tenta extrair texto de PDFs
        if ext == '.pdf':
            try:
                import subprocess
                result = subprocess.run(
                    ['python', '-c', f'''
import fitz
doc = fitz.open(r"{target}")
text = ""
for page in doc:
    text += page.get_text()
print(text[:15000])
'''],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0 and result.stdout.strip():
                    return {"type": "file", "content": result.stdout[:15000], "truncated": len(result.stdout) > 15000, "note": "Texto extraido do PDF"}
            except Exception:
                pass

        return {
            "type": "binary",
            "error": f"Arquivo {ext} e binario e nao pode ser lido como texto.",
            "suggestion": f"Para visualizar este arquivo, use bash('start {target.name}') para abrir no programa padrao.",
            "file": target.name,
            "size": target.stat().st_size,
        }

    content = target.read_text("utf-8", errors="replace")
    return {"type": "file", "content": content[:10000], "truncated": len(content) > 10000}

async def tool_write(path: str, content: str, root: str = "") -> dict:
    from tools.explorer import resolve_path
    target = resolve_path(path, root)
    existed = target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)
    return {"status": "ok", "path": str(target), "action": "overwritten" if existed else "created"}

async def tool_bash(command: str, workdir: str = "") -> dict:
    """Executa qualquer comando — com verificação de Modo Restrito."""
    if not command.strip():
        return {"error": "Comando vazio"}
    # ── Verifica Modo Restrito (Sandbox) ──────────────────────────────
    try:
        import yaml
        config_path = Path("C:/DEEP-AUREA/config.yaml")
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and data.get("security", {}).get("sandbox_enabled", False):
                cmd_lower = command.strip().lower()
                project_root = str(get_base_dir()).lower()
                drives_blocked = [r"d:", r"d:\\", r"i:", r"i:\\", r"e:", r"e:\\",
                                  r"f:", r"f:\\", r"g:", r"g:\\", r"h:", r"h:\\",
                                  r"j:", r"j:\\", r"k:", r"k:\\", r"l:", r"l:\\",
                                  r"m:", r"m:\\", r"n:", r"n:\\", r"o:", r"o:\\",
                                  r"p:", r"p:\\", r"q:", r"q:\\", r"r:", r"r:\\",
                                  r"s:", r"s:\\", r"t:", r"t:\\", r"u:", r"u:\\",
                                  r"v:", r"v:\\", r"x:", r"x:\\", r"y:", r"y:\\",
                                  r"z:", r"z:\\"]
                for blocked in drives_blocked:
                    if blocked in cmd_lower:
                        if not cmd_lower.startswith(project_root[:2]):
                            return {"error": "Acesso Negado: O terminal está bloqueado pelo Modo Restrito."}
                if "\\" in cmd_lower:
                    import re
                    abs_paths = re.findall(r'[a-zA-Z]:\\\\[^\\\s]+', cmd_lower)
                    for p in abs_paths:
                        if not p.lower().startswith(project_root[:2]):
                            return {"error": "Acesso Negado: O terminal está bloqueado pelo Modo Restrito."}
    except Exception:
        pass  # Se erro ao ler config, permite execução normal
    # ───────────────────────────────────────────────────────────────────
    try:
        wd = workdir or str(get_base_dir())
        # Garantir que o workdir existe
        from pathlib import Path as _P
        if not _P(wd).exists():
            wd = str(get_base_dir())
        r = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, timeout=300, cwd=wd,
            encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL,
        )
        return {
            "stdout": strip_ansi(r.stdout[-5000:]),
            "stderr": strip_ansi(r.stderr[-2000:]),
            "returncode": r.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Timeout 60s"}
    except Exception as e:
        return {"error": str(e)}

async def tool_search(pattern: str, path: str = "", include: str = "") -> dict:
    try:
        _base = get_base_dir()
        search_root = Path(_base / path).resolve() if path else _base
        if not str(search_root).startswith(str(_base)):
            return {"error": "Acesso negado"}
        import subprocess
        cmd = ["rg", "-n", pattern, str(search_root)]
        if include:
            cmd.extend(["-g", include])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        lines = [l for l in r.stdout.split("\n") if l.strip()][:50]
        return {"matches": len(lines), "results": lines[:30]}
    except FileNotFoundError:
        # fallback to pure python search
        matches = []
        for f in sorted(search_root.rglob("*")):
            if f.is_file() and not f.name.startswith("."):
                try:
                    content = f.read_text("utf-8", errors="replace")
                    for i, line in enumerate(content.split("\n"), 1):
                        if pattern in line:
                            rel = f.relative_to(get_base_dir())
                            matches.append(f"{rel}:{i}: {line.strip()[:120]}")
                            if len(matches) >= 30:
                                break
                except Exception:
                    pass
            if len(matches) >= 30:
                break
        return {"matches": len(matches), "results": matches[:30]}
    except Exception as e:
        return {"error": str(e)}

async def tool_grep(pattern: str, path: str = "", include: str = "") -> dict:
    return await tool_search(pattern, path, include)

async def tool_execute_python(code: str) -> dict:
    try:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        clean_code = textwrap.dedent(code)
        exec_globals = {"__builtins__": __builtins__}
        exec(clean_code, exec_globals)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        return {"stdout": output[-3000:], "status": "ok"}
    except Exception as e:
        sys.stdout = old_stdout
        return {"error": str(e), "status": "error"}

async def tool_create_directory(path: str, root: str = "") -> dict:
    from tools.explorer import resolve_path
    try:
        target = resolve_path(path, root)
        target.mkdir(parents=True, exist_ok=True)
        return {"status": "ok", "path": str(target), "created": target.exists()}
    except Exception as e:
        return {"error": str(e)}

async def tool_delete(path: str, root: str = "") -> dict:
    from tools.explorer import resolve_path
    try:
        target = resolve_path(path, root)
        if not target.exists():
            return {"error": "Caminho não encontrado"}
        if target.is_dir():
            import shutil
            shutil.rmtree(target)
            return {"status": "ok", "action": "deleted_dir", "path": str(target)}
        else:
            target.unlink()
            return {"status": "ok", "action": "deleted_file", "path": str(target)}
    except Exception as e:
        return {"error": str(e)}

async def tool_rename(old_path: str, new_path: str, root: str = "") -> dict:
    from tools.explorer import resolve_path
    try:
        old_target = resolve_path(old_path, root)
        new_target = resolve_path(new_path, root)
        if not old_target.exists():
            return {"error": "Caminho original não encontrado"}
        old_target.rename(new_target)
        return {"status": "ok", "from": str(old_target), "to": str(new_target)}
    except Exception as e:
        return {"error": str(e)}

async def tool_install_package(package: str) -> dict:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True, text=True, timeout=120
        )
        return {
            "stdout": r.stdout[-2000:],
            "stderr": r.stderr[-1000:],
            "returncode": r.returncode,
        }
    except Exception as e:
        return {"error": str(e)}
