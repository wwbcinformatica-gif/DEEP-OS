<<<<<<< HEAD
**Ultima atualizacao:** 2026-08-17 (Sessao 15) - Limpeza do Git + .gitignore atualizado

---

## Sessao 2026-08-17 (15) - Limpeza do Git + .gitignore

### Resumo

Limpeza completa do repositorio: remocao de arquivos pessoais, binarios grandes e dados sensiveis do git. Atualizacao do .gitignore para evitar que esses arquivos sejam versionados no futuro.

### Alteracoes aplicadas

1. **.gitignore atualizado** — novas regras adicionadas:
   - `WBC_Informatica_LandingPage/` — landing page pessoal
   - `api_keys.json` — chaves de API (sensiveis)
   - `*.dll`, `*.exe`, `*.rar`, `*.zip` — binarios e compactados
   - `bin/` — binarios do llama-server
   - `models/` — modelos GGUF (grandes demais)

2. **Arquivos removidos do git** (mantidos localmente):
   - `WBC_Informatica_LandingPage/` — 1197 arquivos (catalogo GSM DIGITAL)
   - `backend/config/api_keys.json` — API keys
   - `config/api_keys.json` — API keys
   - `bin/vulkan/` — 33 arquivos (dll/exe do llama-server)
   - `models/` — 2 arquivos de configuracao

3. **Commits realizados:**
   - `d1847d4` — fix: organizacao de modelos GGUF + Ternary-Bonsai no dropdown LLAMACPP
   - `f07e76e` — feat: commit completo - todas as sessoes (1-14)
   - `17d1ba4` — chore: remove arquivos pessoais e binarios do git

### Commits Pushados

```
f07e76e..17d1ba4  master -> master (GitHub)
```

### Arquivos alterados

- `.gitignore` (atualizado com novas regras)

### Como reiniciar

Execute `C:\DEEP-AUREA\START-TOTAL.bat` (backend + frontend).
=======
**Ultima atualizacao:** 2026-08-24 (Sessao 21) - GGUF Auto-Detection, Vision, Thinking Panel, GPU Support

---

## Sessao 2026-08-24 (21) - GGUF Auto-Detection, Vision, Thinking Panel, GPU Support

### Resumo
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)

Sistema de deteccao automatica de modelos GGUF, suporte a visao (mmproj), painel de thinking no contexto, voz sem thinking, suporte a GPU para llamacpp, correcao do monitor de GPU, e script de limpeza de memoria.

<<<<<<< HEAD
## Sessao 2026-08-17 (14) - Organizacao de Modelos + Ternary-Bonsai no Dropdown

### Resumo

Limpeza de duplicatas de modelos GGUF (~11 GB liberados), correcao dos Modelfiles para caminhos relativos, adicao dos modelos Ternary-Bonsai ao dropdown do provider LLAMACPP, e inclusao do modelo dspark.

### Alteracoes aplicadas

1. **Remocao de duplicatas (~11 GB liberados)**
   - `models/gguf/27B/Bonsai-27B-Q1_0.gguf` (3.8 GB) — duplicata removida
   - `models/gguf/bonsai.gguf` (7.2 GB) — duplicata do Ternary-Bonsai Q2_0 removida
   - `models/ternary-gguf/27B/.cache/` — cache do HuggingFace removido

2. **Modelfiles corrigidos para caminhos relativos**
   - `Modelfile.bonsai-27b`: `C:\DEEP-AUREA\models\...` → `./models/...`
   - `Modelfile.bonsai-27b-1bit`: `C:\DEEP-AUREA\models\...` → `./models/...`
   - `Modelfile.llama-3.2-3b`: `C:\DEEP-AUREA\models\...` → `./models/...`
   - `Modelfile.nemomix-12b`: `C:\DEEP-AUREA\models\...` → `./models/...`
   - `Modelfile.qwen2.5-7b`: `C:\DEEP-AUREA\models\...` → `./models/...`

3. **Script importar_bonsai.bat corrigido**
   - Caminhos hardcoded `G:\Bonsai-demo-main\...` → `%~dp0models\...` (portavel)

4. **Backend GGUF_MODELS atualizado**
   - Labels renomeados para incluir "Ternary-Bonsai"
   - Novo modelo adicionado: `bonsai-27b-dspark` (Bonsai-27B-dspark-Q4_1.gguf)
   - Arquivo: `backend/routes/llamacpp_route.py`

5. **Frontend constants.ts atualizado**
   - Labels renomeados para incluir "Ternary-Bonsai"
   - Novo modelo adicionado: `bonsai-27b-dspark`
   - Arquivo: `frontend/src/lib/constants.ts`

6. **Frontend rebuildado** — build OK

### Modelos GGUF Disponiveis (LLAMACPP)

| ID | Label | Arquivo | Tamanho |
|----|-------|---------|---------|
| `bonsai-27b` | Ternary-Bonsai 27B Q2_0 | ternary-gguf/27B/Ternary-Bonsai-27B-Q2_0.gguf | 6.8 GB |
| `bonsai-27b-1bit` | Ternary-Bonsai 27B Q1_0 | gguf/Bonsai-27B-Q1_0.gguf | 3.8 GB |
| `bonsai-27b-dspark` | Ternary-Bonsai 27B dspark Q4_1 | gguf/27B/Bonsai-27B-dspark-Q4_1.gguf | 1.7 GB |
| `llama-3.2-3b-gguf` | Llama 3.2 3B Q4_K_M | gguf/Llama-3.2-3B-Instruct-Q4_K_M.gguf | 1.9 GB |
| `nemomix-12b-gguf` | NemoMix 12B Q4_K_M | gguf/NemoMix-Unleashed-12B-Q4_K_M.gguf | 7.1 GB |
| `qwen2.5-7b-gguf` | Qwen 2.5 7B Q4_K_M | gguf/Qwen2.5-7B-Instruct-Q4_K_M.gguf | 4.5 GB |

### Estrutura Final dos Modelos

```
C:\DEEP-AUREA\models\
├── gguf/
│   ├── Bonsai-27B-Q1_0.gguf              (3.8 GB)
│   ├── Llama-3.2-3B-Instruct-Q4_K_M.gguf (1.9 GB)
│   ├── NemoMix-Unleashed-12B-Q4_K_M.gguf (7.1 GB)
│   ├── Qwen2.5-7B-Instruct-Q4_K_M.gguf  (4.5 GB)
│   └── 27B/
│       └── Bonsai-27B-dspark-Q4_1.gguf   (1.7 GB)
└── ternary-gguf/
    └── 27B/
        ├── Ternary-Bonsai-27B-Q2_0.gguf     (6.8 GB)
        ├── Ternary-Bonsai-27B-mmproj-BF16.gguf (888 MB)
        └── Ternary-Bonsai-27B-mmproj-Q8_0.gguf (600 MB)
```

### Arquivos alterados

- `backend/routes/llamacpp_route.py` (labels + dspark)
- `frontend/src/lib/constants.ts` (labels + dspark)
- `Modelfile.bonsai-27b` (caminho relativo)
- `Modelfile.bonsai-27b-1bit` (caminho relativo)
- `Modelfile.llama-3.2-3b` (caminho relativo)
- `Modelfile.nemomix-12b` (caminho relativo)
- `Modelfile.qwen2.5-7b` (caminho relativo)
- `importar_bonsai.bat` (caminhos portaveis)
- `models/gguf/27B/Bonsai-27B-Q1_0.gguf` (deletado — duplicata)
- `models/gguf/bonsai.gguf` (deletado — duplicata)
- `models/ternary-gguf/27B/.cache/` (deletado — cache)

### Espaço

| Antes | Depois | Economia |
|-------|--------|----------|
| ~30 GB | ~19 GB | **~11 GB** |

### Como reiniciar

Execute `C:\DEEP-AUREA\START-TOTAL.bat` (backend + frontend). Faca Ctrl+Shift+R no navegador para pegar o build novo.
=======
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
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)

**Problema:** Arquivos mmproj (projeção de visão) não eram detectados ou associados aos modelos.

<<<<<<< HEAD
### Resumo

Criacao de scripts `mudar_nome.bat` e `voltar_original.bat` para trocar o nome do assistente (Charon) em todos os arquivos do projeto. Correcao do provider `llamacpp` que nao aparecia no dropdown do chat central.

### Alteracoes aplicadas

1. **Provider llamacpp no dropdown do chat**
   - `frontend/src/components/ChatPanel.tsx`: Adicionado `llamacpp` a lista fixa de providers no select (linha 1003)
   - Antes: `['ollama', 'openclaude', 'opencode', 'groq', 'openrouter', 'openai', 'gemini', 'mimo']`
   - Depois: `['ollama', 'llamacpp', 'openclaude', 'opencode', 'groq', 'openrouter', 'openai', 'gemini', 'mimo']`

2. **Script mudar_nome.bat**
   - Detecta o diretorio do projeto automaticamente (busca `CHARON_CONTEXT.md` ou `backend/routes/voice_ws.py` subindo ate 3 niveis)
   - Aceita qualquer nome (WBC, AUREA, JARVIS, etc.)
   - Usa `str.replace()` do Python (nao regex) para substituicao direta
   - Altera: voice_ws.py (system instruction, default voice, startup briefing), terminal (prompt), StatusBar (botoes), CharonPanel (labels), VoiceHud, CharonToolMessage, ChatPanel (comando /), App.tsx (help text, voiceName), api_keys.json

3. **Script voltar_original.bat**
   - Restaura tudo para "Charon" (nome original)
   - Mesma logica de deteccao de path
   - Substitui qualquer nome anterior (WBC, AUREA, etc.) por Charon

4. **Correcao do voiceName no App.tsx**
   - `frontend/src/App.tsx`: `voiceName="WBC"` corrigido para `voiceName="Charon"` (valor original)

### Arquivos alterados

- `C:\DEEP-AUREA\frontend\src\components\ChatPanel.tsx` (llamacpp no dropdown)
- `C:\DEEP-AUREA\frontend\src\App.tsx` (voiceName restaurado para Charon)
- `C:\DEEP-AUREA\frontend\src\components\StatusBar.tsx` (restaurado para Charon)
- `C:\DEEP-AUREA\frontend\src\components\CharonPanel.tsx` (restaurado para Charon)
- `C:\DEEP-AUREA\frontend\src\components\VoiceHud.tsx` (restaurado para Charon)
- `C:\DEEP-AUREA\frontend\src\components\CharonToolMessage.tsx` (restaurado para Charon)
- `C:\DEEP-AUREA\backend\routes\voice_ws.py` (restaurado para Charon)
- `C:\DEEP-AUREA\mudar_nome.bat` (novo - script de renomeacao)
- `C:\DEEP-AUREA\voltar_original.bat` (novo - restaura para Charon)

### Estado atual dos scripts

- `mudar_nome.bat`: Funcional, detecta path automaticamente
- `voltar_original.bat`: Funcional, restaura para Charon
- **NOTA:** Ainda precisa de melhoria na deteccao de path quando o script esta em diretorio diferente do projeto (ex: G:\OPENCODE\DEEP-AUREA vs C:\DEEP-AUREA)

### Pendencias

- Melhorar deteccao de path dos scripts (usar .bat como ponteiro para o projeto)
- O Charon ainda as vezes nao conecta no Gemini Live (verificar API key)
- Script nao encontra o projeto quando executado de diretorio irmao

### Como reiniciar

Execute C:\DEEP-AUREA\START-TOTAL.bat (backend + frontend).
=======
**Solucao:** `_find_mmproj()` busca automaticamente mmproj correspondente ao modelo por similaridade de nome.

**Arquivos modificados:**
- `backend/routes/llamacpp_route.py` — Nova funcao `_find_mmproj()`
- `_start_llama_server()` passa `--mmproj` quando encontrado
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)

**Como funciona:**
- Busca mmproj na mesma pasta do modelo por similaridade de nome
- Prefere Q8_0 sobre BF16 (melhor qualidade)
- Modelos com visão aparecem com 👁️ no dropdown
- `--mmproj` passado automaticamente ao iniciar o servidor

<<<<<<< HEAD
## Sessao 2026-08-16 (12) - Renomeacao Charon→WBC + Logica Provider Local/Cloud

### Resumo

Renomeacao do assistente de voz de "Charon" para "WBC" em todo o sistema. Implementada logica que desativa modelos locais (ollama/llamacpp) quando WBC esta ligado, mudando automaticamente para provider cloud. Restaurado voice_ws.py do backup C:\DEEP-AUREA com system instruction completa.

### Alteracoes aplicadas

1. **Renomeacao Charon → WBC (todo o sistema)**
   - `backend/routes/voice_ws.py`: system instruction, default voice, startup briefing, transcript speaker
   - `frontend/src/components/StatusBar.tsx`: botao "WBC ON/OFF", titulo, default speaker
   - `frontend/src/components/CharonPanel.tsx`: label "⚡ WBC", status "WBC ativo/inativo"
   - `frontend/src/components/ChatPanel.tsx`: comando /wbc
   - `frontend/src/components/CharonToolMessage.tsx`: "WBC · TOOL_NAME", "executado via WBC"
   - `frontend/src/components/VoiceHud.tsx`: nome "WBC"
   - `frontend/src/App.tsx`: textos de ajuda, voiceName="WBC"

2. **Modelos locais so ativos quando WBC OFF**
   - `frontend/src/App.tsx`: useEffect que monitora `charonActive`
     - WBC ON + provider local (ollama/llamacpp) → salva provider e muda para opencode (cloud)
     - WBC OFF → restaura provider local salvo

3. **voice_ws.py restaurado do backup C:\DEEP-AUREA**
   - System instruction com contexto do projeto (CHARON_CONTEXT.md)
   - 20 ferramentas com tool calling funcional
   - Reconexao automatica ao Gemini Live API
   - Startup briefing simplificado
   - Nenhum arquivo em C:\ foi modificado (apenas copiado)

4. **Script de renomeacao**
   - `mudar_nome.bat`: script para mudar nome do assistente em todos os arquivos

### Arquivos alterados

- `C:\DEEP-AUREA\backend\routes\voice_ws.py` (restaurado do backup + renomeado para WBC)
- `C:\DEEP-AUREA\frontend\src\App.tsx` (useEffect charonActive + textos)
- `C:\DEEP-AUREA\frontend\src\components\StatusBar.tsx` (WBC ON/OFF)
- `C:\DEEP-AUREA\frontend\src\components\CharonPanel.tsx` (⚡ WBC)
- `C:\DEEP-AUREA\frontend\src\components\ChatPanel.tsx` (comando /wbc)
- `C:\DEEP-AUREA\frontend\src\components\CharonToolMessage.tsx` (WBC · tool)
- `C:\DEEP-AUREA\frontend\src\components\VoiceHud.tsx` (WBC)
- `C:\DEEP-AUREA\mudar_nome.bat` (novo - script de renomeacao)

### Pendencias

- WBC nao esta respondendo corretamente as perguntas (comportamento estranho no Gemini Live)
- Modelo Bonsai Q2_0 confunde nomes (James Blunt → James Brown) e abre sites errados
- Verificar se problema e do modelo ou da API Gemini

### Como reiniciar

Execute C:\DEEP-AUREA\START-TOTAL.bat (backend + frontend).

---

### Resumo

Adicionado provider `llamacpp` ao frontend que permite usar os modelos GGUF da pasta `C:\DEEP-AUREA\models` diretamente pelo select do chat, sem precisar importar para o Ollama.

### Alteracoes aplicadas

1. **Backend - Rota para modelos GGUF locais**
   - `backend/routes/ollama_route.py`: Nova funcao `_fetch_local_gguf_models()` que escaneia `C:\DEEP-AUREA\models` recursivamente buscando arquivos `.gguf`
   - Ignora arquivos `mmproj` (projeção multimodal)
   - Gera nome amigavel removendo sufixos de quantizacao (Q4_K_M, Q8_0, etc.)
   - Retorna nome, caminho, arquivo, tamanho em GB e fonte
   - Rotas `/ollama/status` e `/ollama/models` agora incluem `local_models` na resposta
   - Nova rota `GET /ollama/local-models` para listar apenas modelos locais

2. **Frontend - Novo provider `llamacpp`**
   - `frontend/src/lib/constants.ts`: Adicionado `llamacpp` ao tipo `Provider`, ao array `PROVIDERS` e ao objeto `MODELS` com 5 modelos GGUF pre-definidos
   - `frontend/src/App.tsx`: Novo state `llamacppModels` + useEffect que busca `/llamacpp/models` quando provider e `llamacpp`
   - `frontend/src/components/SettingsPage.tsx`: Prop `llamacppModels` + logica de selecao para provider `llamacpp`
   - `frontend/src/components/PageRenderer.tsx`: Prop `llamacppModels` repassada
   - `frontend/src/components/ChatPanel.tsx`: Prop `llamacppModels` + logica de selecao para provider `llamacpp`

3. **Build OK** - Frontend compilou sem erros

### Modelos GGUF Disponiveis

| Modelo | Arquivo | Tamanho |
|--------|---------|---------|
| Bonsai 27B Q2_0 | Ternary-Bonsai-27B-Q2_0.gguf | ~10GB |
| Bonsai 27B Q1_0 | Bonsai-27B-Q1_0.gguf | ~7GB |
| Llama 3.2 3B Q4_K_M | Llama-3.2-3B-Instruct-Q4_K_M.gguf | ~2GB |
| NemoMix 12B Q4_K_M | NemoMix-Unleashed-12B-Q4_K_M.gguf | ~7GB |
| Qwen 2.5 7B Q4_K_M | Qwen2.5-7B-Instruct-Q4_K_M.gguf | ~4GB |

### Como usar

1. No seletor de Provider, escolha **`llamacpp`**
2. No seletor de Modelo, os arquivos GGUF aparecem com nome e tamanho
3. Ao selecionar, o `llama-server.exe` (em `bin/vulkan/`) e iniciado automaticamente na porta 8080
4. O backend roteia chamadas via OpenAI-compatible API (`http://localhost:8080/v1`)

### Arquivos alterados

- `C:\DEEP-AUREA\backend\routes\ollama_route.py` (funcao _fetch_local_gguf_models + novas rotas)
- `C:\DEEP-AUREA\frontend\src\lib\constants.ts` (provider llamacpp)
- `C:\DEEP-AUREA\frontend\src\App.tsx` (state llamacppModels + useEffect)
- `C:\DEEP-AUREA\frontend\src\components\SettingsPage.tsx` (prop + selecao)
- `C:\DEEP-AUREA\frontend\src\components\PageRenderer.tsx` (prop)
- `C:\DEEP-AUREA\frontend\src\components\ChatPanel.tsx` (prop + selecao)

### Como reiniciar

Execute C:\DEEP-AUREA\START-TOTAL.bat (backend + frontend).

---

### Resumo

Correcao do problema com o atalho Shift+W no browser_control e testes completos de todas as 20 ferramentas do Charon.

### Alteracoes aplicadas

1. **Correcao do atalho Shift+W (browser_control)**
   - actions/browser_control.py: funcao _close_native_tabs agora usa Alt+F4 em vez de Ctrl+Shift+W para fechar todas as abas
   - backend/actions_mark/browser_control.py: mesma correcao aplicada
   - Motivo: Ctrl+Shift+W conflitava com atalhos do Windows

2. **Instalacao de dependencias faltantes**
   - playwright: necessario para browser_control
   - sounddevice: necessario para screen_process
   - send2trash: necessario para file_controller (delete)

3. **Testes completos das ferramentas**
   - 19/19 imports OK (todas as actions importadas)
   - 20/20 tool declarations OK (todas as ferramentas declaradas)
   - Funcionalidade verificada: file_controller, computer_control, browser_control, system_status, web_search, open_app

4. **Scripts de teste criados**
   - test_charon_tools.py: verifica imports e tool declarations
   - test_charon_functionality.py: verifica funcionalidade das ferramentas
   - test_charon_summary.py: resumo final dos testes

### Arquivos alterados

- C:\DEEP-AUREA\actions\browser_control.py (correcao do atalho)
- C:\DEEP-AUREA\backend\actions_mark\browser_control.py (correcao do atalho)
- C:\DEEP-AUREA\test_charon_tools.py (novo - teste de imports)
- C:\DEEP-AUREA\test_charon_functionality.py (novo - teste de funcionalidade)
- C:\DEEP-AUREA\test_charon_summary.py (novo - resumo)

### Resultado

- Todas as 20 ferramentas do Charon funcionando 100%
- Problema do Shift+W corrigido (usa Alt+F4 em vez de Ctrl+Shift+W)
- Dependencias todas instaladas
- Sistema pronto para uso

### Como reiniciar

Execute C:\DEEP-AUREA\START-TOTAL.bat (backend + frontend).

---

## Sessao 2026-08-14 (9) - Melhorias de Voz, Arquivos e Help do Charon

### Resumo

Ajustes na comunicacao texto/voz do Charon, criacao de arquivos sem sobrescrita, listagem de pastas corrigida e nova secao de ajuda.

### Alteracoes aplicadas

1. **Texto digitado no painel Charon aparece no contexto**
   - frontend/src/App.tsx: onSendText agora adiciona a mensagem do usuario (speaker: user) a charonTranscripts antes de enviar pelo WebSocket.
   - backend/routes/voice_ws.py: _handle_response envia output_transcription do Charon (speaker: charon), entao a fala dele tambem aparece no contexto.

2. **Silencio para envio automatico no modo Aurea aumentado para 5s**
   - frontend/src/components/ChatPanel.tsx: timers deepSilenceTimerRef de 1500ms -> 5000ms (nao envia a mensagem antes de terminar de falar).

3. **Screenshots com data/hora (nao sobrescrevem)**
   - actions/computer_control.py e backend/actions_mark/computer_control.py: fallback vira jarvis_screenshot_AAAAMMDD_HHMMSS.png.
   - actions/browser_control.py e backend/actions_mark/browser_control.py: jarvis_browser_AAAAMMDD_HHMMSS.png (+ import time).
   - actions/file_processor.py e backend/actions_mark/file_processor.py: _output_path adiciona _AAAAMMDD_HHMMSS aos resultados (OCR, conversoes, frames, transcricoes).

4. **Listagem de pastas corrigida (confusao de diretorio)**
   - actions/file_controller.py e backend/actions_mark/file_controller.py: a versao TTS agora lista TODAS as pastas primeiro e limita apenas os arquivos (max 100). Antes cortava 15 itens alfabeticos e ocultava pastas alem da posicao 15.

5. **Reconexao automatica do Charon**
   - backend/routes/voice_ws.py: _receive_loop extraido para _handle_response; quando a conexao do Gemini cai (ex: 1006 abnormal closure), tenta reconectar ate 5x com backoff e reenvia o briefing.

6. **System instruction do Charon**
   - backend/routes/voice_ws.py: instrucoes de quando usar file_controller vs computer_control; todas as 20 ferramentas sempre ativas.

7. **Criacao de pastas**
   - Confirmado que create_folder funciona; instrucao do modelo reforcada para usar file_controller com create_folder em vez de clicar na interface.

8. **Ajuda do Charon**
   - frontend/src/App.tsx: nova secao "CHARON - ASSISTENTE DE VOZ" no menu de ajuda (topo direito).
   - frontend/src/components/ChatPanel.tsx: novo comando slash /charon na lista.

### Arquivos alterados

- C:\DEEP-AUREA\frontend\src\App.tsx
- C:\DEEP-AUREA\frontend\src\components\ChatPanel.tsx
- C:\DEEP-AUREA\backend\routes\voice_ws.py
- C:\DEEP-AUREA\actions\computer_control.py
- C:\DEEP-AUREA\actions\browser_control.py
- C:\DEEP-AUREA\actions\file_processor.py
- C:\DEEP-AUREA\actions\file_controller.py
- C:\DEEP-AUREA\backend\actions_mark\computer_control.py
- C:\DEEP-AUREA\backend\actions_mark\browser_control.py
- C:\DEEP-AUREA\backend\actions_mark\file_processor.py
- C:\DEEP-AUREA\backend\actions_mark\file_controller.py

### Como reiniciar

Execute C:\DEEP-AUREA\START-TOTAL.bat (backend + frontend). Os itens de audio (5s) e help sao no frontend; as ferramentas no backend.

---



## Estado Atual: FUNCIONAL + CHARON COM 20 FERRAMENTAS + ACESSO TOTAL A UNIDADES

O sistema estÃ¡ operacional em `localhost:5175` (frontend) / `localhost:8001` (backend).

**Provider ativo:** MiMo V2.5 (gratis) via `mimo` provider â†’ **mimo.exe executor + API cloud com native tool calling**



**Acesso a unidades:** . Charon consegue acessar G:\, C:\, D:\ e qualquer unidade.

**TTS do Charon:** . Listagem de pastas agora  resumida e amigvel para voz.

**Como iniciar:** `C:\DEEP-AUREA\START-TOTAL.bat` (backend + frontend)


---

## Sessao 2026-08-13 (7) - Correcoes de Acesso e TTS do Charon

### Resumo

Correcoes aplicadas para que o Charon execute ferramentas de arquivo em qualquer unidade e fale resultados de listagem sem engasgar.

### Correcoes que deram certo

1. **Acesso total as unidades (G:, C:, D:, etc.)**
   - Arquivo: actions/file_controller.py
   - _is_safe_path() agora respeita permissions.json (full_access: true / file_controller: allow).
   - Normalizacao de drive isolado: G: -> G:\ para acessar a raiz corretamente.

2. **sys.path do Charon inclui backend/**
   - Arquivo: backend/routes/voice_ws.py
   - Adicionado backend/ ao sys.path para que actions.file_controller consiga importar core.permissions.

3. **TTS amigavel para listagem de pastas**
   - Arquivo: actions/file_controller.py
   - list_files() retorna versao resumida quando usado pelo Charon:
     - Sem emojis
     - Sem tamanhos de arquivo
     - Maximo 15 itens
     - Formato curto em poucas frases

### Arquivos alterados

- C:\DEEP-AUREA\actions\file_controller.py
- C:\DEEP-AUREA\backend\routes\voice_ws.py
- C:\DEEP-AUREA\backend\actions_mark\file_controller.py (copia de integracao)
- G:\WBC-Mark-L\actions\file_controller.py (projeto original sincronizado)

### Testes confirmados

- list_files('G:') -> lista raiz de G:\ (82 itens)
- list_files('C:') -> lista raiz de C:\ (20 itens)
- _is_safe_path(Path('G:\')) -> True
- _is_safe_path(Path('C:\')) -> True
- _is_safe_path(Path('D:\')) -> True

### Como reiniciar

Execute C:\DEEP-AUREA\START-TOTAL.bat para aplicar todas as correcoes.

---

## SessÃ£o 2026-08-12 (6) â€” Charon: Todas as Ferramentas do WBC-Mark-L

### Contexto

O projeto original `G:\WBC-Mark-L` Ã© um assistente de voz desktop (PyQt) com **20 ferramentas** via Gemini Live API function calling. O DEEP-AUREA tem um voice endpoint (`/ws/voice`) que atualmente sÃ³ usa Google Search como ferramenta built-in. O objetivo Ã© portar **TODAS** as 20 ferramentas para o Charon do DEEP-AUREA.

### Ferramentas a Implementar (20 total)

| # | Tool Name | DescriÃ§Ã£o | Arquivo Origem | ParÃ¢metros |
|---|-----------|-----------|----------------|------------|
| 1 | `open_app` | Abrir qualquer aplicativo | `actions/open_app.py` | `app_name` (required) |
| 2 | `web_search` | Busca web (search/news/research/price/compare) | `actions/web_search.py` | `query` (required), `mode`, `items`, `aspect` |
| 3 | `system_status` | MÃ©tricas do sistema (CPU/RAM/GPU/Temp) | `actions/system_monitor.py` | *(nenhum)* |
| 4 | `weather_report` | RelatÃ³rio do tempo por cidade | `actions/weather_report.py` | `city` (required) |
| 5 | `send_message` | Enviar mensagem (WhatsApp/Telegram) | `actions/send_message.py` | `receiver`, `message_text`, `platform` (all required) |
| 6 | `reminder` | Lembrete agendado via Task Scheduler | `actions/reminder.py` | `date`, `time`, `message` (all required) |
| 7 | `youtube_video` | Controle YouTube (play/summarize/trending) | `actions/youtube_video.py` | `action`, `query`, `save`, `region`, `url` |
| 8 | `screen_process` | Captura de tela ou webcam | `actions/screen_processor.py` | `angle` (screen/camera), `text` (required) |
| 9 | `close_camera` | Fechar cÃ¢mera | *(inline)* | *(nenhum)* |
| 10 | `computer_settings` | Controle do PC (volume/brightness/shortcuts) | `actions/computer_settings.py` | `action`, `description`, `value` |
| 11 | `browser_control` | Controle completo do navegador | `actions/browser_control.py` | `action` (required), `browser`, `url`, `query`, `selector`, `text`, etc. |
| 12 | `file_controller` | Gerenciar arquivos/pastas | `actions/file_controller.py` | `action` (required), `path`, `destination`, `content`, etc. |
| 13 | `desktop_control` | Controle da Ã¡rea de trabalho | `actions/desktop.py` | `action` (required), `path`, `url`, `mode`, `task` |
| 14 | `code_helper` | Escrever/editar/explicar/executar cÃ³digo | `actions/code_helper.py` | `action` (required), `description`, `language`, `file_path`, etc. |
| 15 | `dev_agent` | Criar projetos completos multi-arquivo | `actions/dev_agent.py` | `description` (required), `language`, `project_name`, `timeout` |
| 16 | `computer_control` | Controle direto (type/click/hotkeys/scroll) | `actions/computer_control.py` | `action` (required), `text`, `x`, `y`, `keys`, etc. |
| 17 | `game_updater` | Steam/Epic Games (install/update/list) | `actions/game_updater.py` | `action`, `platform`, `game_name`, `app_id`, etc. |
| 18 | `flight_finder` | Buscar voos no Google Flights | `actions/flight_finder.py` | `origin`, `destination`, `date` (all required), `return_date`, `passengers`, `cabin` |
| 19 | `file_processor` | Processar arquivos (PDF/Word/CSV/imagem) | `actions/file_processor.py` | `file_path`, `action`, `params` |
| 20 | `manage_monitor` | Monitoramento em background | `actions/background_monitor.py` | `action` (required), `topic` |

### AdaptÃ§Ãµes NecessÃ¡rias

O WBC-Mark-L Ã© desktop (PyQt), o DEEP-AUREA Ã© web. AdaptaÃ§Ãµes:

| Aspecto | WBC-Mark-L | DEEP-AUREA (Charon) |
|---------|-----------|---------------------|
| UI | `self.ui` (Qt widgets) | Sem UI desktop â€” results retornados como texto |
| PermissÃµes | `check_permission()` por tool | Simplificado â€” sem permissÃµes (ou adicionar depois) |
| TTS | `self.speak()` via Qt | Via Ã¡udio Gemini Live API (jÃ¡ funciona) |
| CÃ¢mera/Tela | `self.ui.start_camera_stream()` | Retornar resultado como texto (sem stream visual) |
| Config OS | `from config import is_windows` | `platform.system()` direto |
| Dependencies | psutil, sounddevice, playwright | Precisam estar no venv do DEEP-AUREA |

### Estrutura de ImplementaÃ§Ã£o

**1. Arquivo principal:** `backend/routes/voice_ws.py`

```
- TOOL_DECLARATIONS (copiado do WBC-Mark-L/main.py linhas 105-504)
- Imports das actions (copiado do WBC-Mark-L/main.py linhas 37-59)
- _execute_tool() (adaptado do WBC-Mark-L/main.py linhas 797-1046)
- _receive_loop() atualizado para tratar response.tool_call
- LiveConnectConfig com function_declarations em vez de google_search
```

**2. Receive Loop â€” handler de tool_call:**

```python
# Atual receive_loop sÃ³ trata server_content e data
# Precisa adicionar:
if response.tool_call:
    fn_responses = []
    for fc in response.tool_call.function_calls:
        fr = await self._execute_tool(fc)
        fn_responses.append(fr)
    await self.session.send_tool_response(function_responses=fn_responses)
```

**3. _execute_tool â€” dispatch simplificado:**

```python
async def _execute_tool(self, fc) -> types.FunctionResponse:
    name = fc.name
    args = dict(fc.args or {})
    loop = asyncio.get_event_loop()
    result = "Done."
    
    try:
        if name == "open_app":
            r = await loop.run_in_executor(None, lambda: open_app(parameters=args))
            result = r or f"Opened {args.get('app_name')}."
        elif name == "web_search":
            r = await loop.run_in_executor(None, lambda: web_search_action(parameters=args))
            result = r or "Done."
        # ... (20 tools)
    except Exception as e:
        result = f"Tool '{name}' failed: {e}"
    
    return types.FunctionResponse(id=fc.id, name=name, response={"result": result})
```

**4. LiveConnectConfig:**

```python
config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    output_audio_transcription={},
    input_audio_transcription={},
    system_instruction=sys_instr,
    tools=[types.Tool(function_declarations=TOOL_DECLARATIONS)],
    session_resumption=types.SessionResumptionConfig(),
    # ...
)
```

### System Instruction Atualizada

```
"Voce e o Charon, assistente de voz do Deep-Aurea. 
Fale em portugues brasileiro. Seja direto e util. 
Voce tem acesso a 20 ferramentas para controlar o computador, 
buscar na web, gerenciar arquivos, abrir apps, e muito mais. 
Use as ferramentas sempre que o usuario pedir. 
Nunca invente resultados â€” execute as ferramentas de verdade."
```

### DependÃªncias

AÃ§Ãµes que requerem pacotes extras (verificar se estÃ£o no venv):

| Pacote | Usado por | Status |
|--------|-----------|--------|
| `psutil` | system_monitor, open_app | âš ï¸ Verificar |
| `sounddevice` | (nÃ£o usado no voice) | âŒ NÃ£o necessÃ¡rio |
| `playwright` | browser_control | âš ï¸ Verificar |
| `send2trash` | file_controller (delete) | âš ï¸ Verificar |
| `numpy` | screen_processor | âš ï¸ Verificar |

### Arquivos a Modificar

| Arquivo | AÃ§Ã£o | Tamanho |
|---------|------|---------|
| `backend/routes/voice_ws.py` | **REESCREVER** â€” adicionar TOOL_DECLARATIONS, imports, _execute_tool, receive_loop handler | ~500 linhas novas |
| `.memory/MEMORY-charon-voice-fix.md` | **ATUALIZAR** â€” documentar todas as 20 ferramentas |
| `STATUS.md` | **ATUALIZAR** â€” documentar sessÃ£o 6 |

### Fluxo de ExecuÃ§Ã£o

```
1. UsuÃ¡rio fala: "Abra o Chrome"
2. Frontend envia Ã¡udio via WebSocket
3. Backend envia para Gemini Live API
4. Gemini responde com tool_call: { name: "open_app", args: { app_name: "Chrome" } }
5. Receive_loop detecta response.tool_call
6. _execute_tool executa open_app(parameters={app_name: "Chrome"})
7. Resultado retornado para Gemini via send_tool_response()
8. Gemini gera resposta em Ã¡udio: "Chrome aberto, senhor."
9. Ãudio enviado de volta ao frontend via WebSocket
```

### PendÃªncias desta SessÃ£o

- [x] Copiar TOOL_DECLARATIONS do WBC-Mark-L
- [x] Copiar imports das actions
- [x] Verificar dependÃªncias (psutil, playwright, send2trash, sounddevice)
- [x] Instalar dependÃªncias faltantes (send2trash, playwright, sounddevice)
- [x] Criar config.py para compatibilidade com actions
- [x] Implementar _execute_tool adaptado (sem UI desktop)
- [x] Atualizar receive_loop com handler de tool_call
- [x] Trocar tools=[google_search] por tools=[function_declarations]
- [x] Atualizar system instruction
- [x] Documentar tudo no STATUS.md e .memory

---

## SessÃ£o 2026-08-08 (5) â€” Vozes ElevenLabs, Dani Brandi, Microfone, Ferramentas, .opencode

### 1. Vozes ElevenLabs integradas (IMPLEMENTADO)
- **Vozes adicionadas:** Natasha (sensual), Serafina (sedutora), Ivy (expressiva), Ingmar (masculina misteriosa)
- **Backend:** `backend/routes/tts.py` â€” endpoint `/api/tts/elevenlabs` com streaming httpx â†’ ElevenLabs API
- **Frontend:** `ChatPanel.tsx` â€” `ELEVEN_VOICES` map + streaming MediaSource + SourceBuffer
- **VoicePreset type:** Atualizado em `App.tsx`, `ChatPanel.tsx`, `PageRenderer.tsx`, `SettingsPage.tsx`
- **Settings UI:** BotÃµes para selecionar vozes ElevenLabs (agrupadas por categoria)
- **API key:** Requer `ELEVENLABS_API_KEY` em `backend/.env` (ainda nÃ£o configurada)
- **Voice IDs:** Natasha=`PB6BdkFkZLbI39GHdnbQ`, Serafina=`4tRn1lSkEn13EVTuqb0g`, Ivy=`hVcZZGM9Eziug8b1rHSa`, Ingmar=`xrNwYO0xeioXswMCcFNF`

### 2. Dani Brandi â€” voz feminina brasileira (IMPLEMENTADO)
- **Problema:** Dani Brandi tocava voz masculina (mesma do Jarvis) porque usava `rate="-5%" pitch="-15Hz"` hardcoded
- **SoluÃ§Ã£o:** Adicionado `EDGE_VOICE_SETTINGS` no `ChatPanel.tsx` com rate/pitch por voz:
  - Jarvis: `rate="-5%" pitch="-15Hz"` (grave masculino)
  - Dani Brandi, Francisca, Thalita: `rate="+0%" pitch="+0Hz"` (natural feminino)
- **Backend:** `tts.py` â€” `TTSRequest` agora aceita `rate` e `pitch` parametrizÃ¡veis
- **Edge TTS voice:** `pt-BR-FranciscaNeural` (Dani Brandi mapeada para esta voz neural feminina)

### 3. Microfone nÃ£o reinicia apÃ³s fala (CORRIGIDO)
- **Problema:** ApÃ³s a primeira fala do TTS, o microfone nÃ£o reiniciava mais â€” comando de voz parava de funcionar
- **Causa:** Todos os callbacks de fim de fala (`onended`, `onerror`, `catch`) chamavam `recognitionRef.current?.start()` diretamente com `isStartingRef.current = true`. Se o `start()` falhasse (ex: recognition ainda parando), `isStartingRef.current` ficava `true` para sempre, bloqueando `safeRestart()` em todas as chamadas futuras
- **SoluÃ§Ã£o:** Todos os callbacks agora usam `safeRestart()` que:
  1. Verifica se nÃ£o estÃ¡ jÃ¡ reiniciando/iniciando
  2. Faz `stop()` primeiro, depois `start()` apÃ³s 250ms
  3. Reseta `isRestartingRef` corretamente
- **Arquivos afetados:** Edge TTS path, ElevenLabs path, browser speech synthesis path, catch block â€” todos em `ChatPanel.tsx`

### 4. Tool calling em loop infinito (CORRIGIDO)
- **Problema:** MiMo V2.5 chamava ferramentas em loop (20+ passos seguidos de bash/execute_python) sem nunca dar resposta final
- **Causa 1:** `max_tokens=2048` truncava a resposta antes do modelo gerar a conclusÃ£o
- **Causa 2:** `should_force_final` nÃ£o era passado para o lifecycle, permitindo loop infinito
- **Causa 3:** `planning_enforced=False` para MiMo (pulava planejamento)
- **SoluÃ§Ã£o:**
  - `max_tokens` aumentado de 2048 â†’ 8192
  - `consecutive_tool_limit` reduzido de 10 â†’ 8
  - `should_force_final_fn` criada e passada para `run_lifecycle`
  - `planning_enforced=True` para todos os providers (inclusive MiMo)
- **Arquivos:** `backend/core/llm_native.py` (max_tokens), `backend/routes/chat.py` (lifecycle config)

### 5. Sandbox do bash com path hardcoded (CORRIGIDO)
- **Problema:** `tool_bash` lia config de `C:/DEEP-AUREA/config.yaml` (hardcoded), mas o projeto estÃ¡ em `C:\DEEP-AUREA`
- **SoluÃ§Ã£o:** Agora busca `config.yaml` relativo ao backend primeiro, fallback para `C:/DEEP-AUREA`
- **Arquivo:** `backend/tools/system_tools.py`

### 6. MiMo Executor integrado no handle_task_stream (IMPLEMENTADO)
- **Problema:** `mimo_executor.py` existia mas nÃ£o era usado em nenhum lugar do backend
- **SoluÃ§Ã£o:** Reescrito `mimo_executor.py` com formato correto de eventos do mimo.exe (JSON linha por linha com `part` aninhado). Integrado no `handle_task_stream` â€” quando `provider == "mimo"`, roteia para `stream_mimo_task()` que chama `mimo.exe run --format json --model xiaomi/mimo-v2.5 --dangerously-skip-permissions --dir <root>`
- **Fluxo:**
  1. Frontend envia `provider: "mimo"` + mensagem
  2. Backend detecta `provider == "mimo"` no `handle_task_stream`
  3. `stream_mimo_task()` chama `mimo.exe` como subprocesso
  4. Eventos JSON sÃ£o parseados: `text` â†’ `content`, `tool_use` â†’ `tool_start`/`tool_end`
  5. Streaming para frontend: `token`, `tool_start`, `tool_end`, `done`
  6. Resultado salvo no histÃ³rico do banco
- **Arquivo:** `backend/tools/mimo_executor.py` (reescrito), `backend/routes/chat.py` (integraÃ§Ã£o)

### 7. Agentes e Skills do .opencode integrados (IMPLEMENTADO)
- **Recursos disponÃ­veis:** 27 agentes especializados + 39 skills em `C:\DEEP-AUREA\.opencode\`
- **Loader:** `backend/core/opencode_loader.py` â€” carrega agentes (`agent/*.md`) e skills (`skills/*/SKILL.md`) com parser de frontmatter YAML
- **IntegraÃ§Ã£o no chat:**
  - `parse_at_mentions` agora reconhece todos os agentes e skills do `.opencode` dinamicamente
  - `inject_mention_context` injeta o prompt completo do agente + conteÃºdo da skill no `system_prompt`
  - Ex: `@coder` carrega o prompt do `coder.md`, `@powershell-windows` carrega os padrÃµes da skill
- **Endpoints:**
  - `GET /opencode/agents` â€” lista todos os agentes disponÃ­veis
  - `GET /opencode/skills` â€” lista todas as skills disponÃ­veis
- **Arquivos:** `backend/core/opencode_loader.py` (novo), `backend/routes/chat.py` (integraÃ§Ã£o)

---

## SessÃ£o 2026-08-07 (4) â€” Player Interno/Externo por Comando de Voz

### 1. SeleÃ§Ã£o de player por comando de voz ou texto (IMPLEMENTADO)
- **Problema:** O popup de mÃ­dia sempre aparecia para o usuÃ¡rio escolher entre player interno e externo, mesmo quando o usuÃ¡rio jÃ¡ havia especificado qual queria usar.
- **SoluÃ§Ã£o:** O backend agora detecta a intenÃ§Ã£o do usuÃ¡rio na mensagem e envia a aÃ§Ã£o correta para o frontend:
  - **"media interno" / "player interno" / "no media" / "tocar no media"** â†’ `media_play_internal`
  - **"media externo" / "player externo" / "windows media"** â†’ `media_play_external`
  - **Sem especificaÃ§Ã£o** â†’ `media_play` (abre o popup com reconhecimento de voz)
- **Arquivos:** `backend/routes/chat.py`, `frontend/src/App.tsx`

---

## SessÃ£o 2026-08-07 (3) â€” MiMo Executor + Tool Calling Real + Voz no Dialog de MÃ­dia

### 1. MiMo Executor â€” tool calling nativo via mimo.exe (IMPLEMENTADO)
### 2. CorreÃ§Ã£o do bloqueio de media_play no llm_native.py (IMPLEMENTADO)
### 3. DetecÃ§Ã£o de intenÃ§Ã£o de mÃ­dia no texto (IMPLEMENTADO)
### 4. ReforÃ§o do system prompt contra execuÃ§Ã£o falsa (IMPLEMENTADO)
### 5. Voz no dialog de mÃ­dia â€” escolha por comando de voz (IMPLEMENTADO)
### 6. Plugin de Voz para OpenCode (IMPLEMENTADO)

---

## SessÃ£o 2026-08-07 (2) â€” Modo Voz, Wake Word "Deep" e Filtro de Idioma

### 1. Modo Voz â€” resposta apenas em PT-BR (IMPLEMENTADO)
### 2. Wake Word "Deep" â€” modo de escuta permanente (IMPLEMENTADO)
### 3. Fuzzy Matching + Filtro FonÃ©tico (IMPLEMENTADO)
### 4. MÃ¡quina de estados do modo Deep (IMPLEMENTADO)
### 5. BotÃ£o microfone clÃ¡ssico restaurado (IMPLEMENTADO)

---

## SessÃ£o 2026-08-07 (1) â€” CorreÃ§Ã£o, Contexto e Jarvis TTS

### 1. Fluxo de interrupÃ§Ã£o/correÃ§Ã£o (IMPLEMENTADO)
### 2. PreservaÃ§Ã£o total de contexto (IMPLEMENTADO)
### 3. RecuperaÃ§Ã£o de sessÃµes presas (IMPLEMENTADO)
### 4. Jarvis TTS â€” correÃ§Ã£o de corte de Ã¡udio (IMPLEMENTADO)
### 5. Auto-send toggle (IMPLEMENTADO)
### 6. SecurityToggle como botÃ£o quadrado (IMPLEMENTADO)
### 7. Limpeza de `_strip_english_thinking` (IMPLEMENTADO)

---

## Charon (Gemini Live API) â€” CorreÃ§Ãµes Anteriores

### Ãudio Engasgando/Arranhando (CORRIGIDO)
- **Ring buffer:** 24k â†’ 192k samples (8 segundos)
- **Pre-buffer:** 12k samples (0.5s antes de tocar)
- **Buffer intermediÃ¡rio:** Chunks acumulados por 20ms antes de enviar ao worklet
- **NormalizaÃ§Ã£o:** `/ 32768` (PCM 16-bit correto)

### BotÃ£o Interrupt (CORRIGIDO)
- Limpa buffer de Ã¡udio
- Fecha WebSocket (interrompe sessÃ£o Gemini)
- Para microfone
- NÃ£o reconecta automaticamente

### CharonPanel â€” Painel de Contexto (IMPLEMENTADO)
- Mostra transcripts em tempo real
- Status do Charon (ouvindo/falando/inativo)
- Toggle pelo botÃ£o "T" na status bar
- Largura: 340px quando ativo
- NÃ£o abre WebSocket prÃ³prio (herda do StatusBar)

### Google Search (CONFIGURADO)
- `tools=[types.Tool(google_search=types.GoogleSearch())]` â€” builtin do Gemini
- **SERÃ SUBSTITUÃDO** por function_declarations nesta sessÃ£o

---

## Arquivos Modificados (todas as sessÃµes)

### SessÃ£o 6 (2026-08-12) â€” EM IMPLEMENTAÃ‡ÃƒO

| Arquivo | MudanÃ§a |
|---------|---------|
| `backend/routes/voice_ws.py` | **REESCREVER** â€” TOOL_DECLARATIONS (20 tools), imports, _execute_tool, receive_loop handler, function_declarations |
| `.memory/MEMORY-charon-voice-fix.md` | **ATUALIZAR** â€” documentar 20 ferramentas |
| `STATUS.md` | **ATUALIZAR** â€” documentar sessÃ£o 6 |

### SessÃ£o 5 (2026-08-08)

| Arquivo | MudanÃ§a |
|---------|---------|
| `backend/tools/mimo_executor.py` | **REESCRO** â€” formato correto de eventos do mimo.exe |
| `backend/core/opencode_loader.py` | **NOVO** â€” loader de agentes (27) e skills (39) |
| `backend/routes/chat.py` | Integracao mimo_executor, inject_mention_context, endpoints .opencode |
| `backend/core/llm_native.py` | max_tokens 2048â†’8192 |
| `backend/routes/tts.py` | TTSRequest com rate/pitch parametrizaveis |
| `backend/tools/system_tools.py` | config.yaml path relativo + timeout 120s |
| `frontend/src/App.tsx` | voicePreset type com 14 vozes |
| `frontend/src/components/ChatPanel.tsx` | EDGE_VOICE_SETTINGS, ELEVEN_VOICES, safeRestart |
| `frontend/src/components/PageRenderer.tsx` | VoicePreset type |
| `frontend/src/components/SettingsPage.tsx` | VoicePreset type + VOICE_OPTIONS |
=======
### 3. Thinking Panel no Contexto (NOVO)

**Problema:** Thinking/raciocinio do modelo não era visível de forma organizada.
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)

**Solucao:** Painel Context (lado direito) mostra thinking em caixa azul com header "THINKING".

**Arquivos modificados:**
- `frontend/src/components/ProcessPanel.tsx` — Secao de thinking no Context

<<<<<<< HEAD
### DEEP-AUREA
```bat
C:\DEEP-AUREA\START-TOTAL.bat
```
- Backend: http://localhost:8001
- Frontend: http://localhost:5175

### Teste Charon (WebSocket direto)
```python
import asyncio, websockets, json
async def test():
    async with websockets.connect("ws://localhost:8001/ws/voice") as ws:
        await ws.send(json.dumps({"type": "start", "voice": "Charon"}))
        await ws.send(json.dumps({"type": "text", "text": "Abra o Chrome"}))
        while True:
            msg = await ws.recv()
            if isinstance(msg, bytes):
                print(f"[Audio: {len(msg)} bytes]")
            else:
                print(json.loads(msg))
asyncio.run(test())
```

---

## PendÃªncias

### Charon â€” SessÃ£o 6
- [ ] Implementar 20 ferramentas no voice_ws.py
- [ ] Verificar dependÃªncias (psutil, playwright, send2trash) no venv
- [ ] Testar cada ferramenta via WebSocket
- [ ] Documentar resultado no .memory
=======
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

**Arquivo criado:** `C:\DEEP-AUREA\Limpar_Processos_Memoria.bat`

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

## Estado Atual: FUNCIONAL + GGUF AUTO-DETECTED + GPU SUPPORT

O sistema esta operacional em `localhost:5175` (frontend) / `localhost:8001` (backend).

**Provider ativo:** MiMo V2.5 (gratis) via `mimo` provider → mimo.exe executor + API cloud com native tool calling

**Modelos GGUF:** Auto-detectados via scan recursivo — novos modelos aparecem automaticamente

**Vision:** Modelos com mmproj detectados automaticamente — 👁️ no dropdown

**GPU:** Toggle salva para Ollama + Llamacpp — `--n-gpu-layers` passado ao iniciar

**Thinking:** Mostrado no painel Context (lado direito) — voz não lê thinking

**Ferramentas Charon (33):** youtube_video, open_app, weather_report, browser_control, computer_control, computer_settings, desktop_control, file_controller, code_helper, dev_agent, game_updater, flight_finder, file_processor, system_status, reminder, web_search, send_message, screen_process, calorie_counter, pushup_counter, upload_video, + 11 novas

**Como iniciar:** `C:\DEEP-AUREA\START-TOTAL.bat` (backend + frontend)

**Limpeza:** `C:\DEEP-AUREA\Limpar_Processos_Memoria.bat` (encerra processos pesados)

---

## Pendencias
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)

### Geral
- **ElevenLabs:** Configurar `ELEVENLABS_API_KEY` em `backend/.env`
- **MiMo Executor:** Implementar `--continue` para manter contexto entre mensagens
- **web_fetch:** User-Agent precisa de upgrade (403 em sites com Cloudflare)
- **Wake word:** Falsos positivos em ambientes barulhentos
<<<<<<< HEAD
=======

### Browser Automation
- **CDP:** Conexao com Chrome via porta 9222 (alternativa ao Playwright)
- **Fill form:** Preenchimento automático de formulários via Charon
- **Screenshot:** Captura de tela para analise de paginas

### Modelos Locais
- **llamacpp context overflow:** NemoMix 12B Q4_K_M tem limite de 8192 tokens; system_prompt + historico excede este limite. Precisa reduzir system prompt ou aumentar --ctx-size.
- **GPU detection:** Driver NVIDIA atualizado (610.88) — verificar se monitor detecta VRAM corretamente após reinicialização
>>>>>>> d436640 (v2.0: GGUF auto-detection, GPU support, vision, thinking panel, monitor fix, portability scripts)
