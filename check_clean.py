"""Verify server clean start with directives active."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("backend")))

from main import app
from agents.orchestrator import load_agent_prompt

p = load_agent_prompt("jarvis")
ok = "terminantemente proibido" in p
print(f"Servidor: {len(app.routes)} rotas")
print(f"Diretriz anti-passos ativa: {ok}")
