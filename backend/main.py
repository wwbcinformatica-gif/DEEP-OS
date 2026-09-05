"""
DEEP-OS — Backend modular
FastAPI + LangChain + Memória Vetorial + Multi-Agentes
"""
import sys as _sys
import os as _os
_BACKEND_DIR = _os.path.dirname(_os.path.abspath(__file__))
if _BACKEND_DIR not in _sys.path:
    _sys.path.insert(0, _BACKEND_DIR)

import asyncio
import traceback

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from core.config import DB_PATH, get_base_dir
from core.logging_setup import get_logger, setup_logging
from database.connection import init_db, set_db_path
from middleware.tenant import TenantMiddleware, TenantContext

logger = setup_logging(level="INFO", log_file="logs/wbc-backend.log")

set_db_path(DB_PATH)
init_db()

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(title="DEEP-OS", version="1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Em produção, restrinja às origens do frontend
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5176",
    "http://2.25.143.185:5176",
    "http://2.25.143.185:8001",
    "http://deep-os.tech",
    "https://deep-os.tech",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de isolamento multi-tenant
app.add_middleware(TenantMiddleware)


# ── Exception Handler Global ──────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura exceções não tratadas e retorna erro 500 com logging detalhado."""
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    logger.error(
        "Exceção não tratada em %s %s: %s\n%s",
        request.method,
        request.url.path,
        type(exc).__name__,
        "".join(tb),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": type(exc).__name__,
            "message": str(exc)[:500],
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Trata ValueErrors com status 400 em vez de 500."""
    logger.warning("ValueError em %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=400,
        content={"error": "Requisição inválida", "detail": str(exc)[:500]},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Recurso não encontrado", "path": request.url.path},
    )

# ── Routes ──────────────────────────────────────────────────────
from core.workspace_manager import WorkspaceManager
from routes.agent import router as agent_router
from routes.agent_fork import router as agent_fork_router
from routes.brain import router as brain_router
from routes.chat import router as chat_router
from routes.config import router as config_router
from routes.coworker import router as coworker_router
from routes.cron import router as cron_router
from routes.triggers import router as triggers_router
from routes.secrets import router as secrets_router
from routes.logs import router as logs_router
from routes.explorer_routes import router as explorer_router
from routes.generate import router as generate_router
from routes.history import router as history_router
from routes.knowledge import router as knowledge_router
from routes.memory_routes import router as memory_router
from routes.monitor_routes import router as monitor_router
from routes.agent_diagnostics import router as agent_diagnostics_router
from routes.ollama_route import router as ollama_router
from routes.openclaude_memory import router as openclaude_memory_router
from routes.plugins import router as plugins_router
from routes.tasks import router as tasks_router
from routes.teste_route import router as teste_router
from routes.teams import router as teams_router
from routes.terminal import _cleanup_stale_sessions
from routes.terminal import router as terminal_router
from routes.tools_api import router as tools_api_router
from routes.tts import router as tts_router
from routes.stt import router as stt_router
from routes.workspace import router as workspace_router
from routes.ws_terminal import router as ws_terminal_router
from routes.voice_ws import router as voice_router
from routes.llamacpp_route import router as llamacpp_router
from routes.browser import router as browser_router

# ─── Rotas SaaS ────────────────────────────────────────────────────
from routes.auth import router as auth_router
from routes.admin import router as admin_router

# ─── WorkspaceManager: carrega workspace persistido ─────────────────
WorkspaceManager.get_instance().load_workspace()

app.include_router(chat_router)
app.include_router(explorer_router)
app.include_router(terminal_router)
app.include_router(ws_terminal_router)
app.include_router(voice_router)
app.include_router(history_router)
app.include_router(knowledge_router)
app.include_router(brain_router)
app.include_router(tools_api_router)
app.include_router(ollama_router)
app.include_router(generate_router)
app.include_router(memory_router)
app.include_router(openclaude_memory_router)
app.include_router(plugins_router)
app.include_router(agent_router)
app.include_router(agent_fork_router)
app.include_router(teams_router)
app.include_router(cron_router)
app.include_router(triggers_router)
app.include_router(secrets_router)
app.include_router(logs_router)
app.include_router(coworker_router)
app.include_router(tasks_router)
app.include_router(teste_router)
app.include_router(monitor_router)
app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(config_router)
app.include_router(workspace_router)
app.include_router(agent_diagnostics_router)
app.include_router(llamacpp_router)
app.include_router(browser_router)

# ─── Rotas SaaS ────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {
        "app": "DEEP-OS",
        "version": "1.0",
        "endpoints": [
            "/chat", "/chat/stream",
            "/explorer", "/explorer/read",
            "/terminal",
            "/history",
            "/knowledge",
            "/brain/artifacts",
            "/tool/read", "/tool/write", "/tool/bash",
            "/ollama/status",
            "/generate/stream",
            "/memory", "/memory/vector",
            "/memory/elastic/stats", "/memory/elastic/recall", "/memory/elastic/index",
            "/memory/anti-patterns",
            "/agent/diagnostics", "/agent/run",
            "/openclaude/import/history",
            "/plugins", "/plugins/*/init",
            "/agent/execute",
            "/coworker/chat", "/coworker/stream",
            "/status",
            "/api/config/sandbox",
            "/api/stt/transcribe",
            "/api/stt/models",
            "/api/stt/health",
            "/cron", "/cron/{job_id}/pause", "/cron/{job_id}/resume", "/cron/{job_id}/run",
            "/triggers", "/triggers/tables", "/triggers/{id}/enable", "/triggers/{id}/disable",
            "/secrets", "/secrets/validate", "/secrets/{key}",
            "/logs", "/logs/stats"
        ]
    }


@app.get("/status")
async def status():
    return {
        "status": "ok",
        "base_dir": str(get_base_dir()),
        "version": "1.0",
        "db": str(DB_PATH),
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/license")
async def license_status():
    """Verifica o status da licença da instância."""
    try:
        from core.license import check_license
        return await check_license()
    except Exception as e:
        return {"valid": False, "error": str(e)}


@app.on_event("startup")
async def startup():
    log = get_logger("startup")
    log.info("Iniciando DEEP-OS v1.0 (SaaS Mode)")
    asyncio.create_task(_cleanup_stale_sessions())

    # Inicializa secrets manager
    from core.secrets import init_secrets
    init_secrets()
    log.info("Secrets manager inicializado")

    # Inicializa banco administrativo
    try:
        from init_admin_db import init_admin_db
        init_admin_db()
        log.info("Banco administrativo inicializado")
    except Exception as e:
        log.warning("Erro ao inicializar banco admin: %s", e)

    # Inicializa diretório de tenants
    TenantContext.ensure_tenant_dirs()
    log.info("Diretórios de tenants inicializados")

    # Verifica licença
    try:
        from core.license import check_license
        license_status = await check_license()
        if license_status.get("valid"):
            log.info("Licença válida. Expira: %s", license_status.get("expires", "N/A"))
        else:
            log.warning("Licença inválida ou ausente. Funcionalidades podem ser limitadas.")
    except Exception as e:
        log.warning("Erro ao verificar licença: %s", e)

@app.on_event("shutdown")
async def shutdown():
    log = get_logger("shutdown")
    log.info("Desligando servidor")
    try:
        from plugins.mcp_bridge import shutdown_mcp_servers
        shutdown_mcp_servers()
        log.info("Servidores MCP desligados")
    except Exception as e:
        log.warning("Erro ao desligar MCP: %s", e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
