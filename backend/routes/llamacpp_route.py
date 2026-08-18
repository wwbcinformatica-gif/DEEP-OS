import json
import subprocess
import os
import time
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Base dir dinamico — funciona em qualquer unidade (C:, G:, D:, etc.)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LLAMA_SERVER_EXE = BASE_DIR / "bin" / "vulkan" / "llama-server.exe"
LLAMA_SERVER_PORT = 8080

MODELS_DIR = BASE_DIR / "models"

GGUF_MODELS = {
    "bonsai-27b": {
        "file": str(MODELS_DIR / "ternary-gguf" / "27B" / "Ternary-Bonsai-27B-Q2_0.gguf"),
        "label": "Ternary-Bonsai 27B Q2_0",
        "ctx": 32768,
    },
    "bonsai-27b-1bit": {
        "file": str(MODELS_DIR / "gguf" / "Bonsai-27B-Q1_0.gguf"),
        "label": "Ternary-Bonsai 27B Q1_0",
        "ctx": 32768,
    },
    "bonsai-27b-dspark": {
        "file": str(MODELS_DIR / "gguf" / "27B" / "Bonsai-27B-dspark-Q4_1.gguf"),
        "label": "Ternary-Bonsai 27B dspark Q4_1",
        "ctx": 32768,
    },
    "llama-3.2-3b-gguf": {
        "file": str(MODELS_DIR / "gguf" / "Llama-3.2-3B-Instruct-Q4_K_M.gguf"),
        "label": "Llama 3.2 3B Q4_K_M",
        "ctx": 8192,
    },
    "nemomix-12b-gguf": {
        "file": str(MODELS_DIR / "gguf" / "NemoMix-Unleashed-12B-Q4_K_M.gguf"),
        "label": "NemoMix 12B Q4_K_M",
        "ctx": 8192,
    },
    "qwen2.5-7b-gguf": {
        "file": str(MODELS_DIR / "gguf" / "Qwen2.5-7B-Instruct-Q4_K_M.gguf"),
        "label": "Qwen 2.5 7B Q4_K_M",
        "ctx": 8192,
    },
}


def _check_llama_server() -> dict:
    try:
        r = subprocess.run(
            ["curl.exe", "-s", "--max-time", "3", f"http://localhost:{LLAMA_SERVER_PORT}/health"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            return {"running": data.get("status") == "ok", "port": LLAMA_SERVER_PORT}
    except Exception:
        pass
    return {"running": False, "port": LLAMA_SERVER_PORT}


def _current_loaded_model() -> str | None:
    """Tenta descobrir qual modelo o llama-server carregou via /props."""
    try:
        r = subprocess.run(
            ["curl.exe", "-s", "--max-time", "3", f"http://localhost:{LLAMA_SERVER_PORT}/props"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            path = data.get("default_generation_settings", {}).get("model") or data.get("model_path", "")
            if path:
                return Path(path).name
    except Exception:
        pass
    return None


def _start_llama_server(model_id: str) -> dict:
    info = GGUF_MODELS[model_id]
    template_file = str(LLAMA_SERVER_EXE.parent.parent / "models" / "chat-template.txt")
    cmd = [
        str(LLAMA_SERVER_EXE),
        "--model", info["file"],
        "--port", str(LLAMA_SERVER_PORT),
        "--ctx-size", str(info["ctx"]),
        "--host", "0.0.0.0",
    ]
    if Path(template_file).exists():
        cmd.extend(["--chat-template", f"file://{template_file}"])
    else:
        cmd.extend(["--chat-template", "chatml"])
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    return {"status": "starting", "model": model_id, "port": LLAMA_SERVER_PORT}


def ensure_llamacpp_model(model_id: str, max_wait: int = 60) -> dict:
    """Garante que o llama-server esteja rodando o modelo GGUF correto."""
    if model_id not in GGUF_MODELS:
        return {"error": f"Modelo '{model_id}' desconhecido"}

    info = GGUF_MODELS[model_id]
    if not Path(info["file"]).exists():
        return {"error": f"Arquivo GGUF nao encontrado: {info['file']}"}

    if not LLAMA_SERVER_EXE.exists():
        return {"error": f"llama-server.exe nao encontrado: {LLAMA_SERVER_EXE}"}

    status = _check_llama_server()
    target_filename = Path(info["file"]).name

    # Se estiver rodando outro modelo, para e reinicia
    if status["running"]:
        current = _current_loaded_model()
        if current and current != target_filename:
            subprocess.run(["taskkill", "/f", "/im", "llama-server.exe"], capture_output=True)
            time.sleep(1)

    # Se nao estiver rodando, inicia
    if not _check_llama_server()["running"]:
        _start_llama_server(model_id)
        # Aguarda subir
        for _ in range(max_wait):
            if _check_llama_server()["running"]:
                return {"ok": True, "model": model_id}
            time.sleep(1)
        return {"error": "llama-server nao respondeu a tempo"}

    return {"ok": True, "model": model_id, "already_running": True}


class StartGGUFPayload(BaseModel):
    model_id: str


@router.get("/llamacpp/status")
async def llamacpp_status():
    status = _check_llama_server()
    current = _current_loaded_model()
    return {
        "running": status["running"],
        "port": status["port"],
        "current_model": current,
        "models": list(GGUF_MODELS.keys()),
    }


@router.get("/llamacpp/models")
async def llamacpp_models():
    status = _check_llama_server()
    current = _current_loaded_model()
    result = []
    for mid, info in GGUF_MODELS.items():
        exists = Path(info["file"]).exists()
        loaded = status["running"] and current and current == Path(info["file"]).name
        result.append({
            "id": mid,
            "label": info["label"],
            "available": exists,
            "loaded": loaded,
        })
    return {"running": status["running"], "current_model": current, "models": result}


@router.post("/llamacpp/start")
async def llamacpp_start(payload: StartGGUFPayload):
    return ensure_llamacpp_model(payload.model_id)


@router.post("/llamacpp/stop")
async def llamacpp_stop():
    subprocess.run(
        ["taskkill", "/f", "/im", "llama-server.exe"],
        capture_output=True,
    )
    return {"status": "stopped"}

