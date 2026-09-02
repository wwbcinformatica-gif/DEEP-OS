# DEEP-OS - Memoria do Projeto

## Visao Geral
Assistente de IA pessoal com 3 modos de interacao:
- **Chat** (texto) — Jarvis via OpenRouter ou modelos locais
- **Voz** (Live API) — Charon via Google Gemini Live
- **Text-to-Speech** — ElevenLabs (mais natural que Gemini TTS)

## Arquitetura
- **Backend:** FastAPI (Python) em `C:\DEEP-OS\backend\`
- **Frontend:** React + Vite (TypeScript) em `C:\DEEP-OS\frontend\`
- **Config:** `C:\DEEP-OS\config.yaml`
- **Start:** `C:\DEEP-OS\START-TOTAL.bat`

## Estrutura Principal

### Backend (`backend/`)
- `main.py` — Servidor FastAPI, rotas, CORS
- `routes/chat.py` — Chat com Jarvis (usa `orchestrator.py`)
- `routes/voice_ws.py` — WebSocket Gemini Live (Charon)
- `routes/agent.py` — Execucao de agentes (Architect, Debugger, etc)
- `routes/config.py` — Endpoints de configuracao (identity, agent-models)
- `routes/knowledge.py` — Upload de PDFs/imagens
- `routes/memoria.py` — Memoria persistente
- `routes/mcp.py` — Integracao MCP
- `agents/orchestrator.py` — Resolucao de modelos por tarefa
- `tools/` — 47 ferramentas (file, browser, code, system, etc)

### Frontend (`frontend/src/`)
- `App.tsx` — Layout principal: Explorer | Chat | Charon
- `components/` — 30+ componentes React
  - `ConfigModal.tsx` — Modal de configuracao com 7 abas
  - `AgentsPage.tsx` — Configuracao de agentes e modelos
  - `KnowledgePage.tsx` — Upload e gerenciamento de conhecimento
  - `SettingsPage.tsx` — Configuracoes gerais
  - `ChatPanel.tsx` — Interface do chat
  - `VoicePanel.tsx` — Interface do Charon (voz)
  - `MiniMonitors.tsx` — CPU/RAM/GPU no header
  - `SecurityToggle.tsx` — Toggle de seguranca
- `lib/constants.ts` — Constantes e tipos

### Config (`config.yaml`)
```yaml
identity:
  assistant_name: "DEEP-OS"
  user_name: "Lucas"
  theme: "matrix"
  mood: "profissional"

agent_models:
  jarvis: qwen2.5-coder:14b
  architect: qwen3:14b
  debugger: qwen2.5-coder:14b
  planner: qwen3.5:9b
  coder: qwen2.5-coder:14b
```

## Sessoes Recentes

### Sessao 26 (2026-08-27)
- **Correcao Audio Charon** — 3 bugs em `voice_ws.py`:
  - MIME type `audio/pcm` → `audio/pcm;rate=16000` (Gemini ignorava audio sem taxa)
  - `_resolve_voice()` case-insensitive (GEMINI_VOICES tinha chaves minusculas)
  - Greeting dinamico usa `identity.assistant_name` em vez de hardcoded "Charon"

### Sessao 25 (2026-08-27)
- **Correcao Critica Charon** — 4 bugs corrigidos em `voice_ws.py`:
  - `EXTRA_TOOL_DECLARATIONS` definido 2x (sobrescrevia tools)
  - `MEDIUM` sem bash/read_file (16 tools → 18)
  - `_ensure_receive_loop` duplicado
  - `_get_charon_toolset()` sem cache (lia config.yaml a cada chamada)
- Contagens: BASIC=18, MEDIUM=18, FULL=26

### Sessao 23 (2026-08-27)
- **Dropdown Customizado** — `CustomDropdown` com `ReactDOM.createPortal` para evitar clipping
- **Agent Models** — Selecao de modelo por agente, persistido em config.yaml
- **Toggle Melhorado** — Knob circular com `var(--bg-2)` em vez de branco
- **Layout ConfigModal** — 7 abas com sub-abas (Conhecimento, Agentes)

### Sessao 22 (2026-08-27)
- **Identity System** — Nome do assistente e usuario configuravel
- **Voice Selector** — 8 vozes Gemini Live (Charon, Puck, Fenrir, Orus, Kore, Leda, Aoede, Zephyr)
- **Layout Redesign** — Explorer | Chat | Charon com drag handles
- **MiniMonitors** — CPU/RAM/GPU no header
- **Terminal no Config** — Aba Monitor/Terminal integrada

### Sessao 21 (2026-08-26)
- **ElevenLabs TTS** — Voz mais natural que Gemini
- **Memory Page** — Gerenciamento de memoria persistente
- **Knowledge Page** — Upload de PDFs e imagens

### Sessao 20 (2026-08-26)
- **MCP Integration** — Servidores MCP configuraveis
- **Architect Agent** — Agente de arquitetura de software
- **Debugger Agent** — Agente de debug

## Pendencias

### Prioridade Alta
- [ ] ElevenLabs — Configurar `ELEVENLABS_API_KEY` em `backend/.env`
- [ ] MiMo Executor — Implementar `--continue` para contexto entre mensagens
- [ ] web_fetch — User-Agent upgrade (403 em Cloudflare)

### Prioridade Media
- [ ] CDP — Conexao Chrome via porta 9222
- [ ] Fill form — Preenchimento automatico via Charon
- [ ] Screenshot — Captura de tela para analise

### Prioridade Baixa
- [ ] Wake word — Reduzir falsos positivos
- [ ] llamacpp — Aumentar `--ctx-size` ou reduzir system prompt
- [ ] GPU detection — Verificar VRAM apos reinicializacao

## Comandos Uteis
```bash
# Iniciar sistema
C:\DEEP-OS\START-TOTAL.bat

# Limpar processos
C:\DEEP-OS\Limpar_Processos_Memoria.bat

# Atualizar frontend (aps mudancas)
Ctrl+F5 no navegador
```

## Modelos Disponiveis
| Modelo | Tipo | Nota |
|--------|------|------|
| qwen2.5-coder:14b | Coding | Bom equilibrio |
| qwen3:14b | Raciocinio | Avancado |
| qwen3.5:9b | Raciocinio | Leve |
| deepseek-coder-v2 | Coding | Especialista |
| gemma4:12b | Geral | Google |
| llama-3.2:3b | Geral | Leve |
| qwen3-vl:8b | Multimodal | Vision |

## Ferramentas Charon (3 niveis)
- **BASIC (18):** open_app, web_search, system_status, weather_report, send_message, reminder, youtube_video, screen_process, computer_settings, browser_control, file_controller, desktop_control, code_helper, dev_agent, computer_control, file_processor, bash, read_file
- **MEDIUM (18):** Todas BASIC (recomendado)
- **FULL (26):** MEDIUM + write_file, save_document, file_edit, web_fetch, memory_save, memory_recall

## Notas Importantes
- **Voz nao muda em sessao** — Precisa desconectar e reconectar
- **Toggle Chat** — ControlaCharon panel (lado direito)
- **Toggle Explorer** — Controla painel esquerdo
- **Drag handle** — Vermelho entre Chat/Charon
- **Config** — Botao engrenagem no header abre modal
