# DEEP-AUREA — Status do Projeto

**Última atualização:** 2026-07-16

---

## Estado Atual: FUNCIONAL

O sistema está operacional em `localhost:5175` (frontend) / `localhost:8001` (backend).

---

## Histórico de Correções (Sessão 2026-07-16)

### 1. Sincronização com opencode (C:\MiMo-Code)
- Copiados 27 agentes e 38 skills (135 arquivos) — idênticos ao opencode
- Criado `CLAUDE.md`
- Atualizado `.editorconfig`, `.prettierrc`, `package.json` para corresponder ao opencode

### 2. Configuração do system_prompt
- `config.yaml` — system_prompt expandido com instruções explícitas para usar `web_search`/`web_fetch`
- Backend (`chat.py:471`) — fallback `_load_config_system_prompt()` garante que o prompt sempre seja carregado
- Frontend (`App.tsx:256`) — busca system_prompt do backend no startup

### 3. Lista de modelos sem tool calling
- `chat.py:307` — removido `deepseek-v4-flash` do `CLOUD_NO_TOOL_MODELS`

### 4. Correção do web_search (BUG CRÍTICO)
- **Problema:** A lib `duckduckgo_search` usa GET para DuckDuckGo, que retorna HTTP 202 (vazio)
- **Resultado:** `web_search` retornava 0 resultados → modelo inventava dados
- **Correção:** `backend/tools/web_search.py` reescrito para usar **POST** para `html.duckduckgo.com/html/`
- **Verificado:** 10 resultados reais retornados com POST

### 5. Debug logging adicionado
- `llm_native.py` — logs detalhados em `stream_chat_with_tools`: provider, model, tools, msg_roles, system_prompt preview

---

## Arquivos Modificados (esta sessão)

| Arquivo | Mudança |
|---|---|
| `config.yaml` | System_prompt expandido, limpeza |
| `CLAUDE.md` | Criado (referencia AGENTS.md) |
| `.editorconfig` | LF, 2-space indent, 80 chars |
| `.prettierrc` | `semi: false`, `printWidth: 120` |
| `package.json` | Scripts: typecheck, clean, docker:up/down/build |
| `backend/config.yaml` | Comentário descritivo |
| `backend/routes/chat.py` | Fallback system_prompt, debug logging |
| `backend/tools/web_search.py` | **Reescrito** — POST para html.duckduckgo.com |
| `backend/core/llm_native.py` | Debug logging em stream_chat_with_tools |
| `frontend/src/App.tsx` | Fetch system_prompt do backend no startup |

---

## Pendências

- **criar ebook sobre terremoto Venezuela 2026** — dados reais disponíveis via web_search, modelo pode gerar
- **web_fetch** — funciona mas não foi extensivamente testado com todos os sites
- **Instalar `ddgs`** — pacote novo do DuckDuckGo (opcional, POST direto funciona sem dependência extra)

---

## Como Iniciar

```bat
C:\DEEP-AUREA\START-TOTAL.bat
```

- Backend: http://localhost:8001
- Frontend: http://localhost:5175
