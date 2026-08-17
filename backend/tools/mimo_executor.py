"""
MiMo Executor - Integracao do mimo.exe com tool calling nativo.

O mimo.exe e um agente local (clone do OpenCode) com tool calling nativo.
Este modulo chama o mimo.exe como subprocesso e faz streaming dos eventos.

Formato de eventos do mimo.exe (JSON linha por linha):
  {"type":"step_start","part":{"type":"step-start"}}
  {"type":"tool_use","part":{"type":"tool","tool":"write","callID":"...","state":{"status":"completed","input":{...},"output":"..."}}}
  {"type":"step_finish","part":{"reason":"tool-calls"|"stop"}}
  {"type":"text","part":{"type":"text","text":"..."}}
  {"type":"error","error":{"name":"...","data":{"message":"..."}}}
"""

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MIMO_EXE = str(_PROJECT_ROOT / ".mimocode" / "bin" / "mimo.exe")


async def stream_mimo_task(
    message: str,
    model: str = "xiaomi/mimo-v2.5",
    root: str = "",
    timeout: int = 300,
    history: list = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Executa uma tarefa via mimo.exe com streaming de eventos.

    Yields eventos no formato compativel com o lifecycle do DEEP-AUREA:
        {"type": "content", "data": "texto"}
        {"type": "tool_start", "tool": "write", "params": {...}}
        {"type": "tool_end", "tool": "write", "result": {...}}
        {"type": "done", "content": "...", "tool_calls": [...]}
        {"type": "error", "message": "..."}
    """
    # Se tem historico, injeta na mensagem
    full_message = message
    if history:
        context_parts = []
        for msg in history[-15:]:  # ultimas 15 mensagens para nao estourar
            role = "Usuario" if msg["role"] == "user" else "Assistente"
            context_parts.append(f"{role}: {msg['content'][:500]}")
        context_str = "\n".join(context_parts)
        full_message = f"[CONTEXTO DA CONVERSA]\n{context_str}\n[FIM DO CONTEXTO]\n\nMensagem atual: {message}"

    cmd = [
        MIMO_EXE, "run", full_message,
        "--format", "json",
        "--model", model,
        "--dangerously-skip-permissions",
    ]
    if root:
        cmd.extend(["--dir", root])

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        full_content = ""
        full_reasoning = ""
        tool_events = []

        while True:
            try:
                line = await asyncio.wait_for(
                    process.stdout.readline(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                yield {"type": "error", "message": f"Timeout apos {timeout}s"}
                break

            if not line:
                break

            line_str = line.decode("utf-8", errors="replace").strip()
            if not line_str:
                continue

            try:
                event = json.loads(line_str)
            except json.JSONDecodeError:
                continue

            event_type = event.get("type", "")
            part = event.get("part", {})

            if event_type == "text":
                text = part.get("text", "")
                if text:
                    full_content += text
                    yield {"type": "content", "data": text}

            elif event_type == "reasoning":
                text = part.get("text", "") or part.get("content", "")
                if text:
                    full_reasoning += text
                    yield {"type": "content", "data": text}

            elif event_type == "tool_use":
                tool_name = part.get("tool", "")
                state = part.get("state", {})
                tool_input = state.get("input", {})
                tool_output = state.get("output", "")
                tool_status = state.get("status", "")

                if tool_name and tool_status == "completed":
                    yield {"type": "tool_start", "tool": tool_name, "params": tool_input}
                    result = {"output": tool_output} if tool_output else {"status": "ok"}
                    if isinstance(tool_output, dict):
                        result = tool_output
                    yield {"type": "tool_end", "tool": tool_name, "result": result}
                    tool_events.append({
                        "tool": tool_name,
                        "params": tool_input,
                        "result": result,
                    })

            elif event_type == "step_start":
                pass

            elif event_type == "step_finish":
                reason = part.get("reason", "")
                if reason == "stop":
                    pass

            elif event_type == "error":
                err = event.get("error", {})
                err_data = err.get("data", {})
                err_msg = err_data.get("message", "") or str(err)
                yield {"type": "error", "message": err_msg}

        await process.wait()

        if process.returncode != 0:
            stderr_data = await process.stderr.read()
            stderr_str = stderr_data.decode("utf-8", errors="replace")
            if stderr_str and not full_content:
                yield {"type": "error", "message": f"mimo.exe erro: {stderr_str[:500]}"}

        yield {
            "type": "done",
            "content": full_content,
            "reasoning": full_reasoning,
            "tool_calls": tool_events,
        }

    except FileNotFoundError:
        yield {"type": "error", "message": f"mimo.exe nao encontrado em {MIMO_EXE}"}
    except Exception as e:
        yield {"type": "error", "message": f"Erro ao executar mimo.exe: {str(e)}"}


async def run_mimo_task(
    message: str,
    model: str = "xiaomi/mimo-v2.5",
    root: str = "",
    timeout: int = 300,
) -> Dict[str, Any]:
    """
    Executa uma tarefa via mimo.exe e retorna o resultado completo.
    """
    result = {"content": "", "tool_calls": [], "reasoning": "", "error": None}

    async for event in stream_mimo_task(message, model, root, timeout):
        if event["type"] == "content":
            result["content"] += event.get("data", "")
        elif event["type"] == "error":
            result["error"] = event.get("message", "")
        elif event["type"] == "done":
            result["content"] = event.get("content", result["content"])
            result["tool_calls"] = event.get("tool_calls", [])
            result["reasoning"] = event.get("reasoning", "")

    return result