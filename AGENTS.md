# DEEP-AUREA - Agent Instructions

## Project Overview
DEEP-AUREA is an AI Agent Operating System (Sistema Operacional de Agentes de IA). It orchestrates multiple specialized AI agents to automate software engineering tasks. Runs 100% locally with support for multiple LLM providers.

## Tech Stack
- **Backend**: Python (FastAPI + Uvicorn) at `backend/`
- **Frontend**: React + TypeScript (Vite) at `frontend/`
- **Config**: `config.yaml` for agent settings
- **Memory**: Spiral Memory system in `backend/core/spiral_memory.py`
- **Database**: SQLite with pooled connections at `backend/database/`

## Commands
- `START-TOTAL.bat` - Start both backend and frontend (recommended)
- `npm run dev` - Start both backend and frontend
- `npm run dev:backend` - Start backend only (port 8001)
- `npm run dev:frontend` - Start frontend only (port 5175)
- `npm run build` - Build frontend
- `npm run test` - Run all tests
- `npm run lint` - Run linters
- `STOP-TOTAL.bat` - Stop all services

## Project Structure
```
C:\DEEP-AUREA\
├── backend/          # Python FastAPI backend
│   ├── core/         # Core modules (spiral_memory, lifecycle, agent_config, secrets, log_viewer)
│   ├── agents/       # Agent loop and configurations
│   ├── cron/         # Cron scheduler (real asyncio execution)
│   ├── database/     # SQLite pool + triggers system
│   ├── memory/       # Elastic memory, vector memory (FAISS), brain
│   └── routes/       # API routes (chat, cron, triggers, secrets, logs, etc.)
├── frontend/         # React + TypeScript (Vite)
│   └── src/
│       └── components/  # UI components (ArchitecturePage, ChatPanel, etc.)
├── .memory/          # Portable project memory (junction from mimocode)
├── docs/             # Documentation (architecture.html)
├── config.yaml       # Main configuration file
├── .mimocode/        # MiMo Code portable installation
│   └── bin/mimo.exe  # MiMo Code executable
└── mimo.bat          # Launch MiMo Code from this project
```

## Portable Memory (CRITICAL)
The MiMo Code memory system stores durable knowledge in `.memory/` inside the project directory. A junction links from `~/.local/share/mimocode/memory/projects/global/` to `C:\DEEP-AUREA\.memory\`.

**When moving this project to another machine:**
1. Copy the entire `C:\DEEP-AUREA\` folder
2. On the new machine, run: `mklink /J "%USERPROFILE%\.local\share\mimocode\memory\projects\global" "C:\DEEP-AUREA\.memory"`
3. Memory is now portable — all 14+ files of project knowledge travel with the project

## Auto-Learning Rule
The agent MUST automatically:
1. Save knowledge to `.memory/MEMORY.md` without being asked
2. Create and update tasks in the task tracker without asking
3. Learn from every interaction and store patterns
4. Execute tasks autonomously without waiting for confirmation at each step

## APIs do Sistema
- `POST/GET/DELETE /cron` — Scheduler real com execucao via asyncio
- `POST/GET/DELETE /triggers` — Database triggers (watch SQLite tables)
- `POST/GET/DELETE /secrets` — Gerenciamento de .env
- `GET/DELETE /logs` — Viewer estruturado de logs
- `POST /chat/stream` — Chat SSE com streaming
- `GET/POST /memory` — Sistema de memoria
- `POST /agent/execute` — Execucao direta de agentes

## Guidelines
- Backend runs on port 8001 (dev) or 8000 (production)
- Frontend runs on port 5175 (Vite dev server)
- Config is centralized in config.yaml
- Use Portuguese (PT-BR) for all user-facing messages
- Follow existing code patterns in backend/ and frontend/
- Memory is AUTOMATIC — agent saves learnings without being asked
