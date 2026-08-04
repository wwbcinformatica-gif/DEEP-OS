from pathlib import Path

from fastapi import HTTPException

from core.config import get_explorer_root


def resolve_path(path: str, root: str = "") -> Path:
    base = Path(root).resolve() if root else get_explorer_root()
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return target

async def explorer_list(path: str = "", root: str = ""):
    try:
        if root:
            root_path = Path(root).resolve()
            if not root_path.exists() or not root_path.is_dir():
                raise HTTPException(status_code=400, detail="Diretório raiz não encontrado")
            target = (root_path / path).resolve()
            if not str(target).startswith(str(root_path)):
                raise HTTPException(status_code=403, detail="Acesso negado")
        else:
            _root = get_explorer_root()
            target = (_root / path).resolve()
            if not str(target).startswith(str(_root)):
                raise HTTPException(status_code=403, detail="Acesso negado")
        if not target.exists():
            raise HTTPException(status_code=404, detail="Caminho não encontrado")
        if target.is_file():
            rel = root_path if root else get_explorer_root()
            return {
                "type": "file",
                "name": target.name,
                "path": str(target.relative_to(rel)).replace("\\", "/"),
                "size": target.stat().st_size,
            }
        items = []
        rel_base = root_path if root else get_explorer_root()
        for child in sorted(target.iterdir()):
            items.append({
                "name": child.name,
                "path": str(child.relative_to(rel_base)).replace("\\", "/"),
                "type": "directory" if child.is_dir() else "file",
                "size": child.stat().st_size if child.is_file() else 0,
            })
        return {"type": "directory", "name": target.name, "path": path, "items": items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def explorer_read(path: str, root: str = ""):
    try:
        if root:
            root_path = Path(root).resolve()
            target = (root_path / path).resolve()
            if not str(target).startswith(str(root_path)):
                raise HTTPException(status_code=403, detail="Acesso negado")
        else:
            _root = get_explorer_root()
            target = (_root / path).resolve()
            if not str(target).startswith(str(_root)):
                raise HTTPException(status_code=403, detail="Acesso negado")
        if not target.exists() or not target.is_file():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        ext = target.suffix.lower()
        try:
            content = target.read_text(encoding="utf-8", errors="replace")
            return {"type": "text", "content": content, "language": ext.lstrip(".")}
        except Exception:
            return {"type": "binary", "content": None, "language": ext.lstrip(".")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
