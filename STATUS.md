# DEEP-OS — Status do Projeto

**Ultima atualizacao:** 2026-09-05 (Sessao 30) — Deploy VPS + Docker + Dominio

---

## Sessao 2026-09-05 (30) — Deploy VPS Hostinger + Docker + Dominio

### Resumo

Deploy completo do DEEP-OS em VPS Hostinger (Ubuntu 26.04, Python 3.14). Dominio `deep-os.tech` apontando para `2.25.143.185`. Corrigidos multiples bugs de deploy: CORS, proxy, encoding, import condicionais para headless. Criado sistema Docker para deploy automatico.

### 1. Identidade Sync (CORRECAO)

**Problema:** `PUT /api/config/identity` nao sincronizava com `config.yaml` nem `api_keys.json`.

**Solucao:** `save_assistant_config()` atualiza root `config.yaml`, `backend/config.yaml`, e `api_keys.json`.

**Arquivos:** `backend/routes/config.py` (linha 142-153), `backend/memory/config_manager.py`

### 2. Charon Greeting Fix (CORRECAO)

**Problema:** Charon enviava briefing como mensagem de usuario — Gemini respondia ao briefing como input do usuario.

**Solucao:** Greeting agora usa `send_client_content` com trigger curto ("Se apresente para X agora"). System instruction reforcada com "Fale EXCLUSIVAMENTE em portugues brasileiro".

**Arquivo:** `backend/routes/voice_ws.py` (linha 1263-1282)

### 3. Italian Transcription Fix (CORRECAO)

**Problema:** Gemini Live transcrevia em italiano em vez de portugues.

**Solucao:** Adicionado `language_code="pt-BR"` ao `LiveConnectConfig`.

**Arquivo:** `backend/routes/voice_ws.py` (linha 859-874)

### 4. Second Message Hang Fix (CORRECAO)

**Problema:** Segunda mensagem de texto travava.

**Solucao:** `session._turn_done_event.clear()` e `session._interrupted = False` antes de `send_client_content`.

**Arquivo:** `backend/routes/voice_ws.py` (linha 1614-1629)

### 5. Activity Panel Formatting (MELHORIA)

**Problema:** Resultados `web_search` apareciam como texto monospace cru.

**Solucao:** Cards organizados com titulo, snippet, e URL da fonte.

**Arquivo:** `frontend/src/components/saas/CharonPage.tsx`

### 6. pyautogui Import Fix (CORRECAO CRITICA VPS)

**Problema:** `import pyautogui` causava `KeyError: 'DISPLAY'` em VPS headless (sem tela).

**Solucao:** `except (ImportError, Exception)` em 5 arquivos de actions.

**Arquivos:** `youtube_video.py`, `computer_control.py`, `computer_settings.py`, `desktop.py`, `send_message.py`

### 7. sounddevice Import Fix (CORRECAO CRITICA VPS)

**Problema:** `import sounddevice` causava `PortAudioError` em VPS sem PulseAudio.

**Solucao:** Import condicional com flag `_SD`.

**Arquivo:** `backend/actions/screen_processor.py` (linha 14-18)

### 8. ws_terminal.py Encoding Fix (CORRECAO CRITICA VPS)

**Problema:** `SyntaxError: Non-UTF-8 code` em Python 3.14.

**Solucao:** Adicionado `# -*- coding: utf-8 -*-` e corrigidos caracteres corrompidos.

**Arquivo:** `backend/routes/ws_terminal.py`

### 9. CORS + Vite Host + Proxy (CORRECAO CRITICA)

**Problema:** Frontend nao encontrava backend ("FAILED TO FETCH"). CORS so aceitava localhost.

**Solucao:**
- CORS: Adicionados `http://2.25.143.185:5176`, `http://deep-os.tech`, `https://deep-os.tech`
- Vite: `host` mudado de `localhost` para `0.0.0.0`
- Proxy: Adicionadas rotas `/chat`, `/voice` (WebSocket), `/admin`

**Arquivos:** `backend/main.py` (linha 42-55), `frontend/vite.config.ts`

### 10. Git History Cleanup (CORRECAO)

**Problema:** Push falhava — arquivo `.rar` de 554MB no historico.

**Solucao:** `git filter-branch` removeu `.rar` do historico. Adicionado `*.rar`, `*.zip`, `*.7z` ao `.gitignore`.

### 11. Docker Deploy (NOVO)

**Problema:** Deploy manual no VPS era demorado e propenso a erros.

**Solucao:** Docker Compose + nginx proxy. Deploy com 1 comando.

**Arquivos criados:**
- `docker-compose.prod.yml` — Backend + Frontend containers
- `backend/Dockerfile` — Python 3.11 + uvicorn
- `frontend/Dockerfile.prod` — Node build + nginx
- `frontend/nginx.conf` — Proxy reverso (API, WebSocket)
- `nginx/vps-nginx.conf` — Config nginx para VPS
- `deploy.sh` — Script de deploy
- `.github/workflows/deploy.yml` — Deploy automatico via GitHub Actions

### 12. requirements.txt Fix

**Problema:** `opencv-python` causava conflito com `opencv-python-headless` no VPS.

**Solucao:** Trocado para `opencv-python-headless` no requirements.txt.

---

## Estado Atual do Deploy

### VPS Hostinger
- **IP:** 2.25.143.185
- **Dominio:** deep-os.tech
- **OS:** Ubuntu 26.04.1 LTS (Python 3.14)
- **User:** root

### Servicos (Manual — antes do Docker)
| Servico | Porta | Status |
|---------|-------|--------|
| Backend (uvicorn) | 8001 | Rodando |
| Frontend (Vite) | 5176 | Rodando |
| ChatBot (Node) | 8010 | Rodando |
| Nginx | 80 | **PENDENTE** — precisa instalar |

### Docker (Apos build completo)
| Container | Porta | Status |
|-----------|-------|--------|
| backend | 8001 | Building... |
| frontend | 5176 | Building... |

### Para acessar
- **http://2.25.143.185:5176** — Frontend via Vite
- **http://2.25.143.185:8001** — Backend direto
- **https://deep-os.tech** — Via nginx (precisa configurar)

### Para finalizar deploy Docker
```bash
cd /root/DEEP-OS
# Esperar build do Docker terminar
docker compose -f docker-compose.prod.yml up -d

# Instalar nginx para o dominio
apt install nginx -y
cp /root/DEEP-OS/nginx/vps-nginx.conf /etc/nginx/nginx.conf
systemctl restart nginx
```

---

## Git Commits (Sessao 30)

| Hash | Descricao |
|------|-----------|
| 80dc3bb | feat: Docker deploy automatico + GitHub Actions + nginx proxy |
| 9afdf85 | remove .rar 554MB do tracking + gitignore rars/zips |
| 91fb589 | fix: CORS + Vite host 0.0.0.0 + proxy chat/voice/admin |
| b7b45f0 | fix: encoding utf-8 em ws_terminal.py (Python 3.14) |
| ea57803 | fix: sounddevice import condicional (VPS headless sem PulseAudio) |
| 046a9ce | fix: pyautogui import fallback (VPS headless sem DISPLAY) |
| 66e6c16 | fix: identity sync + greeting + voice save + activity formatting |

---

## Arquivos Importantes

| Arquivo | Descricao |
|---------|-----------|
| `config.yaml` | Config raiz (identity, charon_toolset, agent_models) |
| `backend/config.yaml` | Config backend (sincronizado) |
| `backend/config/api_keys.json` | API keys + identity |
| `backend/main.py` | FastAPI + CORS + rotas |
| `backend/routes/voice_ws.py` | Gemini Live WebSocket (Charon) |
| `backend/routes/config.py` | Endpoints de config (identity) |
| `backend/memory/config_manager.py` | Leitura/salvamento de config |
| `frontend/src/components/saas/CharonPage.tsx` | Interface do Charon |
| `frontend/vite.config.ts` | Proxy + host config |
| `docker-compose.prod.yml` | Docker para producao |
| `deploy.sh` | Script de deploy |

---

## Como Atualizar (Apos Docker)

**Manual:**
```bash
cd /root/DEEP-OS && bash deploy.sh
```

**Automatico (GitHub Actions):**
Adicionar secrets no GitHub:
- `VPS_HOST` = `2.25.143.185`
- `VPS_SSH_KEY` = chave SSH privada

---

## Sessoes Anteriores (Resumo)

| Sessao | Data | Descricao |
|--------|------|-----------|
| 29 | 2026-09-04 | Portacao Mark-LI + Filtro Contexto + Audio Fix |
| 28 | 2026-09-04 | Portacao Mark-LI completa |
| 27 | 2026-08-27 | Correcao Frontend (6 arquivos) |
| 26 | 2026-08-27 | Correcao Audio Charon (MIME, voice, greeting) |
| 25 | 2026-08-27 | Correcao Critica Charon (tools duplicadas, cache) |
| 23 | 2026-08-27 | Dropdown Customizado + Agent Models |
| 22 | 2026-08-27 | Identity + Voice Selector + Layout Redesign |
| 21 | 2026-08-26 | ElevenLabs + Memory + Knowledge |
| 20 | 2026-08-26 | MCP + Architect + Debugger |

---

## Pendencias

### Deploy (IMEDIATO)
- [ ] Instalar nginx no VPS (`apt install nginx -y`)
- [ ] Configurar nginx com `nginx/vps-nginx.conf`
- [ ] Verificar se Docker build terminou
- [ ] Testar `https://deep-os.tech`

### Deploy Automatico
- [ ] Configurar GitHub Actions (secrets VPS_HOST + VPS_SSH_KEY)
- [ ] Testar deploy via push

### VPS
- [ ] Criar script `start-saas.sh` para Linux
- [ ] Configurar systemd services (backend + frontend + chatbot)
- [ ] SSL/HTTPS com Let's Encrypt

### Funcionalidades
- [ ] ElevenLabs — Configurar `ELEVENLABS_API_KEY`
- [ ] web_fetch — User-Agent upgrade (403 Cloudflare)
- [ ] Wake word — Reduzir falsos positivos
- [ ] llamacpp — Aumentar `--ctx-size`
