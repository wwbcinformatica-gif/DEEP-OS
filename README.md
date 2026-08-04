97 arquivos Python OK, zero erros. DEEP-AUREA está no ar! 🎉
Resumo do que foi feito:
🌀 Sistema Deep-Aurea (Spiral Memory)
- backend/core/spiral_memory.py — Módulo completo do Keeper (Modelo B):
- extrair_snapshot() — Extração rule-based do contexto (arquivo atual, erros, decisões)
- formatar_snapshot_para_prompt() — Formata como system message compacta
- gerar_snapshot_com_llm() — Usa Modelo B (ex: deepseek-r1:7b) para sumarização semântica
- deve_refrescar() — Decide quando refrescar (a cada 4 passos)
- backend/core/lifecycle.py — Adicionado on_spiral_refresh callback no loop principal
- backend/agents/loop.py — Integrado: a cada 4 passos, Keeper extrai contexto e injeta no Worker
- backend/core/agent_config.py — Suporte a SpiralMemoryConfig lido do config.yaml
- config.yaml — Seção spiral_memory: com keeper_model: deepseek-r1:7b
🏷️ Renomeação completa
- 📁 Pasta: C:\WBC-ZERO-G 5.0 → C:\DEEP-AUREA
- 📄 ~50 arquivos atualizados (log prefixes, docstrings, títulos, paths)
- 🧹 Referências WBC-PDV removidas do config.yaml e manual
🚀 Como usar
O spiral memory já está ativo por padrão. O Keeper usa deepseek-r1:7b (Ollama) pra sumarizar, mas se não estiver disponível, cai pra regras deterministicas. Configurável em config.yaml:
spiral_memory:
  enabled: true
  interval: 4
  keeper_provider: "ollama"
  keeper_model: "deepseek-r1:7b"
ℹ️ O venv antigo pode não funcionar após o rename — rode python -m venv venv pra recriar.
▣  Build · DeepSeek V4 Flash Free · 11m 38s
ok maravilha muito bom agora vou testar todo o contexto desta conversa em relação a este projeto deica organizado aqui por favor  C:\WBC-PDV 2.0\README.md
+ Thought: 12.4s
→Read README.md 
+ Thought: 5.4s
# Wrote README.md
# 🧠 DEEP-AUREA

**Sistema Operacional de Agentes de IA** — antigo WBC-ZERO-G 5.0

Plataforma full-stack que orquestra múltiplos agentes de IA especializados para automatizar tarefas de engenharia de software. Opera 100% local com suporte a múltiplos provedores de LLM.

---

## 📁 Localização

```
C:\DEEP-AUREA\
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
C:\DEEP-AUREA\START-TOTAL.bat
```

### Menu rápido
```bash
C:\DEEP-AUREA\run.bat
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

© 2026 DEEP-AUREA. Todos os direitos reservados.

+ Thought: 606ms
Pronto! README.md completo em C:\WBC-PDV 2.0\README.md com:
- Visão geral do DEEP-AUREA
- Arquitetura completa
- Spiral Memory — explicação, arquivos, configuração, 3 níveis de sumarização
- Fluxo do Keeper (Modelo B) em espiral
- Todos os agentes, skills, provedores
- Notas pós-rename
Pode testar o sistema agora que está tudo documentado! 🚀
▣  Build · DeepSeek V4 Flash Free · 3m 0s
top de mais muito obrigado]
+ Thought: 432ms
Por nada! Foi um prazer criar o Deep-Aurea com você. O sistema de memória espiral é uma ideia genuinely inovadora — dois modelos trabalhando em sincronia é algo que pouca gente pensou em fazer.
Se precisar de algo mais é só chamar. Boa sorte com os testes! 🚀🌀