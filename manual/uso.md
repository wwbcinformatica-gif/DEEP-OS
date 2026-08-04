# DEEP-AUREA - Manual de Uso

**Versao:** 2.2  
**Plataforma:** Windows (portatil)  
**Stack:** Python FastAPI + React/Vite

---

## 1. O que e o DEEP-AUREA

DEEP-AUREA e um **Sistema Operacional de Agentes de IA** que orquestra multiplos agentes de inteligencia artificial para automatizar tarefas de engenharia de software. Executa 100% localmente com suporte a multiplos provedores de LLM.

### Principais funcionalidades

- Chat com IA multi-provedor (8+ provedores)
- 20+ agentes especializados (@coder, @debugger, @architect, etc.)
- Ferramentas reais de desenvolvimento (ler/escrever arquivos, terminal, busca)
- Memoria de longo prazo (vetorial + espiral)
- Interface web completa com streaming
- Sistema de plugins MCP
- Lifecycle engine com protecao contra loops

---

## 2. Estrutura do Projeto

```
C:\DEEP-AUREA\
├── backend/              # Python FastAPI (porta 8001)
│   ├── .env              # Chaves de API (NAO versionar)
│   ├── .env.example      # Template de chaves
│   ├── requirements.txt  # Dependencias Python
│   ├── main.py           # Ponto de entrada
│   ├── core/             # Modulos centrais
│   ├── routes/           # Endpoints da API
│   ├── agents/           # Loop dos agentes
│   ├── tools/            # Ferramentas disponiveis
│   ├── memory/           # Sistema de memoria
│   ├── database/         # SQLite (data/interactions.db)
│   ├── data/             # Dados persistentes
│   └── logs/             # Logs do servidor
├── frontend/             # React + Vite (porta 5175)
│   ├── src/              # Codigo fonte
│   └── package.json      # Dependencias Node.js
├── config.yaml           # Configuracao principal
├── START-TOTAL.bat       # Inicia tudo
├── STOP-TOTAL.bat        # Para tudo
├── mimo.bat              # Inicia MiMo Code
└── manual/               # Esta documentacao
```

---

## 3. Instalacao

### Pre-requisitos

- **Node.js** (v18+) com npm
- **Python** (3.11+) com pip
- **Git** (opcional, para versionamento)

### Passo a passo

```bash
# 1. Entrar na pasta do projeto
cd C:\DEEP-AUREA

# 2. Instalar dependencias do frontend
cd frontend
npm install
cd ..

# 3. Criar ambiente virtual Python
python -m venv venv
venv\Scripts\activate

# 4. Instalar dependencias do backend
pip install -r backend\requirements.txt

# 5. Configurar chaves de API
copy backend\.env.example backend\.env
# Edite backend\.env e preencha as chaves desejadas

# 6. Iniciar o sistema
START-TOTAL.bat
```

### Acessos apos instalacao

| Servico   | URL                       |
|-----------|---------------------------|
| Frontend  | http://localhost:5175      |
| Backend   | http://localhost:8001      |
| API Docs  | http://localhost:8001/docs |

---

## 4. Configuracao de Provedores de IA

Edite o arquivo `backend\.env` com as chaves dos provedores que deseja usar:

```env
# Gratuito (recomendado para comecar)
GROQ_API_KEY=gsk_...
MIMO_API_KEY=sk-...

# Pagos
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
OPENROUTER_API_KEY=sk-or-...
```

### Provedores disponiveis

| Provedor   | Custo    | Modelos Principais           | Tool Calling |
|------------|----------|------------------------------|--------------|
| Groq       | Gratuito | Llama 3.3 70B, Mixtral       | Sim          |
| MiMo       | Gratuito | MiMo V2.5                    | Nao*         |
| Ollama     | Gratuito | Qwen, DeepSeek, Gemma (local)| Sim          |
| OpenAI     | Pago     | GPT-4o, GPT-4 Turbo          | Sim          |
| Gemini     | Pago     | Gemini 1.5 Pro/Flash         | Sim          |
| OpenRouter | Pago     | Claude, Llama, etc.           | Sim          |
| OpenClaude | Pago     | Claude Sonnet                 | Sim          |
| OpenCode   | Pago     | DeepSeek V4, Nemotron        | Nao          |

> *MiMo V2.5 nao suporta tool calling nativo. O sistema envia respostas em texto plano.

### Como usar Ollama (modelos locais)

```bash
# 1. Instalar Ollama
# Baixe em https://ollama.com

# 2. Baixar um modelo
ollama pull qwen3:8b

# 3. No frontend, selecione "ollama" como provedor e o modelo desejado
```

---

## 5. Como Usar o Chat

### Interface

A interface tem 3 paineis principais:
- **Explorer** (esquerda): Navegador de arquivos
- **Chat** (centro): Conversa com o agente
- **Terminal** (baixo): Terminal web integrado

### Comandos de chat

| Comando    | Descricao                          |
|------------|------------------------------------|
| `/goal`    | Definir objetivo de longo prazo    |
| `/clear`   | Limpar contexto da conversa        |
| `/status`  | Ver status do sistema              |
| `/help`    | Lista todos os comandos            |
| `/stop`    | Interromper execucao atual         |
| `/run`     | Executar comando no terminal       |

### Uso de agentes (@mentions)

Digite `@` no chat para ver agentes disponiveis:

- `@coder` - Programador especialista
- `@debugger` - Especialista em debugging
- `@architect` - Arquiteto de software
- `@planner` - Planejador de tarefas
- `@reviewer` - Revisor de codigo

### Exemplos de uso

```
# Criar um arquivo
"crie um arquivo main.py com uma API FastAPI basica"

# Explorar o projeto
"liste os arquivos da pasta backend"

# Executar comando
"execute pytest para rodar os testes"

# Analisar codigo
"analise o arquivo backend/routes/chat.py e sugira melhorias"
```

---

## 6. Ferramentas Disponiveis

O agente tem acesso a ferramentas reais via tool calling:

| Ferramenta         | Descricao                          |
|--------------------|------------------------------------|
| `read`             | Ler conteudo de arquivos           |
| `write`            | Criar/sobrescrever arquivos        |
| `bash`             | Executar comandos no terminal      |
| `explorer`         | Listar diretorios                  |
| `search`           | Buscar texto em arquivos           |
| `glob`             | Buscar arquivos por padrao         |
| `web_search`       | Pesquisar na internet              |
| `web_fetch`        | Buscar conteudo de URLs            |
| `file_edit`        | Editar trechos de arquivos         |
| `delete`           | Deletar arquivos/pastas            |
| `rename`           | Renomear arquivos/pastas           |
| `create_directory` | Criar pastas                       |
| `memory_write`     | Salvar na memoria de longo prazo   |
| `memory_read`      | Ler da memoria de longo prazo      |
| `monitor_dashboard`| Ver uso de CPU/RAM                 |

### Protecao contra operacoes de risco

O sistema pede confirmacao para operacoes perigosas:
- Deletar arquivos/pastas criticos
- Comandos bash de alto risco (rm -rf, etc.)
- Renomear arquivos

---

## 7. Sistema de Memoria

### Memoria de longo prazo

O agente lembra de conversas anteriores automaticamente. A memoria e organizada em namespaces:

- `conversations` - Historico de conversas
- `project_knowledge` - Conhecimento sobre o projeto
- `reflections` - Reflexoes do agente
- `preferences` - Preferencias do usuario

### Memoria espiral (Deep-Aurea)

Sistema avancado com dois modelos:
- **Modelo A (Worker)**: Executa ferramentas
- **Modelo B (Keeper)**: Monitora e refresca o contexto

Configuracao em `config.yaml`:

```yaml
spiral_memory:
  enabled: true
  interval: 4
  keeper_provider: "ollama"
  keeper_model: "deepseek-r1:7b"
```

---

## 8. Configuracao

### Arquivo config.yaml

Configuracoes principais do sistema:

```yaml
agent:
  max_tool_steps: 100      # Maximo de passos por tarefa
  max_turns: 25            # Maximo de turnos
  personality: jarvis      # Personalidade do agente
  image_input_mode: image  # Modo de entrada de imagens

server:
  hostname: 0.0.0.0
  port: 8000

display:
  accent_theme: dark       # Tema visual
  language: pt-BR          # Idioma
  streaming: true          # Streaming de respostas

spiral_memory:
  enabled: true
  interval: 4
  keeper_provider: "ollama"
  keeper_model: "deepseek-r1:7b"
```

### Temas visuais

Temas de accent disponiveis no frontend:
- Laranja, Maracuja, Verde Palha
- Azul Claro (padrao), Dourado Claro
- Grafite, Dark

---

## 9. Portabilidade

O projeto e **totalmente portatil** - basta copiar a pasta inteira para outra maquina Windows.

### Checklist de portabilidade

- [x] `requirements.txt` com todas as dependencias Python
- [x] `package.json` com todas as dependencias Node.js
- [x] `backend/.env.example` com template de chaves
- [x] `config.yaml` com configuracoes padrao
- [x] `START-TOTAL.bat` para inicializar tudo
- [x] `STOP-TOTAL.bat` para parar tudo
- [x] Scripts de banco criados automaticamente (SQLite)
- [x] Diretorios de dados criados automaticamente

### Em outra maquina

```bash
# 1. Copiar a pasta C:\DEEP-AUREA inteira

# 2. Instalar Node.js e Python (se nao tiver)

# 3. Instalar dependencias
cd C:\DEEP-AUREA\frontend && npm install
cd C:\DEEP-AUREA
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt

# 4. Configurar chaves de API
copy backend\.env.example backend\.env
# Editar backend\.env

# 5. Iniciar
START-TOTAL.bat
```

---

## 10. Solucao de Problemas

### Backend nao inicia

```
# Verificar se as dependencias estao instaladas
pip install -r backend\requirements.txt

# Verificar se o arquivo .env existe
dir backend\.env

# Verificar logs
type backend\logs\wbc-backend.log
```

### Frontend nao conecta ao backend

```
# Verificar se o backend esta rodando
curl http://localhost:8001/status

# Verificar porta no vite.config.ts
# Deve ser 5175 com proxy para 8001
```

### Modelo nao responde / Erro de tool calling

O MiMo V2.5 e OpenCode nao suportam tool calling. O sistema automaticamente:
1. Nao envia tools para esses modelos
2. Modifica o prompt para respostas em texto

### Erro 401 (Autenticacao)

Verifique se a chave de API esta correta em `backend/.env`.

---

## 11. Comandos de Inicializacao

| Comando           | Descricao                          |
|-------------------|------------------------------------|
| `START-TOTAL.bat` | Inicia backend + frontend          |
| `STOP-TOTAL.bat`  | Para todos os processos            |
| `mimo.bat`        | Inicia MiMo Code (editor)          |
| `npm run dev`     | Inicia ambos (via npm)             |
| `npm run dev:backend`  | Inicia so o backend           |
| `npm run dev:frontend` | Inicia so o frontend          |

---

## 12. API Endpoints Principais

| Endpoint             | Metodo | Descricao                    |
|----------------------|--------|------------------------------|
| `/chat/stream`       | POST   | Chat com streaming           |
| `/chat`              | POST   | Chat sem streaming           |
| `/explorer`          | GET    | Listar diretorio             |
| `/explorer/read`     | GET    | Ler arquivo                  |
| `/explorer/write`    | POST   | Escrever arquivo             |
| `/terminal`          | POST   | Executar comando             |
| `/ws/terminal`       | WS     | Terminal via WebSocket       |
| `/history`           | GET    | Historico de conversas       |
| `/ollama/status`     | GET    | Status do Ollama             |
| `/memory`            | GET    | Memoria de longo prazo       |
| `/status`            | GET    | Status geral do sistema      |
| `/health`            | GET    | Healthcheck                  |

---

## 13. Informacoes Tecnicas

- **Backend:** Python 3.11+ / FastAPI / Uvicorn
- **Frontend:** React 18 / TypeScript / Vite
- **Banco:** SQLite (data/interactions.db)
- **Terminal:** WebSocket + PowerShell
- **Memoria:** SQLite + JSON + embeddings vetoriais
- **Portas:** Backend 8001, Frontend 5175

---

*Manual atualizado em: Julho 2026*  
*DEEP-AUREA v2.2*
