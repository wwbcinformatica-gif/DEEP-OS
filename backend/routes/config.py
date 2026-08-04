from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.agent_config import reset_config_cache

router = APIRouter(prefix="/api/config", tags=["Config"])

def _get_config_path() -> str:
    from pathlib import Path
    return str(Path(__file__).resolve().parent.parent.parent / "config.yaml")

def _read_config() -> dict:
    path = _get_config_path()
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading config: {e}")

def _write_config(data: dict):
    path = _get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing config: {e}")

def _deep_set(data: dict, key_path: str, value: Any):
    keys = key_path.split(".")
    d = data
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            d[k] = {}
        d = d[k]
    d[keys[-1]] = value

def _deep_get(data: dict, key_path: str, default: Any = None) -> Any:
    keys = key_path.split(".")
    d = data
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
            if d is None:
                return default
        else:
            return default
    return d

class SandboxConfig(BaseModel):
    enabled: bool

class AccentThemeConfig(BaseModel):
    theme: str

class ConfigUpdatePayload(BaseModel):
    section: str
    values: dict

@router.get("")
async def get_full_config():
    data = _read_config()
    return data

@router.put("")
async def update_config(payload: ConfigUpdatePayload):
    data = _read_config()
    data[payload.section] = payload.values
    _write_config(data)
    reset_config_cache()
    return {"status": "success", "section": payload.section}

@router.get("/{section}")
async def get_config_section(section: str):
    data = _read_config()
    return data.get(section, {})

@router.post("/sandbox")
async def update_sandbox_config(config: SandboxConfig):
    data = _read_config()
    if "security" not in data:
        data["security"] = {}
    data["security"]["sandbox_enabled"] = config.enabled
    _write_config(data)
    return {"status": "success", "sandbox_enabled": config.enabled}

@router.post("/accent-theme")
async def update_accent_theme(config: AccentThemeConfig):
    data = _read_config()
    if "display" not in data:
        data["display"] = {}
    data["display"]["accent_theme"] = config.theme
    _write_config(data)
    return {"status": "success", "accent_theme": config.theme}

@router.get("/accent-theme")
async def get_accent_theme():
    data = _read_config()
    theme = _deep_get(data, "display.accent_theme", "azul-claro")
    return {"accent_theme": theme}

# ─── MCP Server CRUD ─────────────────────────────────────────────

class McpServerConfig(BaseModel):
    type: str = "local"
    command: list[str] | None = None
    url: str | None = None
    enabled: bool = True
    environment: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    timeout: int | None = 5000

@router.get("/mcp-servers")
async def list_mcp_servers_config():
    data = _read_config()
    servers = data.get("mcp", {})
    return {"servers": servers}

@router.put("/mcp-servers/{name}")
async def upsert_mcp_server(name: str, config: McpServerConfig):
    data = _read_config()
    if "mcp" not in data:
        data["mcp"] = {}
    entry = {"type": config.type, "enabled": config.enabled}
    if config.type == "local" and config.command:
        entry["command"] = config.command
    if config.type == "remote" and config.url:
        entry["url"] = config.url
    if config.environment:
        entry["environment"] = config.environment
    if config.headers:
        entry["headers"] = config.headers
    if config.timeout:
        entry["timeout"] = config.timeout
    data["mcp"][name] = entry
    _write_config(data)
    return {"status": "success", "server": name}

@router.delete("/mcp-servers/{name}")
async def delete_mcp_server(name: str):
    data = _read_config()
    mcp = data.get("mcp", {})
    if name not in mcp:
        raise HTTPException(status_code=404, detail=f"MCP server '{name}' not found")
    del mcp[name]
    data["mcp"] = mcp
    _write_config(data)
    return {"status": "success", "removed": name}
