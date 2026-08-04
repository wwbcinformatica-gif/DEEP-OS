import json
import subprocess
from pathlib import Path

import yaml
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def _read_config() -> dict:
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


def _write_config(data: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)


def _fetch_ollama_models() -> dict:
    """Chama a API local do Ollama e retorna status + lista de modelos."""
    try:
        r = subprocess.run(
            ["curl.exe", "-s", "--max-time", "5", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=6,
        )
        if r.returncode != 0 or not r.stdout.strip():
            return {"running": False, "models": []}
        data = json.loads(r.stdout)
        models = [m["name"] for m in data.get("models", [])]
        return {"running": True, "models": models}
    except Exception as e:
        return {"running": False, "models": [], "error": str(e)}


def get_gpu_config() -> dict:
    config = _read_config()
    ollama_cfg = config.get("ollama", {})
    return {
        "gpu_enabled": ollama_cfg.get("gpu_enabled", True),
        "gpu_layers": ollama_cfg.get("gpu_layers", -1),
    }


def set_gpu_config(gpu_enabled: bool, gpu_layers: int = -1):
    config = _read_config()
    if "ollama" not in config:
        config["ollama"] = {}
    config["ollama"]["gpu_enabled"] = gpu_enabled
    config["ollama"]["gpu_layers"] = gpu_layers
    _write_config(config)


class GpuConfigPayload(BaseModel):
    gpu_enabled: bool
    gpu_layers: int = -1


@router.get("/ollama/status")
async def ollama_status():
    return _fetch_ollama_models()


@router.get("/ollama/models")
async def ollama_models():
    """Retorna lista de modelos instalados no Ollama."""
    result = _fetch_ollama_models()
    return {
        "running": result["running"],
        "models": result["models"],
    }


@router.get("/ollama/gpu")
async def ollama_get_gpu():
    return get_gpu_config()


@router.post("/ollama/gpu")
async def ollama_set_gpu(payload: GpuConfigPayload):
    set_gpu_config(payload.gpu_enabled, payload.gpu_layers)
    return {"status": "ok", "gpu_enabled": payload.gpu_enabled, "gpu_layers": payload.gpu_layers}
