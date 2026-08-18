# 🧠 DEEP-AUREA

**Sistema Operacional de Agentes de IA** — antigo WBC-ZERO-G 5.0

Plataforma full-stack que orquestra múltiplos agentes de IA especializados para automatizar tarefas de engenharia de software. Opera 100% local com suporte a múltiplos provedores de LLM. Inclui o **Charon**, assistente de voz com 20 ferramentas via Gemini Live.

---

## 📁 Localização

```
G:\DEEP-AUREA\
```

---

## 🌀 Spiral Memory (Deep-Aurea)

Sistema de memória em espiral onde **dois modelos** trabalham em sincronia:

### Modelo A (Worker)
- Executa ferramentas, gera código, resolve a tarefa
- Modelo principal configurado em `config.yaml` (`model.default`)

### Modelo B (Keeper)  
- Monitora o contexto do Worker a cada N passos
- Extrai: arquivo atual, última ação, erros, decisões, progresso
- Gera um **snapshot compacto** da memória de trabalho
- Reinjeta como mensagem de sistema no Worker

### Como funciona

```
Worker (Modelo A) ──executa ferramentas──▶ contexto cresce
                                              │
                  Keeper (Modelo B) ◀──────────┘
                       │  (a cada 4 passos)
                       ▼
         Extrai snapshot + sumariza
                       │
         Injeta no prompt do Worker
                       │
                      ◀─── espiral contínua
```

### Arquivos do Spiral Memory

| Arquivo | Descrição |
|---------|-----------|
| `backend/core/spiral_memory.py` | Módulo principal do Keeper |
| `backend/core/lifecycle.py` | Engine de ciclo de vida com callback de refresh |
| `backend/agents/loop.py` | Integração: Keeper conectado ao Worker |
| `backend/core/agent_config.py` | Config `SpiralMemoryConfig` |

### Configuração (`config.yaml`)

```yaml
spiral_memory:
  enabled: true
  interval: 4
  keeper_provider: "ollama"
  keeper_model: "deepseek-r1:7b"
```

### Três níveis de sumarização

1. **Regras** (sempre ativo) — extração determinística de ferramentas, arquivos, erros
2. **Keeper LLM** (se `keeper_model` configurado) — usa Modelo B para sumarização semântica
3. **Fallback** — se Keeper LLM falhar, volta para regras

---

## 🏗️ Arquitetura

```
C:\DEEP-AUREA\
├── backend/          # FastAPI (Python) — servidor principal
│   ├── agents/       # Orquestrador, loop, teams, fork
│   ├── core/         # Lifecycle, LLM, RAG, prompts, segurança, spiral_memory
│   ├── routes/       # 28+ endpoints REST/WebSocket
│   ├── tools/        # Bash, leitura/escrita, web search, fetch
│   ├── memory/       # Memória vetorial, elástica, brain, reflexão
│   └── main.py       # Entrypoint FastAPI
├── frontend/         # React + TypeScript + Vite + Tailwind
│   └── src/          # Chat, Terminal, Explorer, Editor, Plan, etc.
├── .opencode/        # 25+ agentes e 20+ skills
├── skills/           # Skills de desenvolvimento
├── data/             # Memória persistente, brain, FAQ
└── docs/             # Docs e relatórios de auditoria
```

---

## 🔧 Tech Stack

| Camada | Tecnologias |
|--------|-------------|
| Backend | Python 3.10+, FastAPI, Uvicorn, Pydantic |
| Frontend | React 18, TypeScript 5, Vite 5, Tailwind 4, xterm.js |
| Banco | SQLite, Memória Vetorial (embeddings) |
| LLMs | Ollama (local), OpenAI, Groq, Gemini, OpenRouter, MiMo |
| Protocolos | REST, WebSocket, MCP, SSE (streaming) |
| Modelos locais | qwen3:14b, deepseek-r1:7b/14b, nemomix-12b, qwen2.5-coder |

---

## 🚀 Como usar

### Iniciar
```bash
G:\DEEP-AUREA\START-TOTAL.bat
```

### Menu rápido
```bash
G:\DEEP-AUREA\run.bat
```

### Acessos
| Serviço | URL |
|---------|-----|
| Frontend | http://localhost:5175 |
| Backend API | http://localhost:8001/docs |

---

## 🤖 Agentes Especializados (25+)

Orchestrator, Architect, Coder, Debugger, Backend-Specialist, Frontend-Specialist, Security-Auditor, Penetration-Tester, Database-Architect, DevOps-Engineer, Test-Engineer, Game-Developer, Mobile-Developer, SEO-Specialist, Documentation-Writer, Performance-Optimizer, Project-Planner, QA-Automation-Engineer, Product-Manager, Product-Owner, e mais.

---

## 📝 Skills (32+)

Clean Code, Architecture, Database Design, i18n, Vulnerability Scanner, WebApp Testing, Red Team Tactics, Frontend Design, Python Patterns, PowerShell Windows, Bash Linux, Code Review, Deployment Procedures, Plan Writing, e mais.

---

## ⚙️ Provedores Suportados

| Provider | Tipo | Modelo sugerido |
|----------|------|----------------|
| Ollama | Local | qwen3:14b, deepseek-r1:7b |
| Groq | Cloud | mixtral-8x7b, llama-3.1-70b |
| OpenAI | Cloud | gpt-4o |
| Gemini | Cloud | gemini-1.5-pro |
| OpenRouter | Cloud | vários |
| OpenClaude | Cloud/Self | deepseek-v4-flash |
| MiMo | Cloud | mimmo-7b-rl |

---

## 🎙️ Charon — Assistente de Voz

O **Charon** é o assistente de voz do DEEP-AUREA, baseado no **Gemini Live** (audio nativo) com **20 ferramentas** de função.

### Como usar
- **Falar:** clique no microfone e fale diretamente com o Charon (ou diga "aurea" para ativar o modo de voz do chat central).
- **Digitar:** abra o painel Charon (botão "T" na barra de status) e digite — o texto entra no contexto e o Charon responde por voz.
- **Ligar/desligar:** botão "⚡ Charon" na barra de status.
- **Interromper:** botão ⏹ no HUD de voz, ou fale "para", "silencio", "cala boca".

### Ferramentas principais
| Ferramenta | O que faz |
|-----------|-----------|
| `file_controller` | Criar/listar/deletar/mover arquivos e pastas, abrir documentos e imagens |
| `computer_control` | Mouse, teclado, cliques, hotkeys, screenshot |
| `browser_control` | Navegar, buscar, clicar, digitar no navegador |
| `open_app` | Abrir qualquer aplicativo |
| `file_processor` | OCR, resumos, conversões de PDF/docx/xlsx, transcrições |
| `web_search` / `web_fetch` | Pesquisar e baixar conteúdo da web |

### Comandos de voz úteis
| Fale | O que acontece |
|------|----------------|
| "criar pasta X" | Cria pasta em Documents/Desktop |
| "tira print da tela" | Screenshot com data/hora (nunca sobrescreve) |
| "abre o arquivo config.py" | Abre arquivos no aplicativo padrão |
| "para de ler" / "cala boca" | Interrompe a fala atual |
| "repetir" / "ler novamente" | Repete a última resposta |

> **Nota:** screenshots e resultados de processamento usam nomes com data/hora (`AAAAMMDD_HHMMSS`) para nunca sobrescrever arquivos anteriores. A listagem de pastas mostra sempre todas as pastas, limitando apenas os arquivos (até 100).

---

## 🔄 Fluxo do Spiral Memory (implementado em Jul/2026)

1. Worker inicia tarefa com ferramentas
2. A cada 4 passos, Lifecycle Engine chama Keeper
3. Keeper varre tool_logs + mensagens recentes
4. Gera snapshot (regras OU LLM)
5. Injeta `[DEEP-AUREA MEMORY REFRESH]` no contexto do Worker
6. Worker continua de onde parou com memória fresca

---

## 📌 Notas

- O venv precisa ser recriado após o rename: `python -m venv venv`
- Memória de reflexões e longo prazo em `data/memory/` (regenerável)
- O Spiral Memory é ativado por padrão — desligar em `config.yaml: spiral_memory.enabled: false`

---

---

## 👨‍💻 Desenvolvedor

| Campo | Valor |
|-------|-------|
| **Nome** | Wilson Barbosa Coimbra |
| **Empresa** | WBC |
| **Projeto** | DEEP-AUREA |

© 2026 DEEP-AUREA — Desenvolvido por **Wilson Barbosa Coimbra** (empresa **WBC**). Todos os direitos reservados.