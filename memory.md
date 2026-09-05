# DEEP-OS — Memoria do Projeto

## Visao Geral
Sistema operacional de agentes de IA com 3 modos de interacao:
- **Chat** (texto) — Jarvis via OpenRouter ou modelos locais
- **Voz** (Live API) — Charon via Google Gemini Live
- **SaaS** — Multi-tenant para venda/locacao

## Deploy Atual
- **VPS:** Hostinger, IP `2.25.143.185`, Ubuntu 26.04
- **Dominio:** `deep-os.tech`
- **Docker:** `docker-compose.prod.yml` (backend + frontend)
- **Update:** `cd /root/DEEP-OS && bash deploy.sh`

## Arquitetura
- **Backend:** FastAPI (Python 3.11 no Docker, 3.14 no VPS manual)
- **Frontend:** React + Vite (TypeScript)
- **Config:** `config.yaml` (identity, tools, agent_models)
- **Start Windows:** `C:\DEEP-OS\START-TOTAL.bat`
- **Start VPS:** `docker compose -f docker-compose.prod.yml up -d`

## Arquitetura Docker (Producao)

```
[Navegador] :80 → [nginx] :80
                      ↓ proxy
              [frontend:5176] [backend:8001]
                                 ↑
                          [chatbot:8010]
```

### nginx proxy reverso
- `/` → frontend (Vite)
- `/api/`, `/auth/`, `/chat/`, `/voice/`, `/admin/`, `/ws/` → backend (8001)
- WebSocket upgrade para `/voice/`, `/chat/`, `/ws/`

## Estrutura Principal

### Backend (`backend/`)
- `main.py` — FastAPI + CORS + rotas
- `routes/chat.py` — Chat com Jarvis
- `routes/voice_ws.py` — Gemini Live WebSocket (Charon) — **1700+ linhas**
- `routes/agent.py` — Execucao de agentes
- `routes/config.py` — Endpoints de config (identity, agent-models)
- `routes/ws_terminal.py` — Terminal WebSocket
- `agents/orchestrator.py` — Resolucao de modelos
- `tools/executor.py` — Execucao de tools
- `actions/` — 24 actions do Charon
- `memory/config_manager.py` — Leitura/salvamento de config
- `config/api_keys.json` — API keys + identity

### Frontend (`frontend/src/`)
- `components/saas/CharonPage.tsx` — Interface do Charon (voz + chat)
- `components/saas/AuthPage.tsx` — Login/registro SaaS
- `components/saas/SettingsPage.tsx` — Configuracoes
- `components/saas/AgentsPage.tsx` — Agentes e modelos
- `components/saas/Sidebar.tsx` — Menu lateral
- `components/saas/SaaSApp.tsx` — Layout SaaS
- `vite.config.ts` — Proxy + host config

### Config (`config.yaml`)
```yaml
identity:
  assistant_name: hugo
  user_name: wesley
  voice: charon

charon_toolset: full

agent_models:
  jarvis: qwen2.5-coder:14b
  architect: qwen3:14b
  debugger: qwen2.5-coder:14b
  planner: qwen3.5:9b
  coder: qwen2.5-coder:14b
```

## Sessoes Recentes

### Sessao 30 (2026-09-05) — Deploy VPS
- Deploy completo em VPS Hostinger
- Docker Compose + nginx proxy
- CORS + Vite host 0.0.0.0
- pyautogui/sounddevice import fix (headless)
- ws_terminal.py encoding fix (Python 3.14)
- Git history cleanup (removido .rar 554MB)
- Dominio `deep-os.tech` apontando para VPS

### Sessao 29 (2026-09-04) — Mark-LI Port
- Portacao de 10 funcionalidades do Mark-LI para Charon
- Audio fix (ring buffer 192000, prebuffer 12000)
- Filtro de contexto para topicos relevantes
- Painel central (atividades) separado do painel direito (voz)
- Briefing simplificado com temperatura + status

### Sessao 28 (2026-08-27) — Audio Fix
- MIME type `audio/pcm` → `audio/pcm;rate=16000`
- `_resolve_voice()` case-insensitive
- Greeting dinamico com `identity.assistant_name`

### Sessao 27 (2026-08-27) — Frontend Fix
- 8 bugs corrigidos (StatusBar, VoiceHud, CharonPanel, ToolPanel)
- Toggle buttons melhorados
- Agent models configuraveis

### Sessao 25 (2026-08-27) — Tools Fix
- EXTRA_TOOL_DECLARATIONS duplicado (12 tools perdidas)
- MEDIUM sem bash/read_file
- Cache de `_get_charon_toolset()`

## Ferramentas Charon (3 niveis)
- **BASIC (18):** open_app, web_search, system_status, weather_report, send_message, reminder, youtube_video, screen_process, computer_settings, browser_control, file_controller, desktop_control, code_helper, dev_agent, computer_control, file_processor, bash, read_file
- **MEDIUM (18):** Todas BASIC (recomendado)
- **FULL (26):** MEDIUM + write_file, save_document, file_edit, web_fetch, memory_save, memory_recall

## Vozes Gemini Live
| Voz | Tipo |
|-----|------|
| Charon | Masculina (padrao) |
| Puck | Masculina |
| Fenrir | Masculina |
| Orus | Masculina |
| Kore | Feminina |
| Leda | Feminina |
| Aoede | Feminina |
| Zephyr | Feminina |

## Pendencias

### Deploy (IMEDIATO)
- [ ] Instalar nginx no VPS
- [ ] Configurar nginx para `deep-os.tech`
- [ ] Verificar Docker build
- [ ] Criar primeira conta admin no SaaS

### Deploy Automatico
- [ ] Configurar GitHub Actions secrets
- [ ] Testar auto-deploy via push

### VPS
- [ ] Systemd services (backend + frontend + chatbot)
- [ ] SSL/HTTPS com Let's Encrypt
- [ ] Script `start-saas.sh` para Linux

### Funcionalidades
- [ ] ElevenLabs API key
- [ ] web_fetch User-Agent upgrade
- [ ] Wake word falsos positivos
- [ ] llamacpp context overflow

## Comandos Uteis

```bash
# Deploy no VPS
cd /root/DEEP-OS && bash deploy.sh

# Docker manual
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f

# Windows
C:\DEEP-OS\START-TOTAL.bat
C:\DEEP-OS\STOP-TOTAL.bat
```

## Regras Importantes

1. **Painel direito Charon** — Cada palavra como entrada SEPARADA com timestamp (nao acumular)
2. **Identity sync** — `PUT /api/config/identity` salva em 3 lugares (root config, backend config, api_keys.json)
3. **Voice save** — `handleSaveVoice` deve enviar identity completa (nao so voice)
4. **Git** — Branch e `master` (nao `main`)
5. **VPS** — Python 3.14, sempre usar `opencv-python-headless`
6. **Docker** — Backend Python 3.11 (compatibilidade)
