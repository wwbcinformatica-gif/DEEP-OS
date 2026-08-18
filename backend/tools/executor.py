from fastapi import HTTPException

from agents.fork import fork_subagent, get_subagent_result
from agents.team import send_message, team_create, team_delete
from tasks.task_manager import create_task, get_task, list_tasks, stop_task, update_task
from tools.explorer import explorer_list, explorer_read
from tools.file_edit import tool_file_edit
from tools.file_tools import tool_glob
from tools.monitor import coletar_dashboard
from tools.system_tools import (
    tool_bash,
    tool_create_directory,
    tool_delete,
    tool_execute_python,
    tool_grep,
    tool_install_package,
    tool_read,
    tool_rename,
    tool_search,
    tool_write,
    tool_open_app,
)
from tools.tool_search import tool_tool_search
from tools.web_fetch import tool_web_fetch
from tools.web_search import tool_web_search
from tools.document_reader import tool_read_document

TOOL_REGISTRY = {
    "read": tool_read,
    "write": tool_write,
    "bash": tool_bash,
    "explorer": explorer_list,
    "explorer_read": explorer_read,
    "search": tool_search,
    "grep": tool_grep,
    "execute_python": tool_execute_python,
    "install_package": tool_install_package,
    "create_directory": tool_create_directory,
    "delete": tool_delete,
    "rename": tool_rename,
    # Web & Fetch
    "web_search": tool_web_search,
    "web_fetch": tool_web_fetch,
    # Document Reader
    "read_document": tool_read_document,
    # File Operations
    "file_edit": tool_file_edit,
    "glob": tool_glob,
    # Tool Discovery
    "tool_search": tool_tool_search,
    # Monitor
    "monitor_dashboard": lambda **kw: coletar_dashboard(),
    # App launcher
    "open_app": tool_open_app,
}

TOOL_METADATA = [
    {"name": "read", "description": "Lê arquivo ou lista diretório", "params": {"path": "string", "root": "string (opcional)"}},
    {"name": "write", "description": "Cria ou edita arquivo", "params": {"path": "string", "content": "string", "root": "string (opcional)"}},
    {"name": "bash", "description": "Executa comandos no terminal. IMPORTANTE: Use sempre flags não-interativas (como -y, --yes, --quiet) para comandos npx, npm, pip, etc. Se o comando esperar interação do usuário, ele vai falhar ou travar.", "params": {"command": "string", "workdir": "string (opcional)"}},
    {"name": "explorer", "description": "Navega no explorador de arquivos", "params": {"path": "string", "root": "string (opcional)"}},
    {"name": "explorer_read", "description": "Lê arquivo com syntax highlight", "params": {"path": "string", "root": "string (opcional)"}},
    {"name": "search", "description": "Busca texto em arquivos (regex)", "params": {"pattern": "string", "path": "string", "include": "string"}},
    {"name": "grep", "description": "Busca recursiva com regex em arquivos", "params": {"pattern": "string", "path": "string", "include": "string"}},
    {"name": "execute_python", "description": "Executa código Python em sandbox isolado", "params": {"code": "string"}},
    {"name": "install_package", "description": "Instala pacote pip", "params": {"package": "string"}},
    {"name": "create_directory", "description": "Cria uma ou mais pastas", "params": {"path": "string", "root": "string (opcional)"}},
    {"name": "delete", "description": "Deleta arquivo ou pasta", "params": {"path": "string", "root": "string (opcional)"}},
    {"name": "rename", "description": "Renomeia ou move arquivo ou pasta", "params": {"old_path": "string", "new_path": "string", "root": "string (opcional)"}},
    {"name": "list_mcp_servers", "description": "Lista todos os servidores MCP do OpenClaude ativos e suas ferramentas disponiveis", "params": {}},
    {"name": "init_mcp_plugin", "description": "Inicializa um plugin MCP do OpenClaude pelo nome (ex: github, discord, telegram). Apos iniciar, as ferramentas do plugin ficam disponiveis automaticamente.", "params": {"name": "string (nome do plugin)"}},
    # Web & Fetch
    {"name": "web_search", "description": "Busca na internet", "params": {"query": "string"}},
    {"name": "web_fetch", "description": "Busca conteudo de URL", "params": {"url": "string", "prompt": "string (opcional)"}},
    # Document Reader
    {"name": "read_document", "description": "Le documentos: PDF, DOCX, XLSX, CSV, XML, TXT, PPTX", "params": {"path": "string", "root": "string (opcional)"}},
    # File Operations
    {"name": "file_edit", "description": "Edita arquivo com find-and-replace", "params": {"path": "string", "old_string": "string", "new_string": "string", "root": "string (opcional)"}},
    {"name": "glob", "description": "Busca arquivos por padrao glob", "params": {"pattern": "string", "path": "string (opcional)"}},
    # Tool Discovery
    {"name": "tool_search", "description": "Busca ferramentas disponiveis", "params": {"query": "string"}},
    # Monitor
    {"name": "monitor_dashboard", "description": "Coleta dados de CPU, RAM e logs do servidor", "params": {"linhas_log": "integer (opcional)"}},
    # Agent Forking
    {"name": "fork_subagent", "description": "Cria subagente para tarefa paralela", "params": {"task": "string", "system_prompt": "string (opcional)"}},
    {"name": "get_subagent_result", "description": "Obtem resultado de subagente", "params": {"subagent_id": "string"}},
    # Agent Teams
    {"name": "team_create", "description": "Cria time de agentes", "params": {"name": "string", "members": "list (opcional)"}},
    {"name": "team_delete", "description": "Deleta time de agentes", "params": {"team_id": "string"}},
    {"name": "send_message", "description": "Envia mensagem para agente", "params": {"recipient": "string", "message": "string"}},
    # Cron
    {"name": "cron_create", "description": "Agenda tarefa recorrente", "params": {"expression": "string", "task": "string"}},
    {"name": "cron_delete", "description": "Remove job cron", "params": {"job_id": "string"}},
    {"name": "cron_list", "description": "Lista jobs cron", "params": {}},
]

ALLOWED_BASH_COMMANDS = {"ls", "dir", "cat", "type", "echo", "pwd", "whoami", "date", "time", "python", "py", "node", "npm", "git", "ollama", "curl", "ver", "systeminfo", "cd", "mkdir", "copy", "move", "del", "ren", "find", "code", "start", "pip", "npx"}

def _make_mcp_handler(server_key: str, tool_name: str):
    async def handler(**params):
        from plugins.mcp_bridge import call_mcp_tool
        return await call_mcp_tool(server_key, tool_name, params)
    return handler

def register_mcp_tool(plugin_name: str, server_key: str, tool_def: dict):
    orig_name = tool_def.get("name", "")
    description = tool_def.get("description", "")
    params_schema = tool_def.get("inputSchema", {})
    safe_name = f"{plugin_name}__{orig_name}"

    if safe_name in TOOL_REGISTRY:
        return

    TOOL_REGISTRY[safe_name] = _make_mcp_handler(server_key, orig_name)

    TOOL_METADATA.append({
        "name": safe_name,
        "description": description,
        "params": {k: v.get("type", "unknown") for k, v in params_schema.get("properties", {}).items()},
    })

    from tools import function_defs
    function_defs.TOOLS.append({
        "type": "function",
        "function": {
            "name": safe_name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": params_schema.get("properties", {}),
                "required": params_schema.get("required", []),
            }
        }
    })

def unregister_mcp_tools(plugin_name: str):
    prefix = f"{plugin_name}__"
    to_remove = [name for name in list(TOOL_REGISTRY.keys()) if name.startswith(prefix)]
    for name in to_remove:
        TOOL_REGISTRY.pop(name, None)
    TOOL_METADATA[:] = [m for m in TOOL_METADATA if not m["name"].startswith(prefix)]
    from tools import function_defs
    function_defs.TOOLS[:] = [t for t in function_defs.TOOLS if not t["function"]["name"].startswith(prefix)]

async def list_mcp_servers() -> dict:
    from plugins.mcp_bridge import get_all_mcp_servers
    servers = get_all_mcp_servers()
    result = {}
    for server_key, tools in servers.items():
        result[server_key] = [{"name": t.get("name"), "description": t.get("description", "")} for t in tools]
    return {"servers": result}

async def init_mcp_plugin(name: str) -> dict:
    from plugins.mcp_bridge import MCP_TOOL_REGISTRY, initialize_mcp_server
    from plugins.mcp_loader import get_plugin_info
    info = get_plugin_info(name)
    if not info:
        return {"error": f"Plugin '{name}' not found. Use list_mcp_plugins primeiro."}

    unregister_mcp_tools(name)

    keys = []
    total_tools = 0
    for server_name in info["mcp_servers"]:
        key = await initialize_mcp_server(name, server_name)
        if key:
            keys.append(key)
            entry = MCP_TOOL_REGISTRY.get(key, {})
            tools = entry.get("tools", [])
            for tool_def in tools:
                register_mcp_tool(name, key, tool_def)
                total_tools += 1

    plugin_tools = [k for k in TOOL_REGISTRY if k.startswith(f"{name}__")]
    return {"plugin": name, "servers": keys, "tools_registered": total_tools, "available_as": list(plugin_tools)}

TOOL_REGISTRY["list_mcp_servers"] = list_mcp_servers
TOOL_REGISTRY["init_mcp_plugin"] = init_mcp_plugin

# ── Task Management Tools ──────────────────────────────────
async def tool_task_create(subject: str, description: str = "", active_form: str = ""):
    task = await create_task(subject, description, active_form)
    return {"task_id": task.id, "subject": task.subject, "status": task.status}

async def tool_task_get(task_id: str):
    task = await get_task(task_id)
    if not task:
        return {"error": f"Task {task_id} not found"}
    return task.to_dict()

async def tool_task_update(task_id: str, status: str = None, output: str = None):
    fields = {}
    if status: fields["status"] = status
    if output: fields["output"] = output
    task = await update_task(task_id, **fields)
    if not task:
        return {"error": f"Task {task_id} not found"}
    return task.to_dict()

async def tool_task_list(status: str = None):
    tasks = await list_tasks(status)
    return {"tasks": [t.to_dict() for t in tasks], "count": len(tasks)}

async def tool_task_stop(task_id: str):
    ok = await stop_task(task_id)
    return {"stopped": ok, "task_id": task_id}

TOOL_REGISTRY["task_create"] = tool_task_create
TOOL_REGISTRY["task_get"] = tool_task_get
TOOL_REGISTRY["task_update"] = tool_task_update
TOOL_REGISTRY["task_list"] = tool_task_list
TOOL_REGISTRY["task_stop"] = tool_task_stop

# ── Agent Forking Tools ────────────────────────────────────
async def tool_fork_subagent(task: str, system_prompt: str = "", tools: list = None):
    return await fork_subagent(task, system_prompt, tools)

async def tool_get_subagent_result(subagent_id: str):
    return await get_subagent_result(subagent_id)

async def tool_team_create(name: str, members: list):
    return await team_create(name, members)

async def tool_team_delete(team_id: str):
    return await team_delete(team_id)

async def tool_send_message(recipient: str, message: str):
    return await send_message(recipient, message)

TOOL_REGISTRY["fork_subagent"] = tool_fork_subagent
TOOL_REGISTRY["get_subagent_result"] = tool_get_subagent_result
TOOL_REGISTRY["team_create"] = tool_team_create
TOOL_REGISTRY["team_delete"] = tool_team_delete
TOOL_REGISTRY["send_message"] = tool_send_message

# ── Memory Tools ────────────────────────────────────────────
from memory.engine import memory_delete, memory_list, memory_read, memory_write

TOOL_REGISTRY["memory_write"] = memory_write
TOOL_REGISTRY["memory_read"] = memory_read
TOOL_REGISTRY["memory_list"] = memory_list
TOOL_REGISTRY["memory_delete"] = memory_delete

# ── Media Play Tool ────────────────────────────────────────
async def tool_media_play(name: str = "", path: str = "", isVideo: bool = False):
    return {"action": "media_play", "payload": {"name": name, "path": path, "isVideo": isVideo}}

TOOL_REGISTRY["media_play"] = tool_media_play
TOOL_METADATA.append({"name": "media_play", "description": "Abre midia no player interno do projeto", "params": {"name": "string", "path": "string", "isVideo": "boolean"}})

# -- Close App Tool --
async def tool_close_app(process_name: str = "", file_path: str = ""):
    import asyncio, re as _re

    async def _run(cmd):
        r = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, _ = await r.communicate()
        return out.decode(errors="replace")

    async def _kill_by_name(name):
        # Tenta taskkill direto
        result = await _run(f'taskkill /IM "{name}" /F 2>&1')
        if "SUCCESS" in result or "sucesso" in result.lower():
            return {"closed": name, "status": "ok"}
        # Se falhou, busca por lista de processos
        tasklist = await _run("tasklist /FO CSV 2>&1")
        for line in tasklist.splitlines():
            if name.lower() in line.lower():
                pid_match = _re.search(r'"(\d+)"', line)
                if pid_match:
                    pid = pid_match.group(1)
                    await _run(f"taskkill /PID {pid} /F 2>&1")
                    return {"closed": name, "pid": pid, "status": "ok"}
        return {"closed": name, "status": "not_found", "detail": result.strip()[:200]}

    if process_name:
        return await _kill_by_name(process_name)

    if file_path:
        import os
        basename = os.path.basename(file_path).lower()
        ext = os.path.splitext(basename)[1].lower()

        # Busca processo que tem o arquivo aberto
        if ext in ('.mp3', '.mp4', '.wav', '.avi', '.mkv', '.flac', '.ogg', '.wma', '.m4a'):
            # Processos comuns de midia
            for proc in ('MusicPlayer.exe', 'vlc.exe', 'wmplayer.exe', 'mspaint.exe', 'Photos.exe'):
                r = await _run(f'tasklist /FI "IMAGENAME eq {proc}" /FO CSV 2>&1')
                if proc.lower() in r.lower():
                    return await _kill_by_name(proc)
            # Fallback: mata qualquer coisa com musica
            return await _kill_by_name("MusicPlayer.exe")
        elif ext == '.pdf':
            return await _kill_by_name("AcroRd32.exe")
        elif ext in ('.docx', '.doc'):
            return await _kill_by_name("WINWORD.EXE")
        elif ext in ('.xlsx', '.xls'):
            return await _kill_by_name("EXCEL.EXE")
        elif ext == '.txt':
            return await _kill_by_name("notepad.exe")

    return {"error": "Especifique process_name ou file_path"}

TOOL_REGISTRY["close_app"] = tool_close_app
TOOL_METADATA.append({"name": "close_app", "description": "Fecha um processo ou arquivo aberto", "params": {"process_name": "string", "file_path": "string"}})


def _validate_tool_params(tool_name: str, params: dict) -> str:
    """Valida parametros obrigatorios antes de executar ferramenta."""
    REQUIRED_PARAMS = {
        "bash": ["command"],
        "write": ["path", "content"],
        "read": ["path"],
        "explorer": [],
        "explorer_read": ["path"],
        "search": ["pattern"],
        "grep": ["pattern"],
        "execute_python": ["code"],
        "install_package": ["package"],
        "create_directory": ["path"],
        "delete": ["path"],
        "rename": ["old_path", "new_path"],
        "web_search": ["query"],
        "web_fetch": ["url"],
        "read_document": ["path"],
        "file_edit": ["path", "old_string", "new_string"],
        "glob": ["pattern"],
        "tool_search": ["query"],
        "media_play": ["path"],
        "fork_subagent": ["task"],
        "team_create": ["name"],
        "send_message": ["recipient", "message"],
        "cron_create": ["expression", "task"],
        "cron_delete": ["job_id"],
    }
    
    required = REQUIRED_PARAMS.get(tool_name, [])
    missing = [p for p in required if not params.get(p)]
    if missing:
        return f"Parametros obrigatorios ausentes: {', '.join(missing)}. Ferramenta '{tool_name}' requer: {required}"
    return None

async def execute_tool(tool: str, params: dict) -> dict:
    func = TOOL_REGISTRY.get(tool)
    if not func:
        valid = ", ".join(TOOL_REGISTRY.keys())
        return {"error": f"Ferramenta desconhecida: '{tool}'. Ferramentas validas: {valid}."}
    
    validation_error = _validate_tool_params(tool, params)
    if validation_error:
        return {"error": validation_error}
    
    try:
        return await func(**params)
    except HTTPException as e:
        return {"error": e.detail}
    except Exception as e:
        return {"error": str(e)}

