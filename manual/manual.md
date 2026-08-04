# Manual do DEEP-AUREA

> **Sistema Operacional de Agentes de IA**
> VersÃ£o: 5.2.2 | Plataforma: Windows 11 Pro 64-bit
> Desenvolvedor: Wilson Barbosa Coimbra | Copyright Â© Empresa: WBC 2026

---

## SumÃ¡rio

1. [VisÃ£o Geral](#1-visÃ£o-geral)
2. [Arquitetura](#2-arquitetura)
3. [Hardware de ReferÃªncia](#3-hardware-de-referÃªncia)
4. [Estrutura do Projeto](#4-estrutura-do-projeto)
5. [Setup e InstalaÃ§Ã£o](#5-setup-e-instalaÃ§Ã£o)
6. [Provedores de LLM](#6-provedores-de-llm)
7. [Agentes DisponÃ­veis](#7-agentes-disponÃ­veis)
8. [Lifecycle Engine (v5.0)](#8-lifecycle-engine)
9. [Sistema de Skills](#9-sistema-de-skills)
10. [Sistema de Ferramentas](#10-sistema-de-ferramentas)
11. [MemÃ³ria de Longo Prazo](#11-memÃ³ria-de-longo-prazo)
12. [AutomaÃ§Ã£o e OrquestraÃ§Ã£o](#12-automaÃ§Ã£o-e-orquestraÃ§Ã£o)
13. [Interface Web](#13-interface-web)
14. [Protocolo de Checklist Visual (Mandamento nÂº 9)](#14-protocolo-de-checklist-visual)
15. [Calibragem de Temperatura](#15-calibragem-de-temperatura)
16. [Comandos Ãšteis](#16-comandos-Ãºteis)
17. [VariÃ¡veis de Ambiente](#17-variÃ¡veis-de-ambiente)

â†’ [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 1. VisÃ£o Geral

O **DEEP-AUREA** Ã© um **Sistema Operacional de Agentes de IA** â€” uma plataforma que orquestra mÃºltiplos agentes de inteligÃªncia artificial para automatizar tarefas de engenharia de software.

**Filosofia:** Em vez de uma IA que apenas responde perguntas, criar uma plataforma onde mÃºltiplas IAs trabalham juntas, com ferramentas reais, memÃ³ria persistente e autonomia para executar tarefas complexas.

**PrincÃ­pios:**
1. **Autonomia** â€” A IA deve agir, nÃ£o apenas sugerir
2. **EspecializaÃ§Ã£o** â€” Agentes diferentes para tarefas diferentes
3. **PersistÃªncia** â€” MemÃ³ria entre sessÃµes
4. **Flexibilidade** â€” MÃºltiplos provedores de LLM
5. **Escalabilidade** â€” Sub-agentes e teams para tarefas paralelas
6. **Extensibilidade** â€” Skills e plugins MCP

â†’ [PrÃ³ximo: Arquitetura](#2-arquitetura) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 2. Arquitetura

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              FRONTEND (React + Vite + TypeScript)         â”‚
â”‚   Chat Panel â”‚ Explorer â”‚ Editor â”‚ Terminal Web â”‚ Skills  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚ HTTP / WebSocket / Streaming
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚               BACKEND (FastAPI + Python)                   â”‚
â”‚  Chat â”‚ Tools â”‚ Agents â”‚ Memory â”‚ Workspace â”‚ Cron â”‚ MCP  â”‚
â”‚  Skills â”‚ TTS â”‚ Plan Mode â”‚ Teams â”‚ Monitor â”‚ Plugins      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
            â”‚                           â”‚
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚   SQLite (Banco)    â”‚     â”‚      LLMs            â”‚
  â”‚  history            â”‚     â”‚  Ollama (local)      â”‚
  â”‚  task_state         â”‚     â”‚  Groq (cloud)        â”‚
  â”‚  brain_memories     â”‚     â”‚  OpenAI (cloud)      â”‚
  â”‚  knowledge          â”‚     â”‚  Gemini (cloud)      â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚  OpenClaude (proxy)  â”‚
                              â”‚  OpenRouter (multi)  â”‚
                              â”‚  MiMo (Xiaomi)       â”‚
                              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Requisitos:** Python 3.10+, Node.js 18+, Ollama (para modelos locais) ou contas em provedores cloud.

â†’ [PrÃ³ximo: Hardware](#3-hardware-de-referÃªncia) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 3. Hardware de ReferÃªncia

| Componente | EspecificaÃ§Ã£o |
|------------|---------------|
| **CPU** | AMD Ryzen 5 PRO 2400GE (4C/8T, 3.2 GHz, Zen 14nm) |
| **RAM** | 16 GB DDR4 2667 MHz (2Ã—8 GB) |
| **GPU** | NVIDIA RTX 3060 4GB (Ampere) |
| **SSD Principal** | 512 GB NVMe |
| **Armazenamento Total** | ~6 TB (512GB SSD + 500GB HDD + 1TB + 2Ã—2TB) |
| **Placa-mÃ£e** | ASRock B450M Steel Legend (BIOS P10.30) |
| **SO** | Windows 11 Pro 64-bit (Build 26200) |
| **Rede** | Intel Dual Band Wireless-AC 7265 (Wi-Fi) |

â†’ [PrÃ³ximo: Estrutura](#4-estrutura-do-projeto) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 4. Estrutura do Projeto

```
DEEP-AUREA/
â”œâ”€â”€ backend/                 â† API FastAPI (Python)
â”‚   â”œâ”€â”€ agents/              â† Agentes autÃ´nomos (loop, orquestrador, fork)
â”‚   â”œâ”€â”€ core/                â† NÃºcleo (config, workspace, LLM, prompts)
â”‚   â”‚   â”œâ”€â”€ state_machine.py â† MÃ¡quina de estados do ciclo de vida
â”‚   â”‚   â””â”€â”€ lifecycle.py     â† Engine de ciclo de vida do agente
â”‚   â”œâ”€â”€ database/            â† SQLite (conexÃ£o, init)
â”‚   â”œâ”€â”€ generator/           â† Gerador de projetos
â”‚   â”œâ”€â”€ memory/              â† MemÃ³ria de longo prazo e reflexÃ£o
â”‚   â”œâ”€â”€ plugins/             â† Sistema MCP
â”‚   â”œâ”€â”€ routes/              â† 26+ endpoints da API
â”‚   â”œâ”€â”€ tasks/               â† Gerenciamento de tarefas
â”‚   â””â”€â”€ tools/               â† Ferramentas (read, write, bash, search...)
â”œâ”€â”€ frontend/                â† Interface React + Vite + TypeScript
â”‚   â””â”€â”€ src/
â”‚       â”œâ”€â”€ components/      â† Componentes React
â”‚       â””â”€â”€ hooks/           â† Hooks customizados
â”œâ”€â”€ skills/                  â† Skills do agente (documentos estruturados)
â”œâ”€â”€ .opencode/               â† ConfiguraÃ§Ã£o e skills do OpenCode
â”œâ”€â”€ 0-Projetos/              â† Projetos em desenvolvimento
â”œâ”€â”€ manual/                  â† Este manual
â”œâ”€â”€ config.yaml              â† ConfiguraÃ§Ã£o principal
â”œâ”€â”€ START-TOTAL.bat          â† InicializaÃ§Ã£o unificada
â””â”€â”€ STOP-TOTAL.bat           â† Parada unificada
```

â†’ [PrÃ³ximo: Setup](#5-setup-e-instalaÃ§Ã£o) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 5. Setup e InstalaÃ§Ã£o

### InstalaÃ§Ã£o RÃ¡pida

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # edite com suas chaves de API
uvicorn main:app --host 0.0.0.0 --port 8001

# Frontend (outro terminal)
cd frontend
npm install
npm run dev
```

### InicializaÃ§Ã£o Unificada

```bash
# Iniciar tudo (Backend + Frontend + Navegador)
.\START-TOTAL.bat

# Parar tudo
.\STOP-TOTAL.bat
```

Acesse `http://localhost:5173`

â†’ [PrÃ³ximo: Provedores](#6-provedores-de-llm) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 6. Provedores de LLM

| Provedor | Tipo | Modelos | Requer chave? |
|----------|------|---------|---------------|
| **Ollama** | Local | Locais (qwen, deepseek, gemma, etc.) | NÃ£o |
| **OpenClaude** | Proxy local | Claude Sonnet, Haiku | Sim |
| **OpenRouter** | Cloud multi | VÃ¡rios modelos | Sim |
| **Groq** | Cloud | InferÃªncia ultra-rÃ¡pida | Sim |
| **OpenAI** | Cloud | GPT-4, GPT-4o | Sim |
| **Gemini** | Cloud | Gemini 1.5 Pro | Sim |
| **OpenCode** | Cloud | Modelos OpenCode | Sim |
| **MiMo** | Cloud (Xiaomi) | mimo-v2.5 (gratuito por tempo limitado) | Sim |

â†’ [PrÃ³ximo: Agentes](#7-agentes-disponÃ­veis) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 7. Agentes DisponÃ­veis

### Agentes Locais (Ollama)

| Agente | Modelo | FunÃ§Ã£o |
|--------|--------|--------|
| `@general` | qwen3.5:9b | Assistente geral de engenharia de software |
| `@explore` | Qwen 2.5 Coder 7B | Explorador de cÃ³digo e estrutura |
| `@plan` | deepseek-r1:14b | Planejador de tarefas complexas |
| `@architect` | deepseek-r1:7b | Arquiteto de software |
| `@debugger` | deepseek-coder:6.7b | Debugger especialista |
| `@coder` | gemma4:12b | Programador especialista |
| `@tools` | nemomix-tools:latest | Chamadas de ferramentas |

### Agentes OpenClaude (.opencode/agent/)

| Agente | Especialidade |
|--------|---------------|
| `@general` | Assistente geral full-stack |
| `@explore` | ExploraÃ§Ã£o de cÃ³digo |
| `@plan` | Planejamento de arquitetura |
| `@architect` | Arquiteto de software sÃªnior |
| `@debugger` | Debugging sistemÃ¡tico |
| `@coder` | Programador especialista |
| `@backend-specialist` | Arquitetura backend |
| `@frontend-specialist` | Arquitetura frontend |
| `@database-architect` | Modelagem de dados |
| `@devops-engineer` | Deploy e CI/CD |
| `@security-auditor` | Auditoria de seguranÃ§a |
| `@game-developer` | Desenvolvimento de jogos |
| `@mobile-developer` | Apps mobile |
| `@orchestrator` | CoordenaÃ§Ã£o multi-agente |
| `@test-engineer` | Testes automatizados |
| `@qa-automation-engineer` | AutomaÃ§Ã£o E2E |
| `@performance-optimizer` | OtimizaÃ§Ã£o de performance |
| `@product-manager` | Requisitos de produto |
| `@project-planner` | Planejamento de projetos |
| `@documentation-writer` | DocumentaÃ§Ã£o tÃ©cnica |
| `@seo-specialist` | SEO e GEO |
| `@penetration-tester` | Testes ofensivos |
| `@code-archaeologist` | RefatoraÃ§Ã£o de cÃ³digo legado |

### Agente MiMo (Xiaomi)

| Agente | Modelo | FunÃ§Ã£o |
|--------|--------|--------|
| `@mimo` | mimo-v2.5 | Assistente geral rÃ¡pido (gratuito) |

### Agente Coworking

| Agente | Modelo | FunÃ§Ã£o |
|--------|--------|--------|
| Claude Coworker | Claude Sonnet 4.6 | Agente colaborativo estilo Cursor |

â†’ [PrÃ³ximo: Lifecycle Engine](#8-lifecycle-engine) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 8. Lifecycle Engine (v5.0)

O **Lifecycle Engine** Ã© a mÃ¡quina de estados finita que orquestra todo o ciclo de vida da execuÃ§Ã£o do agente LLM. Substituiu o loop procedural antigo por uma arquitetura baseada em estados com transiÃ§Ãµes explÃ­citas e logs estruturados.

### Arquivos

| Arquivo | FunÃ§Ã£o |
|---------|--------|
| `backend/core/state_machine.py` | EnumeraÃ§Ã£o de estados, classificadores, validadores |
| `backend/core/lifecycle.py` | Engine assÃ­ncrona que executa o ciclo de vida |

### Estados da MÃ¡quina

```
START â†’ CALL_MODEL â†’ CHECK_RESPONSE
  â†’ API_ERROR (retry loop) â†’ CALL_MODEL
  â†’ ACCUMULATE_STREAM (chunk loop) â†’ CLASSIFY_FINISH
  â†’ CLASSIFY_FINISH â†’ (
      tool_calls   â†’ VALIDATE_TOOL â†’ EXECUTE_TOOL â†’ APPEND_OBSERVATION â†’ CALL_MODEL
      length       â†’ TRUNCATED
      content_filter â†’ FILTERED
      stop         â†’ CLASSIFY_CONTENT â†’ (
          has_response â†’ FINAL
          only_think   â†’ THINK_ONLY â†’ (nudge â†’ CALL_MODEL | exceed_limit â†’ FAILED)
      )
  )
```

### Ciclo Completo

| # | Estado | DescriÃ§Ã£o |
|---|--------|-----------|
| 1 | `START` | InÃ­cio do ciclo, inicializaÃ§Ã£o do estado |
| 2 | `CALL_MODEL` | Chamada Ã  API do LLM (streaming ou non-streaming) |
| 3 | `CHECK_RESPONSE` | VerificaÃ§Ã£o do tipo de resposta recebida |
| 4 | `API_ERROR` | Erro na API â†’ retry com backoff exponencial |
| 5 | `ACCUMULATE_STREAM` | AcumulaÃ§Ã£o de chunks de streaming |
| 6 | `CLASSIFY_FINISH` | ClassificaÃ§Ã£o do `finish_reason` |
| 7 | `VALIDATE_TOOL` | ValidaÃ§Ã£o de nome e argumentos da ferramenta |
| 8 | `EXECUTE_TOOL` | ExecuÃ§Ã£o da ferramenta com timeout |
| 9 | `APPEND_OBSERVATION` | Registro do resultado na memÃ³ria contextual |
| 10 | `TRUNCATED` | Resposta interrompida por limite de tokens |
| 11 | `FILTERED` | Resposta bloqueada por filtro de conteÃºdo |
| 12 | `CLASSIFY_CONTENT` | AnÃ¡lise: resposta final ou apenas raciocÃ­nio? |
| 13 | `THINK_ONLY` | Apenas raciocÃ­nio interno â†’ nudge para continuar |
| 14 | `FINAL` | Resposta final entregue ao usuÃ¡rio |
| 15 | `FAILED` | Falha (limite de raciocÃ­nio interno excedido) |

### ClassificaÃ§Ã£o do Finish Reason

| `finish_reason` | Estado | AÃ§Ã£o |
|-----------------|--------|------|
| `tool_calls` / `function_call` | `TOOL_CALLS` | Validar â†’ executar â†’ observar â†’ repetir ciclo |
| `length` / `max_tokens` | `TRUNCATED` | Retornar resposta parcial com aviso |
| `content_filter` | `FILTERED` | Retornar mensagem de bloqueio |
| `stop` / `end_turn` | `CLASSIFY_CONTENT` | Analisar se hÃ¡ resposta ou apenas raciocÃ­nio |

### ClassificaÃ§Ã£o de ConteÃºdo

| Categoria | CritÃ©rio | AÃ§Ã£o |
|-----------|----------|------|
| `HAS_RESPONSE` | ConteÃºdo nÃ£o-vazio no `content` | `FINAL` â†’ retorna ao usuÃ¡rio |
| `ONLY_THINK` | ConteÃºdo vazio, apenas `reasoning` | `THINK_ONLY` â†’ nudge de volta ao modelo |

### Mecanismo de Nudge (Think-Only)

Quando o modelo retorna apenas raciocÃ­nio interno sem resposta:

1. Contagem incrementa (`think_only_count`)
2. Se exceder `max_think_only_loops` (default: 3) â†’ `FAILED`
3. Caso contrÃ¡rio, injeta mensagem forÃ§ando resposta final:
   ```
   [SISTEMA] Seu raciocinio interno foi registrado.
   Agora apresente a RESPOSTA FINAL ao usuario.
   Nao use <think> tags â€” escreva diretamente a resposta.
   ```

### Retry com Backoff Exponencial

```
Tentativa 1: falha â†’ espera 1.0s
Tentativa 2: falha â†’ espera 2.0s
Tentativa 3: falha â†’ retorna erro
```

ConfigurÃ¡vel via `LifecycleConfig`:
- `max_api_retries`: mÃ¡ximo de tentativas (default: 3)
- `api_retry_base_delay`: delay inicial em segundos (default: 1.0)
- `api_retry_backoff`: multiplicador do delay (default: 2.0)

### ConfiguraÃ§Ã£o

```python
LifecycleConfig(
    max_tool_steps=100,        # mÃ¡ximo de passos do agente
    max_api_retries=3,         # tentativas de chamada Ã  API
    max_think_only_loops=3,    # loops de raciocÃ­nio interno antes de FAILED
    tool_timeout=60.0,         # timeout por ferramenta (segundos)
    consecutive_tool_limit=10, # forÃ§ar resposta final apÃ³s N tools seguidas
    api_retry_base_delay=1.0,  # delay base do retry
    api_retry_backoff=2.0,     # multiplicador do backoff
    # Anti-Loop Protection
    anti_loop_enabled=True,
    max_consecutive_state_hash=2,
    circuit_breaker_max_think=5,
    circuit_breaker_max_tools=20,
    # Planning Toll Enforcement
    planning_enforced=True,    # Ativar PedÃ¡gio de Planejamento
    planning_check_steps=2,    # Verificar nos primeiros N passos
)
```

### Planning Toll Enforcement (PedÃ¡gio de Planejamento)

O **PedÃ¡gio de Planejamento** Ã© um mecanismo de seguranÃ§a mecÃ¢nica implementado no `lifecycle.py` que **bloqueia a execuÃ§Ã£o de ferramentas** nos passos 1 e 2 do ciclo de vida atÃ© que o agente apresente:

1. **RaciocÃ­nio estruturado** em texto
2. **Checkboxes visuais** no formato Markdown (`- [ ] Meta 1`, `- [ ] Meta 2`)
3. **JSON task_plan** com campo `steps`

**Fluxo de validaÃ§Ã£o:**

```
PASSO 1 ou 2 com tool_calls:
  â†“
Verificar: _has_checkboxes(content) â‰¥ 2 checkboxes?
  â†“
Sim â†’ Verificar: _has_task_plan_json(content)?
  â†“
  Sim â†’ has_presented_plan = True â†’ liberar tools
  NÃ£o â†’ Nudge de correÃ§Ã£o â†’ forÃ§ar planejamento
  â†“
NÃ£o â†’ Nudge de correÃ§Ã£o: "ERRO DE PROTOCOLO CRITICO: Mandamento nÂº 9"
```

**ConfiguraÃ§Ã£o:**

```python
LifecycleConfig(
    planning_enforced=True,    # Ativar/desativar o pedÃ¡gio
    planning_check_steps=2,    # Verificar nos primeiros N passos
)
```

### Logs de TransiÃ§Ã£o

Cada transiÃ§Ã£o gera log estruturado para debug:
```
[DEEP-AUREA] TransiÃ§Ã£o: START -> CALL_MODEL (passo 1)
[DEEP-AUREA] TransiÃ§Ã£o: CALL_MODEL -> CHECK_RESPONSE (passo 1) | type=tool_calls
[DEEP-AUREA] TransiÃ§Ã£o: CHECK_RESPONSE -> CLASSIFY_FINISH (passo 1) | reason=tool_calls
[DEEP-AUREA] TransiÃ§Ã£o: CLASSIFY_FINISH -> VALIDATE_TOOL (passo 1) | tool=bash valid=True
[DEEP-AUREA] TransiÃ§Ã£o: VALIDATE_TOOL -> EXECUTE_TOOL (passo 1) | tool=bash
[DEEP-AUREA] TransiÃ§Ã£o: EXECUTE_TOOL -> APPEND_OBSERVATION (passo 1) | tool=bash
```

â†’ [PrÃ³ximo: Skills](#9-sistema-de-skills) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 9. Sistema de Skills

Skills sÃ£o **documentos estruturados em Markdown** que ensinam o agente a executar tarefas especÃ­ficas.

### Estrutura

```
skills/
â”œâ”€â”€ software-development/   # Skills de desenvolvimento
â”œâ”€â”€ devops/                 # Skills de infraestrutura
â”œâ”€â”€ security/               # Skills de seguranÃ§a
â”œâ”€â”€ research/               # Skills de pesquisa
â”œâ”€â”€ creative/               # Skills criativos
â”œâ”€â”€ data-science/           # Skills de dados
â””â”€â”€ apple/                  # Skills Apple
```

### Formato SKILL.md

| Campo | ObrigatÃ³rio | DescriÃ§Ã£o |
|-------|-------------|-----------|
| `name` | Sim | Identificador (kebab-case) |
| `description` | Sim | MÃ¡x 60 caracteres |
| `version` | Sim | Semver |
| `author` | Sim | Criador |
| `platforms` | Sim | Suporte por OS |

**SeÃ§Ãµes do corpo:** `When to Use`, `Prerequisites`, `How to Run`, `Procedure`, `Pitfalls`, `Verification`.

â†’ [PrÃ³ximo: Ferramentas](#10-sistema-de-ferramentas) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 10. Sistema de Ferramentas

O agente executa **aÃ§Ãµes reais** no sistema:

| Ferramenta | Capacidade |
|------------|------------|
| `read` / `write` / `delete` | ManipulaÃ§Ã£o de arquivos |
| `bash` | ExecuÃ§Ã£o de comandos (PowerShell) |
| `search` / `glob` | Busca de texto e arquivos |
| `explorer` | NavegaÃ§Ã£o em diretÃ³rios |
| `web_search` / `web_fetch` | Pesquisa na internet |
| `file_edit` | EdiÃ§Ã£o cirÃºrgica de arquivos |
| `task_create` / `task_update` | Tarefas assÃ­ncronas |
| `fork_subagent` | Sub-agentes em paralelo |
| `team_create` / `send_message` | CoordenaÃ§Ã£o entre agentes |
| `cron_create` | Tarefas recorrentes |
| `memory_write` / `memory_read` | MemÃ³ria de longo prazo |
| `monitor_dashboard` | Monitoramento CPU/RAM/logs |

â†’ [PrÃ³ximo: MemÃ³ria](#11-memÃ³ria-de-longo-prazo) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 11. MemÃ³ria de Longo Prazo

O sistema possui **4 namespaces de memÃ³ria persistente**:

| Namespace | FunÃ§Ã£o |
|-----------|--------|
| `conversations` | HistÃ³rico de conversas importantes |
| `project_knowledge` | Conhecimento acumulado sobre o projeto |
| `reflections` | ReflexÃµes e aprendizados da IA |
| `preferences` | PreferÃªncias do usuÃ¡rio |

A IA nÃ£o "esquece" entre sessÃµes â€” acumula conhecimento ao longo do tempo.

â†’ [PrÃ³ximo: AutomaÃ§Ã£o](#12-automaÃ§Ã£o-e-orquestraÃ§Ã£o) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 12. AutomaÃ§Ã£o e OrquestraÃ§Ã£o

| Recurso | FunÃ§Ã£o |
|---------|--------|
| **Cron Jobs** | Tarefas recorrentes |
| **Teams** | Times de agentes comunicando-se |
| **Sub-agents** | Forks para tarefas paralelas |
| **Plan Mode** | Modo de planejamento antes da execuÃ§Ã£o |
| **Tasks** | Tarefas assÃ­ncronas com status |
| **MCP Plugins** | IntegraÃ§Ã£o com sistemas externos |

### Fluxo de ExecuÃ§Ã£o TÃ­pico

```
1. UsuÃ¡rio faz solicitaÃ§Ã£o no Chat
   â†“
2. Agente @general analisa e decide se precisa de planejamento
   â†“
3. Se complexo â†’ @plan cria plano (Plan Mode)
   â†“
4. Plano aprovado â†’ Tarefas criadas
   â†“
5. Sub-agentes forkados para tarefas paralelas
   â†“
6. Cada sub-agente usa ferramentas (read, write, bash, search)
   â†“
7. Resultados consolidados e verificados
   â†“
8. MemÃ³ria atualizada
   â†“
9. Resposta final entregue ao usuÃ¡rio
```

â†’ [PrÃ³ximo: Interface](#13-interface-web) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 13. Interface Web

O frontend oferece:

- **Chat Panel** â€” Conversa com streaming em tempo real + barra de progresso
- **Explorer** â€” NavegaÃ§Ã£o de arquivos do projeto
- **Editor** â€” EdiÃ§Ã£o de cÃ³digo inline
- **Terminal Web** â€” Terminal PowerShell integrado
- **Skills Manager** â€” Gerenciamento de skills
- **Monitor** â€” Dashboard de CPU/RAM/logs

### Arquitetura do ChatPanel.tsx com TaskChecklist

O componente `ChatPanel.tsx` foi projetado com isolamento visual rigoroso para o `TaskChecklist`:

```
<div flex-column overflow:hidden>          â† Container raiz (overflow hidden)
  â”œâ”€â”€ Header (fixo)                       â† Titulo + botoes
  â”œâ”€â”€ Provider/Model Row (fixo)           â† Seletor de provedor e modelo
  â”œâ”€â”€ <TaskChecklist> (condicional)       â† FORA da area de scroll âœ…
  â””â”€â”€ <div flex:1 overflowY:auto>         â† Scroll exclusivo das mensagens
       â””â”€â”€ {msgs.map(...)}               â† Mensagens da conversa
```

**Destaques da arquitetura:**

| Componente | Posicao | Comportamento |
|-----------|---------|---------------|
| `<TaskChecklist>` | Fixo no topo, **fora do scroll** | Lista de checkboxes visuais com status (pending/running/done/error) |
| `<StatusIndicator>` | No header | Indicador de status do provedor |
| `<ThinkingPanel>` | Dentro do scroll | Painel colapsavel de raciocinio |
| Barra de progresso unificada | No TaskChecklist | Progresso visual com percentual e barra animada |

O `TaskChecklist` recebe `checklistSteps` como propriedade e renderiza:
- **Checkboxes azuis** (`- [~]`) para etapa em andamento
- **Checkboxes concluidos** (`- [x]`) para etapas finalizadas
- **Barra de progresso** com percentual em tempo real
- **Label "EM ANDAMENTO"** pulsante quando ha execucao ativa

â†’ [PrÃ³ximo: Protocolo de Checklist Visual](#14-protocolo-de-checklist-visual) | [Voltar ao indice](#sumario)

---

## 14. Protocolo de Checklist Visual (Mandamento nÂº 9)

O **Protocolo de Checklist Visual** Ã© o **Mandamento nÂº 9** do mood opencode â€” uma regra mecÃ¢nica e inquebrÃ¡vel que obriga o agente a apresentar seu raciocÃ­nio e plano visual antes de executar qualquer ferramenta.

### O que Ã© o Mandamento nÂº 9

> **"O agente DEVE apresentar checkboxes visuais e raciocÃ­nio estruturado ANTES de chamar qualquer ferramenta."**

Este protocolo garante que o usuÃ¡rio veja exatamente o que o agente pretende fazer antes que qualquer aÃ§Ã£o seja tomada. Ã‰ uma barreira de seguranÃ§a cognitiva que elimina execuÃ§Ãµes surpresa.

### PedÃ¡gio de Planejamento (`lifecycle.py`)

O **PedÃ¡gio de Planejamento** Ã© implementado no `backend/core/lifecycle.py` como uma verificaÃ§Ã£o mecÃ¢nica no ciclo de vida do agente. Funciona assim:

1. **Passos 1 e 2** do ciclo de vida sÃ£o bloqueados para execuÃ§Ã£o de ferramentas
2. O agente Ã© **mecanicamente obrigado** a apresentar:
   - Seu raciocÃ­nio em texto claro
   - Uma lista de checkboxes no formato Markdown (`- [ ] Meta 1`, `- [ ] Meta 2`)
   - Um JSON `task_plan` com o campo `steps`
3. O lifecycle valida a presenÃ§a de **pelo menos 2 checkboxes** e do **JSON task_plan** antes de liberar as ferramentas
4. Se o agente tentar pular esta etapa, recebe um **nudge de correÃ§Ã£o** e Ã© forÃ§ado a voltar ao planejamento

### Formato Exigido pelo Agente

```markdown
## AnÃ¡lise do Problema
Vou analisar o cÃ³digo existente e criar a estrutura necessÃ¡ria...

## Plano de AÃ§Ã£o
- [ ] Analisar cÃ³digo existente
- [ ] Criar estrutura necessÃ¡ria
- [ ] Implementar funcionalidade
- [ ] Validar resultado

{"type":"task_plan","steps":["Analisar cÃ³digo existente","Criar estrutura necessÃ¡ria","Implementar funcionalidade","Validar resultado"]}
```

### ConfiguraÃ§Ã£o do PedÃ¡gio

```python
LifecycleConfig(
    planning_enforced=True,    # Ativar/desativar o pedÃ¡gio
    planning_check_steps=2,    # Verificar nos primeiros N passos
)
```

### Fluxo MecÃ¢nico

```
Agente recebe tarefa
  â†“
Passo 1: Agente apresenta raciocÃ­nio + checkboxes + task_plan
  â†“
ValidaÃ§Ã£o: _has_checkboxes() + _has_task_plan_json()
  â†“
âœ… Passou â†’ has_presented_plan = True â†’ liberar ferramentas
âŒ Falhou â†’ Nudge de correÃ§Ã£o â†’ forÃ§ar re-planejamento
  â†“
Passo 2+: ExecuÃ§Ã£o livre das ferramentas
```

â†’ [PrÃ³ximo: Calibragem de Temperatura](#15-calibragem-de-temperatura) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 15. Calibragem de Temperatura

O **DEEP-AUREA** recomenda uma calibragem de temperatura padrÃ£o de **0.10** para comportamento estrito e determinÃ­stico.

### Por que 0.10?

| Temperatura | Comportamento | Uso Recomendado |
|-------------|---------------|-----------------|
| 0.0 | Totalmente determinÃ­stico | ReproduÃ§Ã£o exata de testes |
| **0.10** | **Quase determinÃ­stico (recomendado)** | **Uso geral do DEEP-AUREA** |
| 0.3 | Levemente criativo | Brainstorming leve |
| 0.7 | Criativo | GeraÃ§Ã£o de conteÃºdo criativo |
| 1.0 | MÃ¡xima criatividade | Explore radical |

A temperatura **0.10** Ã© o sweet spot para o DEEP-AUREA porque:

- **Elimina alucinaÃ§Ãµes** causadas por sampling excessivo
- **Garante consistÃªncia** nas respostas do agente
- **MantÃ©m o Checklist Visual** Ã­ntegro (sem variaÃ§Ãµes de formato)
- **Preserva a mÃ¡quina de estados** â€” o agente segue o protocolo de forma previsÃ­vel

### Como Configurar

No arquivo `backend/core/config.py` ou via interface:

```python
# ConfiguraÃ§Ã£o padrÃ£o recomendada
DEFAULT_TEMPERATURE = 0.10
```

â†’ [PrÃ³ximo: Comandos](#16-comandos-Ãºteis) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 16. Comandos Ãšteis

```bash
# Iniciar tudo
.\START-TOTAL.bat

# Parar tudo
.\STOP-TOTAL.bat

# Backend isolado (porta 8001)
cd backend && venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8001

# Frontend isolado (porta 5175)
cd frontend && npm run dev

# Testes
pytest backend/tests
cd frontend && npx vitest run
```

â†’ [PrÃ³ximo: VariÃ¡veis](#17-variÃ¡veis-de-ambiente) | [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## 15. VariÃ¡veis de Ambiente

Copie `backend/.env.example` para `backend/.env` e configure:

| VariÃ¡vel | ObrigatÃ³ria | DescriÃ§Ã£o |
|----------|-------------|-----------|
| `GROQ_API_KEY` | Para Groq | Chave da API Groq |
| `OPENAI_API_KEY` | Para OpenAI | Chave da API OpenAI |
| `GEMINI_API_KEY` | Para Gemini | Chave da API Gemini |
| `OPENROUTER_API_KEY` | Para OpenRouter | Chave da API OpenRouter |
| `OPENCLAUDE_API_KEY` | Para OpenClaude | Chave da API OpenClaude |
| `OPENCODE_API_KEY` | Para OpenCode | Chave da API OpenCode |
| `MIMO_API_KEY` | Para MiMo | Chave da API Xiaomi MiMo |

â†’ [Voltar ao Ã­ndice](#sumÃ¡rio)

---

## Documentos Separados

| Documento | Descricao |
|-----------|-----------|
| [Instrucoes de Uso](instrucoes.md) | Comandos `/`, mencoes `@`, confirmacoes de risco, checklist, action cards |
| [Guia SQL](sql_guia_completo.md) | Referencia completa de SQL (DML, DDL, JOINs, procedures, etc.) |
| [WBC-Diag](../0-Projetos/WBC-Diag/README.md) | Sistema de diagnostico de hardware |
| [project-loader](../project-loader/README.md) | CLI para gerenciar projetos |

---

> **DEEP-AUREA** â€” Manual consolidado | VersÃ£o 5.2.2 | Copyright Â© WBC 2026
