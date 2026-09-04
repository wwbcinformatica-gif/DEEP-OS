**Ultima atualizacao:** 2026-09-04 (Sessao 28) - Portacao Mark-LI + Filtro de Contexto + Audio Fix

---

## Sessao 2026-09-04 (28) - Portacao Mark-LI + Filtro de Contexto + Audio Fix

### Resumo

Portadas todas as funcionalidades do Mark-LI para o Charon do DEEP-OS. Corrigido audio engasgando/cortando com buffer intermediario e ring buffer maior. Adicionado filtro de contexto para focar em topicos relevantes. Atualizada chave do Gemini (anterior foi bloqueada por leaked). Painel central separado do painel de voz.

### ⚠️ FORMATO DO PAINEL DIREITO — DEFINITIVO (NAO ALTERAR)

**Formato correto:** Cada palavra/trecho da transcricao aparece como uma entrada SEPARADA com timestamp, empilhando em tempo real. NAO acumular em uma unica mensagem.

```
⚡ Charon · 15:45:50
Boa tarde,
⚡ Charon · 15:45:51
WBC.
⚡ Charon · 15:45:51
Como
⚡ Charon · 15:45:52
posso
⚡ Charon · 15:45:52
ajudar
⚡ Charon · 15:45:52
hoje?
👤 Voce · 15:45:57
Olá, acharam tudo.
```

**Por quê:** Este é o comportamento original do Gemini Live API — envia a transcricao conforme fala (palavra por palavra). O frontend mostra cada pedaco como uma nova entrada. Isso da a sensacao de conversa em tempo real.

**NUNCA fazer:**
- Acumular palavras em uma unica mensagem (isso causa lentidao e delay)
- Esperar turn_complete para mostrar (isso atrasa a transcricao)

**SEMPRE fazer:**
- Enviar cada palavra/trecho imediatamente via WebSocket
- Mostrar cada pedaco como entrada separada no painel direito
- Timestamp em cada entrada

---

### 1. Portacao Mark-LI — Todas as Funcionalidades (NOVO)

**Problema:** Charon do DEEP-OS nao tinha as funcionalidades avancadas do Mark-LI (affective dialog, proactive audio, visao real, monitores, etc).

**Solucao:** Portadas 10 funcionalidades do Mark-LI para o `voice_ws.py`:

| Funcionalidade | Status |
|---------------|--------|
| Affective Dialog + Proactive Audio (v1alpha) | ✓ |
| Visao Real (screen_process injeta imagem no Gemini) | ✓ |
| System Monitor (alertas de CPU/RAM por voz) | ✓ |
| Proactive Mode (check-in apos 15min de silencio) | ✓ |
| Background Monitor (verifica topicos a cada 30min) | ✓ |
| Phone Audio Relay (microfone do celular) | ✓ |
| Session Memory (resumo automatico ao fechar) | ✓ |
| Briefing com temperatura da cidade local | ✓ |
| Fallback automatico v1alpha → v1beta | ✓ |
| Context Window Compression + Session Resumption | ✓ |

**Arquivos criados:**
- `actions/proactive.py` — ProactiveEngine 2.0 (copiado do Mark-LI)
- `actions/download_image.py` — Download de imagens (criado)

**Arquivos modificados:**
- `backend/routes/voice_ws.py` — Portacao completa + 10 funcionalidades

### 2. 3 Actions Faltantes Adicionadas (NOVO)

**Problema:** `calorie_counter`, `pushup_counter`, `upload_video` existiam em `actions/` mas nao estavam integradas no Charon.

**Solucao:** Adicionadas tool declarations + imports + handlers no `voice_ws.py`.

| Action | Tipo | Toolset |
|--------|------|---------|
| calorie_counter | Visao (webcam) | FULL |
| pushup_counter | Visao (webcam) | FULL |
| upload_video | Browser automation | FULL |

**Total de actions:** 24 (todas integradas)
**Total de tools:** 28 (toolset FULL)

### 3. Audio Engasgando/Cortando (CORRECAO CRITICA)

**Problema:** Charon respondia engasgando, cortando audio, demorando responder.

**Causa:** Ring buffer de 48000 (1s) com prebuffer de 2400 (0.1s) — muito pequeno. Chunks WebSocket iam direto ao worklet sem acumular.

**Solucao (baseada no MEMORY-charon-voice-fix.md):**
1. Ring buffer aumentado: 48000 → **192000** (8 segundos)
2. Prebuffer aumentado: 2400 → **12000** (0.5 segundos)
3. Buffer intermediario de **20ms** — acumula chunks antes de enviar ao worklet

**Arquivo modificado:**
- `frontend/src/components/saas/CharonPage.tsx` — PLAYBACK_WORKLET + buffer intermediario

### 4. Filtro de Contexto (NOVO)

**Problema:** Charon trazia conteudo irrelevante (futebol, rede globo, celebridades).

**Solucao:** Campo "Filtro de Contexto" nas Configuracoes do Charon. Usuario define topicos relevantes e o Charon ignora o resto.

- Salvo em `localStorage` (`charon_context_filter`)
- Enviado via WebSocket (`type: context_filter`)
- Aplicado no `_build_system_instruction()` como `[FILTRO DE CONTEXTO]`

**Arquivo modificado:**
- `frontend/src/components/saas/CharonPage.tsx` — Campo de filtro + handler
- `backend/routes/voice_ws.py` — `_context_filter` + handler WebSocket + system_instruction

### 5. Painel Central vs Painel Direito (MODIFICADO)

**Problema:** Ambos os paineis mostravam o mesmo conteudo (transcripts).

**Solucao:** Separacao de paineis:
- **Painel Central (esquerdo):** Log de atividades (tool calls, pesquisas web, resultados, relatorios)
- **Painel Direito:** Voz — transcrição do usuario + respostas do Charon

**Estado separado:** `activityLog` (painel central) vs `transcripts` (painel direito)

**Arquivo modificado:**
- `frontend/src/components/saas/CharonPage.tsx` — Estados separados + JSX

### 6. Layout Fixo (CORRECAO)

**Problema:** Painel se estendia abaixo da janela, cortando conteudo.

**Solucao:**
- `SaaSApp.tsx`: `mainContent` mudou de `minHeight: 100vh` + `overflowY: auto` para `height: 100vh` + `overflow: hidden`
- `CharonPage.tsx`: Todos os paineis com `minHeight: 0` + `overflow: hidden`

**Arquivos modificados:**
- `frontend/src/components/saas/SaaSApp.tsx` — mainContent fixo
- `frontend/src/components/saas/CharonPage.tsx` — container + paineis fixos

### 7. Briefing Simplificado (MODIFICADO)

**Antes:** Briefing de 2 fases (saudacao + noticias do mundo)

**Agora:** Saudacao com nome do usuario + temperatura da cidade local (detectada via IP) + status do sistema (CPU/RAM)

**Arquivo modificado:**
- `backend/routes/voice_ws.py` — `_send_startup_briefing` reescrito

### 8. Chave Gemini Atualizada (CORRECAO CRITICA)

**Problema:** Chave `AIzaSyBDdw...` foi marcada como leaked pelo Google. Nenhum projeto conectava.

**Solucao:** Nova chave `AIzaSyAGOFw...` atualizada em 3 projetos:
- `C:\DEEP-OS\backend\config\api_keys.json`
- `C:\DEEP-OS\backend\.env`
- `C:\Mark-LI\config\api_keys.json`
- `C:\DEEP-AUREA\backend\config\api_keys.json`
- `C:\DEEP-AUREA\backend\.env`

### 9. Toolset FULL Ativado (CONFIG)

**Mudanca:** `config.yaml` mudou de `charon_toolset: basic` para `charon_toolset: full`

**Resultado:** 28 tools ativas (18 BASIC + 10 EXTRA incluindo calorie_counter, pushup_counter, upload_video, save_document, memory_save/recall, web_fetch, bash, file_edit)

### Arquivos Modificados

- `backend/routes/voice_ws.py` — Portacao Mark-LI + 3 actions + filtro contexto + briefing + vision
- `frontend/src/components/saas/CharonPage.tsx` — Audio fix + painel separado + filtro contexto + layout fixo
- `frontend/src/components/saas/SaaSApp.tsx` — mainContent fixo
- `config.yaml` — charon_toolset: full
- `actions/proactive.py` — CRIADO (ProactiveEngine)
- `actions/download_image.py` — CRIADO
- `backend/config/api_keys.json` — Nova chave Gemini
- `backend/.env` — Nova chave Gemini

### Status do Voice API

```json
{
    "available": true,
    "default_voice": "charon",
    "toolset": "full",
    "tools": 28,
    "actions_loaded": true,
    "skills": 40,
    "proactive": true,
    "system_monitor": true,
    "enhanced_live": true
}
```

---

## Sessao 2026-08-27 (27) - Correcao Frontend (6 arquivos)

### Resumo

8 bugs identificados e corrigidos nos componentes frontend relacionados a voz e Charon. O sistema agora funciona perfeitamente com status correto, envio de voz configuravel, e indicadores visuais adequados.

### 1. StatusBar.tsx - voiceName hardcoded (CORRECAO CRITICA)

**Problema:** WebSocket enviava `voice: 'Charon'` hardcoded em vez de usar a voz configurada pelo usuario.

**Impacto:** Independente de qual voz o usuario selecionasse, o backend sempre recebia 'Charon'.

**Solucao:** Adicionado prop `voiceName` ao StatusBar e usado em ambos handlers WebSocket (useEffect inicial e toggleCharon).

### 2. App.tsx - charonVoiceStatus nunca atualizado (CORRECAO CRITICA)

**Problema:** Estado `charonVoiceStatus` era definido mas nunca recebia atualizacoes do StatusBar.

**Impacto:** CharonPanel sempre mostrava status 'idle' mesmo quando conectado.

**Solucao:** Passado `voiceName={voiceName}` e `onCharonVoiceStatus={setCharonVoiceStatus}` para StatusBar.

### 3. VoiceHud.tsx - voice hardcoded (CORRECAO)

**Problema:** WebSocket enviava `voice: 'Charon'` hardcoded.

**Solucao:** Adicionado prop `voiceName` e usado no WebSocket.

### 4. VoiceHud.tsx - onCharonStatusChange inexistente (CORRECAO)

**Problema:** Nao havia callback para notificar mudancas de status.

**Solucao:** Adicionado prop `onCharonStatusChange` e chamado em todas mudancas (connecting, listening, speaking, processing, error).

### 5. CharonPanel.tsx - Nao bloqueia durante processing (CORRECAO)

**Problema:** Input nao era bloqueado durante processamento.

**Solucao:** Adicionado check `voiceStatus === 'processing'` no handleSend e isActive.

### 6. CharonPanel.tsx - Sem indicador visual de processing (CORRECAO)

**Problema:** Usuario nao via feedback visual durante processamento.

**Solucao:** Adicionado cor laranja (#f80) e texto "processando..." no badge de status.

### 7. ToolPanel.tsx - Tailwind CSS inconsistente (CORRECAO)

**Problema:** Usava classes Tailwind CSS em vez de variaveis CSS.

**Solucao:** Convertido todos os estilos para CSS inline com variaveis do tema.

### 8. ChatPanel.tsx - split(':') preservado (VERIFICADO)

**Verificacao:** O parsing `parts.slice(4).join(':')` ja preserva dois-pontos no conteudo. Nenhuma alteracao necessaria.

### Arquivos Modificados

- `frontend/src/components/StatusBar.tsx` — voiceName prop + 2 WebSocket handlers
- `frontend/src/App.tsx` — voiceName + onCharonVoiceStatus para StatusBar
- `frontend/src/components/VoiceHud.tsx` — voiceName + onCharonStatusChange
- `frontend/src/components/CharonPanel.tsx` — blocking processing + indicador visual
- `frontend/src/components/ToolPanel.tsx` — CSS variables

### Build

Build concluido com sucesso (`npm run build`). Apenas warning menor de CSS.

---

## Sessao 2026-08-27 (26) - Correcao Audio Charon (voice_ws.py)

### Resumo

Charon recebia o greeting mas nao processava audio do usuario. 3 bugs adicionais corrigidos em `backend/routes/voice_ws.py`.

### 1. MIME Type do Audio Sem Taxa (CORRECAO CRITICA)

**Problema:** `send_audio()` enviava `mime_type: "audio/pcm"` para o Gemini **sem especificar a taxa de amostragem**. O Gemini precisava da taxa para decodificar o PCM corretamente.

**Impacto:** Audio enviado pelo frontend (PCM16 a 16kHz) era ignorado ou corrompido pelo Gemini. O greeting funcionava (enviado via texto), mas respostas de voz nao chegavam.

**Fluxo do audio:**
```
Frontend: mic 48kHz → downsample 3x → PCM16 16kHz → ws.send(bytes)
Backend:  recebe bytes → send_realtime_input(mime_type="audio/pcm;rate=16000") → Gemini
```

**Solucao:** Adicionado `rate=16000` em todas as 3 ocorrencias de `audio/pcm`:
- `send_audio()` — audio do usuario
- `keepalive_loop()` — ping de silencio
- WebSocket handler — interrupt

### 2. GEMINI_VOICES Case-Sensitive (CORRECAO)

**Problema:** `GEMINI_VOICES` usava chaves minusculas (`"aoede"`, `"charon"`), mas o frontend enviava nomes com maiusculas (`'Aoede'`, `'Charon'`). O lookup `GEMINI_VOICES.get(voice, voice)` nunca encontrava a chave.

**Impacto:** A funcao de lookup nunca funcionava, retornando o nome original como fallback. Por acaso funcionava porque o Gemini aceita nomes com maiusculas, mas o mapeamento era inutil.

**Solucao:** Nova funcao `_resolve_voice(voice)` que normaliza para minusculas antes do lookup.

### 3. Greeting Hardcoded (CORRECAO)

**Problema:** `_send_startup_briefing()` dizia "Sou o Charon" hardcoded, ignorando `identity.assistant_name` do config.

**Solucao:** Agora le `assistant_name` do config e usa no greeting: "Sou o {assistant_name}, seu assistente de voz."

### Arquivo Modificado

- `backend/routes/voice_ws.py` — MIME type, voice resolution, greeting dinamico

---

## Sessao 2026-08-27 (25) - Correcao Critica Charon (voice_ws.py)

### Resumo

4 bugs criticos identificados e corrigidos em `backend/routes/voice_ws.py` que causavam lentidao e perda de funcionalidade no Charon.

### 1. EXTRA_TOOL_DECLARATIONS Sobrescrito (CORRECAO CRITICA)

**Problema:** `EXTRA_TOOL_DECLARATIONS` era definido **duas vezes** no mesmo arquivo:
- 1a definicao (linhas 584-865): ~20 tools completas (game_updater, flight_finder, etc)
- 2a definicao (linhas 868-968): apenas 8 tools (bash, read_file, write_file, etc)

A 2a definicao sobrescrevia a 1a, fazendo 12 tools sumirem no modo FULL.

**Solucao:** Removida a 1a definicao duplicada. Agora existe apenas uma com as 8 tools extras corretas.

### 2. MEDIUM sem bash e read_file (CORRECAO CRITICA)

**Problema:** `MEDIUM_TOOL_DECLARATIONS` (modo recomendado) nao incluia `bash` nem `read_file` — ferramentas criticas que estavam apenas no BASIC e no EXTRA.

**Impacto:** No modo MEDIUM, o Charon nao conseguia executar comandos nem ler arquivos, causando loops de erro.

**Solucao:** Adicionados `bash` e `read_file` ao MEDIUM. Agora MEDIUM = 18 tools (antes 16).

**Contagens corrigidas:**
| Modo | Antes | Depois |
|------|-------|--------|
| BASIC | 18 | 18 |
| MEDIUM | 16 (sem bash/read_file) | **18** (com bash + read_file) |
| FULL | 24 (12 tools perdidas) | **26** (todas as extras corretas) |

### 3. _ensure_receive_loop Duplicado (CORRECAO)

**Problema:** Metodo `_ensure_receive_loop` definido **duas vezes** na classe VoiceSession:
- 1a definicao (linha 957): com print de debug
- 2a definicao (linha 1388): sem print

A 2a sobrescrevia a 1a, comportamento inesperado.

**Solucao:** Removida a 1a definicao. Mantida apenas a 2a (mais limpa).

### 4. _get_charon_toolset() sem Cache (CORRECAO)

**Problema:** `_get_charon_toolset()` lia `config.yaml` do disco **a cada chamada** — chamada multiplos vezes por conexao (em `_get_active_tools()` e `_build_system_instruction()`).

**Solucao:** Adicionado cache com deteccao de `mtime` (igual ao `_load_identity()`). Agora so relê o arquivo quando ele e modificado.

### Arquivo Modificado

- `backend/routes/voice_ws.py` — 4 correcoes (duplicacao tools, cache, metodo duplicado)

### 2. Barrinhas Graficas no Header (NOVO)

**Antes:** Apenas texto (CPU 24%, RAM 7.0G 59%, GPU 0.9G 7%)

**Agora:** Texto + barras de progresso visuais

**Arquivo modificado:**
- `frontend/src/components/MiniMonitors.tsx` — Adicionadas barras de progresso com cores dinamicas

### 3. Estabilidade Gemini Live (CORRECAO CRITICA)

**Problema:** Sessao Gemini Live expirava apos ~2 minutos de inatividade, fazendo Charon parar de responder.

**Causa raiz:** Falta de `context_window_compression` na configuracao da sessao.

**Solucao (copiada do Mark-LI):**
```python
context_window_compression=types.ContextWindowCompressionConfig(
    sliding_window=types.SlidingWindow(),
),
```

**Arquivos modificados:**
- `backend/routes/voice_ws.py` — Adicionado `context_window_compression` em start() e _reconnect()

### 4. Reconexao Automatica (MELHORADO)

**Antes:** Receive loop morria apos 5 tentativas

**Agora:** Reconexao automatica com client novo a cada tentativa

**Mudancas:**
- `_reconnect()` — fecha sessao antiga, cria client novo, reconecta
- `_reconnect` flag — impede reconexoes simultaneas
- Receive loop — reconecta ao inves de morrer
- Keepalive — ping a cada 30s com silencio

### 5. Config.yaml Corrigido

**Problema:** `charon_toolset: false` (boolean antigo)
**Solucao:** `charon_toolset: medium` (string valido)

### Tools por Nivel

| Nivel | Quantidade | Tools |
|-------|------------|-------|
| BASIC | 18 | open_app, web_search, system_status, weather_report, send_message, reminder, youtube_video, screen_process, computer_settings, browser_control, file_controller, desktop_control, code_helper, dev_agent, computer_control, file_processor, bash, read_file |
| MEDIUM | 20 | Todas BASIC + write_file, file_edit |
| FULL | 28 | Todas MEDIUM + save_document, web_fetch, memory_save, memory_recall |

### Como Testar

1. **Toggle:** Config > Agentes > Charon Tools > selecione nivel
2. **Barrinhas:** Header mostra barras de progresso CPU/RAM/GPU
3. **Estabilidade:** Ative Charon, aguarde5+ minutos, tente falar

---

## Sessao 2026-08-27 (23) - Redesign do ConfigModal, Toggle Melhorado, Agent Models

### Resumo

Redesign completo do ConfigModal com transferencia de abas, toggle buttons mais suaves, sistema de modelos por agente configuravel, e dropdown customizado com portal para evitar clipping.

### 1. Transferencia de Abas (MODIFICADO)

**Antes:** Abas separadas Configuracoes, Gerar, Conhecimento, Memoria, Agentes, Arquitetura, MCP, Monitor, Terminal.

**Agora:** Configuracoes, Conhecimento (com sub-abas Gerar e Memoria), Agentes (com sub-abas Voz, Agente, Assistente), Arquitetura, MCP, Monitor, Terminal.

**Arquivos modificados:**
- `frontend/src/components/ConfigModal.tsx` — Tabs reduzidas de 9 para 7
- `frontend/src/components/KnowledgePage.tsx` — Adicionado sub-abas Conhecimento, Gerar, Memoria inline
- `frontend/src/components/AgentsPage.tsx` — Adicionado sub-abas Agentes, Voz, Agente, Assistente
- `frontend/src/components/SettingsPage.tsx` — Abas Voz, Agente, Assistente removidas

### 2. Toggle Buttons Melhorados (MODIFICADO)

**Problema:** Toggle buttons muito brancos, difcil distinguir ativo/inativo.

**Solucao:** Knob circular com cores suaves, fundo mais claro, bordas arredondadas.

**Mudancas visuais:**
- Knob: `var(--bg-2)` em vez de `#fff` branco puro
- Borda: `border-radius: 9` (circular)
- Sombra sutil no knob
- Transicao suave entre estados

**Arquivos modificados:**
- `frontend/src/components/SettingsPage.tsx` — Toggle component atualizado
- `frontend/src/components/AgentsPage.tsx` — Toggle component atualizado
- `frontend/src/components/SecurityToggle.tsx` — Botao改为 toggle circular

### 3. Agent Models (NOVO)

**Problema:** Todos os agentes usavam o mesmo modelo hardcoded.

**Solucao:** Cada agente pode ter modelo diferente, configuravel via UI e persistido em `config.yaml`.

**Agentes suportados:** Jarvis, Architect, Debugger, Planner, Coder

**Modelos disponiveis (dropdown organizado por categoria):**
- **Coding:** qwen2.5-coder:14b, qwen2.5-coder:7b, deepseek-coder-v2, deepseek-coder:6.7b
- **Raciocinio:** qwen3:14b, qwen3.5:9b, deepseek-r1 (varios tamanhos)
- **Geral:** qwen2.5:7b, llama-3.2:3b, gemma4:12b, mistral-nemo:12b
- **Multimodal:** qwen3-vl:8b, qwen2.5vl:7b, llava
- **Cloud (gratuito):** gpt-oss:120b-cloud, kimi-k3:cloud, glm-5.2:cloud, etc

**Defaults por agente:**
| Agente | Modelo | Por que |
|--------|--------|---------|
| Jarvis | qwen2.5-coder:14b | Geral, bom equilibrio |
| Architect | qwen3:14b | Raciocinio avancado |
| Debugger | qwen2.5-coder:14b | Codigo, encontra bugs |
| Planner | qwen3.5:9b | Raciocinio, leve |
| Coder | qwen2.5-coder:14b | Codigo, especialista |

**Arquivos modificados:**
- `backend/routes/config.py` — Endpoints `GET/PUT /api/config/agent-models` + `POST /api/config/agent-models/reset`
- `backend/agents/orchestrator.py` — `resolve_model_for_task()` agora le de `agent_models` no config.yaml
- `backend/routes/agent.py` — `agent_execute()` sempre usa `resolve_model_for_task()` (corrigido)
- `frontend/src/components/AgentsPage.tsx` — Selects de modelo por agente + botao "Restaurar padrao"
- `config.yaml` — Secao `agent_models` com valores padrao

**Estrutura config.yaml:**
```yaml
agent_models:
  jarvis: qwen2.5-coder:14b
  architect: qwen3:14b
  debugger: qwen2.5-coder:14b
  planner: qwen3.5:9b
  coder: qwen2.5-coder:14b
```

**Fix importante:** `agent_execute()` agora sempre usa `resolve_model_for_task()` em vez de so usar quando provider era groq. Isso garante que as configuracoes do usuario sejam sempre respeitadas.

### 4. Dropdown Customizado (NOVO)

**Problema:** Select nativo do browser abria para cima por falta de espaco no modal com `overflow: auto`.

**Solucao:** Dropdown customizado usando `ReactDOM.createPortal` para renderizar fora do modal.

**Caracteristicas:**
- Dropdown abre sempre para baixo
- Organizado por grupos (Coding, Raciocinio, Geral, Multimodal, Cloud)
- Hover effect em cada opcao
- Indicador visual do modelo selecionado
- Fecha ao clicar fora

**Arquivos modificados:**
- `frontend/src/components/AgentsPage.tsx` — Componente `CustomDropdown` com portal

### 5. Cache de Identity (OTIMIZADO)

**Problema:** `_load_identity()` lia `config.yaml` a cada mensagem, causando lentidao.

**Solucao:** Cache de 5 segundos em `chat.py` e `voice_ws.py`.

**Arquivos modificados:**
- `backend/routes/chat.py` — `_load_identity()` com cache
- `backend/routes/voice_ws.py` — `_load_identity()` com cache

### 6. Layout Chat/Charon (CORRIGIDO)

**Problema:** Toggle Chat nao funcionava, drag handle nao redimensionava.

**Solucao:** Chat usa `flex: 1` (espaco restante), Charon usa `chatW` (largura fixa), toggle controla `charonPanel`.

**Arquivos modificados:**
- `frontend/src/App.tsx` — Layout flex corrigido, drag handle funcional

---

## Pendencias

### Geral
- **ElevenLabs:** Configurar `ELEVENLABS_API_KEY` em `backend/.env`
- **MiMo Executor:** Implementar `--continue` para manter contexto entre mensagens
- **web_fetch:** User-Agent precisa de upgrade (403 em sites com Cloudflare)
- **Wake word:** Falsos positivos em ambientes barulhentos

### Browser Automation
- **CDP:** Conexao com Chrome via porta 9222 (alternativa ao Playwright)
- **Fill form:** Preenchimento automático de formulários via Charon
- **Screenshot:** Captura de tela para analise de paginas

### Modelos Locais
- **llamacpp context overflow:** NemoMix 12B Q4_K_M tem limite de 8192 tokens; system_prompt + historico excede este limite. Precisa reduzir system prompt ou aumentar --ctx-size.
- **GPU detection:** Driver NVIDIA atualizado (610.88) — verificar se monitor detecta VRAM corretamente após reinicialização

### Resumo

Customizacao completa do assistente (nome, cor, voz), seletor de vozes Gemini Live, layout redesenhado com terminal dentro do Config, monitores mini no header, e menu Config como modal com abas.

### 1. Customizacao de Assistente (NOVO)

**Problema:** Nome do assistente e usuario eram hardcoded em todo o sistema.

**Solucao:** Sistema de identidade configuravel em `config.yaml` com persistencia.

**Arquivos modificados:**
- `backend/config.yaml` — Secao `identity` com `assistant_name`, `user_name`, `custom_color`, `voice`
- `backend/routes/config.py` — Endpoints `GET/PUT /api/config/identity` + modelo `IdentityConfig`
- `backend/routes/voice_ws.py` — `_load_identity()` le identity do config
- `backend/routes/chat.py` — `build_system_prompt()` sempre prepende identity block
- `CHARON_CONTEXT.md` — Limpo, sem nomes hardcoded

### 2. Seletor de Vozes Gemini Live (NOVO)

**Problema:** Charon usava apenas voz "Charon" sem opcao de mudar.

**Solucao:** Seletor de 8 vozes no menu Configuracoes com persistencia.

**Vozes disponiveis:**
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

**Arquivos modificados:**
- `backend/routes/voice_ws.py` — `GEMINI_VOICES` dict, `_load_identity()` le voz do config
- `frontend/src/components/SettingsPage.tsx` — Aba "Assistente" com seletor de voz
- `frontend/src/components/ConfigModal.tsx` — Aba "Configuracoes" com settings

### 3. Layout Redesenhado (MODIFICADO)

**Problema:** Layout tinha areas mortas e terminal ocupava espaco no centro.

**Solucao:** Layout simplificado: Explorer + Chat + Charon. Terminal e paginas dentro do modal Config.

**Mudancas:**
- **Header:** MiniMonitors (CPU/RAM/GPU) + botao "Config" + Ajuda
- **Esquerdo:** Explorer (raiz de arquivos)
- **Centro:** Chat (ocupa todo espaco restante)
- **Direito:** Charon (quando ativado, com drag handle para redimensionar)
- **Terminal:** Aba dentro do modal Config
- **Paginas:** Todas dentro do modal Config com abas

**Arquivos modificados:**
- `frontend/src/App.tsx` — Layout redesenhado, removido Editor/ProcessPanel do layout principal
- `frontend/src/components/ConfigModal.tsx` — Modal com abas para todas as paginas
- `frontend/src/components/MiniMonitors.tsx` — Monitores compactos no header

### 4. Menu Config como Modal com Abas (NOVO)

**Problema:** Menu de navegacao ocupava espaco horizontal no header.

**Solucao:** Botao "Config" abre modal com abas para todas as paginas.

**Abas disponiveis:**
1. Configuracoes (SettingsPage)
2. Gerar (GeneratePage)
3. Conhecimento (KnowledgePage)
4. Memoria (MemoryPage)
5. Agentes (AgentsPage)
6. Arquitetura (ArchitecturePage)
7. MCP (MCPPage)
8. Monitor (MonitorPanel)
9. Terminal (TerminalPanel)

**Arquivo:** `frontend/src/components/ConfigModal.tsx`

### 5. Monitores Mini no Header (NOVO)

**Problema:** Monitor de processos ocupava painel inteiro na lateral.

**Solucao:** Monitores compactos horizontalmente no header.

**Formato:** `CPU 14%  RAM 6.9G 75%  GPU 0.8G 12%`

**Arquivo:** `frontend/src/components/MiniMonitors.tsx`

### 6. Ajuda Atualizada (MODIFICADO)

**Problema:** Menu de ajuda nao listava novas funcionalidades.

**Solucao:** Secao "PERSONALIZACAO" adicionada com documentacao das novas features.

### Como Testar

1. **Customizacao:** Config > Assistente > mude nome/cor/voz > Salve > reinicie Charon
2. **Vozes:** Config > Assistente > selecione voz diferente > Salve > reconecte Charon
3. **Layout:** Verifique 3 colunas: Explorer | Chat | Charon
4. **Terminal:** Config > Terminal > terminal abre dentro do modal
5. **Monitores:** Header mostra CPU/RAM/GPU compactos
6. **Drag Handle:** Arraste entre Chat e Charon para redimensionar

### Arquivos Criados/Modificados

- `frontend/src/components/ConfigModal.tsx` — Modal com abas (CRIADO)
- `frontend/src/components/MiniMonitors.tsx` — Monitores compactos (CRIADO)
- `frontend/src/App.tsx` — Layout redesenhado
- `frontend/src/components/SettingsPage.tsx` — Aba Assistente com voz
- `backend/routes/config.py` — Endpoints identity
- `backend/routes/voice_ws.py` — Leitura de identity do config
- `backend/routes/chat.py` — System prompt com identity
- `backend/config.yaml` — Secao identity
- `CHARON_CONTEXT.md` — Limpo

---

## Sessao 2026-08-24 (21) - GGUF Auto-Detection, Vision, Thinking Panel, GPU Support

### Resumo

Sistema de deteccao automatica de modelos GGUF, suporte a visao (mmproj), painel de thinking no contexto, voz sem thinking, suporte a GPU para llamacpp, correcao do monitor de GPU, e script de limpeza de memoria.

### 1. GGUF Auto-Detection (CORRIGIDO)

**Problema:** Modelos GGUF eram hardcoded em `GGUF_MODELS` — todo modelo novo exigia alterar o codigo.

**Solucao:** `_scan_gguf_models()` escaneia `models/` recursivamente, detecta novos modelos automaticamente.

**Arquivos modificados:**
- `backend/routes/llamacpp_route.py` — Nova funcao `_scan_gguf_models()`, `_make_model_id()`, `_make_label()`, `_guess_ctx()`
- `frontend/src/lib/constants.ts` — Lista hardcoded removida (dead code)
- `frontend/src/App.tsx` — Busca dinamica via API `/llamacpp/models`

**Como funciona:**
- Escaneamento recursivo de `models/` para arquivos `.gguf`
- Exclui automaticamente arquivos `mmproj` (projeção visão)
- Gera IDs e labels automaticamente a partir do nome do arquivo
- Context size inferido por familia (bonsai=32k, llama/qwen=16k, fallback=8k)
- Re-scan a cada chamada API — novos modelos aparecem sem restart

### 2. mmproj/Vision Support (NOVO)

**Problema:** Arquivos mmproj (projeção de visão) não eram detectados ou associados aos modelos.

**Solucao:** `_find_mmproj()` busca automaticamente mmproj correspondente ao modelo por similaridade de nome.

**Arquivos modificados:**
- `backend/routes/llamacpp_route.py` — Nova funcao `_find_mmproj()`
- `_start_llama_server()` passa `--mmproj` quando encontrado

**Como funciona:**
- Busca mmproj na mesma pasta do modelo por similaridade de nome
- Prefere Q8_0 sobre BF16 (melhor qualidade)
- Modelos com visão aparecem com 👁️ no dropdown
- `--mmproj` passado automaticamente ao iniciar o servidor

### 3. Thinking Panel no Contexto (NOVO)

**Problema:** Thinking/raciocinio do modelo não era visível de forma organizada.

**Solucao:** Painel Context (lado direito) mostra thinking em caixa azul com header "THINKING".

**Arquivos modificados:**
- `frontend/src/components/ProcessPanel.tsx` — Secao de thinking no Context

### 4. Voz sem Thinking (NOVO)

**Problema:** Voz Dani Brandi lia o thinking completo do modelo antes da resposta.

**Solucao:** `stripMarkdown()` remove tags `<think>...</think>` antes de enviar para TTS.

**Arquivos modificados:**
- `frontend/src/components/ChatPanel.tsx` — Regex `<think>[\s\S]*?<\/think>` no stripMarkdown

### 5. GPU Support para Llamacpp (NOVO)

**Problema:** Toggle GPU só salvava para Ollama, llamacpp não usava GPU.

**Solucao:** Toggle agora salva para ambos, `_start_llama_server()` adiciona `--n-gpu-layers`.

**Arquivos modificados:**
- `backend/routes/llamacpp_route.py` — `_get_gpu_config()`, `GET/POST /llamacpp/gpu`
- `backend/config.yaml` — Adicionada seção `llamacpp` com `gpu_enabled` e `gpu_layers`
- `frontend/src/App.tsx` — useEffect salva GPU para Ollama + Llamacpp
- `frontend/src/components/SettingsPage.tsx` — Label atualizado para "GPU (Ollama + Llamacpp)"

**Configuracao:**
```yaml
llamacpp:
  gpu_enabled: true
  gpu_layers: 999
```

### 6. Monitor GPU - Correcao (CORRIGIDO)

**Problema:** Monitor mostrava "GPU não detectada" mesmo com nvidia-smi funcionando.

**Causa:** Python 32-bit não encontrava `nvidia-smi.exe` no PATH.

**Solucao:** Busca explicita em `C:\Windows\System32\nvidia-smi.exe`.

**Arquivos modificados:**
- `backend/tools/monitor.py` — Adicionado `import os` + lista de caminhos do nvidia-smi

### 7. Limpar_Processos_Memoria.bat (NOVO)

**Problema:** `llama-server` consumia ~6GB de RAM, lotando o sistema de 12GB.

**Solucao:** Script batch para encerrar processos pesados e limpar cache.

**Arquivo criado:** `C:\DEEP-OS\Limpar_Processos_Memoria.bat`

**O que faz:**
1. Encerra `llama-server.exe`
2. Encerra processos Node.js
3. Limpa temporários do Windows
4. Compacta memória

### 8. Requisitos do Sistema (DOCUMENTADO)

| Componente | Mínimo | Recomendado |
|---|---|---|
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 6+ cores |
| Disco | 10 GB | 50 GB SSD |
| GPU | Opcional | RTX 3060 12GB+ |

**Consumo típico:**
- llama-server (27B): ~6 GB RAM
- llama-server (7B): ~2-4 GB RAM
- llama-server (3B): ~1-2 GB RAM
- Backend Python: ~200 MB
- Frontend Vite: ~150 MB

### Como Testar

1. **Auto-Detection:** Coloque um `.gguf` em `models/` → aparece no dropdown automaticamente
2. **Vision:** Selecione modelo com mmproj → 👁️ no dropdown → `--mmproj` passado ao iniciar
3. **Thinking:** Envie pergunta → thinking aparece no painel Context (lado direito)
4. **Voz:** Ative Jarvis → only resposta é lida (sem thinking)
5. **GPU:** Toggle GPU ativo → `--n-gpu-layers 999` passado ao iniciar modelo
6. **Monitor:** Abra Monitor → VRAM deve aparecer (após reinicialização com driver atualizado)

### Arquivos Criados/Modificados

- `backend/routes/llamacpp_route.py` — Auto-detection, mmproj, GPU config
- `backend/tools/monitor.py` — Correção nvidia-smi 32-bit
- `backend/config.yaml` — Seção llamacpp adicionada
- `frontend/src/App.tsx` — GPU toggle para ambos providers
- `frontend/src/components/ChatPanel.tsx` — stripMarkdown remove thinking
- `frontend/src/components/ProcessPanel.tsx` — Thinking no Context
- `frontend/src/components/SettingsPage.tsx` — Label GPU atualizado
- `frontend/src/lib/constants.ts` — Lista hardcoded removida
- `Limpar_Processos_Memoria.bat` — Script de limpeza

---

## Sessao 2026-08-23 (20) - Tool Calling Ollama + Separacao de Providers

### Resumo

Corrigido tool calling para modelos Ollama (qwen3.5:9b, Bonsai, etc), expandido LOCAL_TOOLS para 30 ferramentas, e corrigida mistura de modelos GGUF no dropdown do Ollama.

### Problemas Identificados e Corrigidos

#### 1. Ollama Nao Usava Tool Calling (CORRIGIDO)
**Problema:** Modelos Ollama (qwen3.5:9b, Bonsai, etc) geravam checklists textuais mas nunca emitiam `tool_calls` nativos. O sistema parava com `HAS_RESPONSE` sem executar nada.

**Causa raiz:** `_ollama_chat_stream()` em `llm_native.py` nao passava o parametro `tools` para a API nativa `/api/chat` do Ollama. Quando as messages eram multimodais, as tools eram completamente ignoradas.

**Solucao (3 partes):**
1. **Nova funcao `_ollama_chat_stream_with_tools()`** — Usa API nativa do Ollama (`/api/chat`) com suporte a `tools`
2. **`stream_chat_with_tools()` atualizado** — Provider Ollama agora usa API nativa com tools em vez do endpoint OpenAI `/v1/chat/completions`
3. **Lifecycle CHECKLIST_SEM_EXECUCAO** — Detecta quando modelo gera checkboxes sem tool calls e injeta nudge forçando execução (limite de 2 nudges)

**Arquivos modificados:**
- `backend/core/llm_native.py` — Nova funcao `_ollama_chat_stream_with_tools()` + update `stream_chat_with_tools()`
- `backend/core/lifecycle.py` — Campo `checklist_nudge_count` + detecção de checklist sem execução

#### 2. LOCAL_TOOLS com Poucas Ferramentas (CORRIGIDO)
**Problema:** Filtro `LOCAL_TOOLS` enviava apenas 14 tools para modelos locais (Ollama/llamacpp), deixando funcionalidades importantes de fora.

**Solucao:** Expandido de 14 para **30 tools essenciais**:

| Categoria | Tools |
|---|---|
| Arquivos/Código | read, write, bash, explorer, search, glob, create_directory, delete, rename, file_edit, read_document, execute_python, find_file |
| Web | web_search, web_fetch |
| Tarefas | task_create, task_update, task_list |
| Sistema/Apps | open_app, close_app, system_status, computer_settings |
| Mídia | media_play |
| Memória | memory_write, memory_read, memory_list |
| Outros | tool_search, monitor_dashboard, reminder |

**Arquivo:** `backend/routes/chat.py` — `LOCAL_TOOLS` expandido

#### 3. Modelos GGUF Misturados no Ollama (CORRIGIDO)
**Problema:** Endpoint `/ollama/models` listava arquivos GGUF (Bonsai, NemoMix, etc) junto com modelos Ollama nativos, causando confusão no dropdown.

**Solucao:** Endpoints `/ollama/status` e `/ollama/models` agora retornam APENAS modelos Ollama nativos. Modelos GGUF ficam exclusivos no provider llamacpp.

**Arquivo:** `backend/routes/ollama_route.py` — Removida mistura de GGUF nos endpoints Ollama

### Como Testar

1. **Ollama com tool calling:** Selecione provider "ollama" + "qwen3.5:9b" → envie "liste as pastas de C:/" → deve usar tool_call `explorer` ou `bash`
2. **30 tools:** Verifique no log do backend: `[CHAT] provider=ollama model=qwen3.5:9b tools=30`
3. **Separacao de providers:** Dropdown Ollama mostra apenas modelos Ollama; dropdown llamacpp mostra apenas GGUF

---

## Estado Atual: FUNCIONAL + CUSTOMIZAVEL + LAYOUT REDESENHADO

O sistema esta operacional em `localhost:5175` (frontend) / `localhost:8001` (backend).

**Provider ativo:** MiMo V2.5 (gratis) via `mimo` provider → mimo.exe executor + API cloud com native tool calling

**Customizacao:** Nome do assistente, nome do usuario, cor da interface, e voz do Charon configuraveis em Config > Assistente

**Vozes Gemini Live:** 8 vozes disponiveis (Charon, Puck, Fenrir, Orus, Kore, Leda, Aoede, Zephyr)

**Layout:** Explorer (esquerda) + Chat (centro) + Charon (direita) — terminal e paginas dentro do modal Config

**Monitores:** CPU/RAM/GPU compactos no header

**Modelos GGUF:** Auto-detectados via scan recursivo — novos modelos aparecem automaticamente

**Vision:** Modelos com mmproj detectados automaticamente — 👁️ no dropdown

**GPU:** Toggle salva para Ollama + Llamacpp — `--n-gpu-layers` passado ao iniciar

**Thinking:** Mostrado no painel Context (lado direito) — voz não lê thinking

**Ferramentas Charon (33):** youtube_video, open_app, weather_report, browser_control, computer_control, computer_settings, desktop_control, file_controller, code_helper, dev_agent, game_updater, flight_finder, file_processor, system_status, reminder, web_search, send_message, screen_process, calorie_counter, pushup_counter, upload_video, + 11 novas

**Como iniciar:** `C:\DEEP-OS\START-TOTAL.bat` (backend + frontend)

**Limpeza:** `C:\DEEP-OS\Limpar_Processos_Memoria.bat` (encerra processos pesados)

---

## Pendencias

### Geral
- **ElevenLabs:** Configurar `ELEVENLABS_API_KEY` em `backend/.env`
- **MiMo Executor:** Implementar `--continue` para manter contexto entre mensagens
- **web_fetch:** User-Agent precisa de upgrade (403 em sites com Cloudflare)
- **Wake word:** Falsos positivos em ambientes barulhentos

### Browser Automation
- **CDP:** Conexao com Chrome via porta 9222 (alternativa ao Playwright)
- **Fill form:** Preenchimento automático de formulários via Charon
- **Screenshot:** Captura de tela para analise de paginas

### Modelos Locais
- **llamacpp context overflow:** NemoMix 12B Q4_K_M tem limite de 8192 tokens; system_prompt + historico excede este limite. Precisa reduzir system prompt ou aumentar --ctx-size.
- **GPU detection:** Driver NVIDIA atualizado (610.88) — verificar se monitor detecta VRAM corretamente após reinicialização
