# Instrucoes de Uso — DEEP-AUREA

> Como interagir com o sistema de agentes

---

## Sumario

1. [Comandos de Barra](#1-comandos-de-barra)
2. [Comandos de Voz](#2-comandos-de-voz)
3. [Comandos de Voz - Midia](#3-comandos-de-voz---midia)
4. [Ferramentas do Agente](#4-ferramentas-do-agente)
5. [Menções (@)](#5-mencoes)
6. [Confirmações de Risco](#6-confirmacoes-de-risco)
7. [Checklist Visual](#7-checklist-visual)
8. [MEDIA Player](#8-media-player)
9. [Monitor](#9-monitor)
10. [Lifecycle Engine](#10-lifecycle-engine)
11. [FAQ](#11-faq)

---

## 1. Comandos de Barra

Atalhos rapidos que disparam acoes especificas. Digite `/` seguido do comando no chat.

| Comando | Descricao | Exemplo |
|---------|-----------|---------|
| `/goal <texto>` | Define um objetivo | `/goal Criar uma API REST` |
| `/run <comando>` | Executa comando no terminal | `/run python main.py` |
| `/clear` | Limpa contexto da conversa | `/clear` |
| `/status` | Exibe status do sistema | `/status` |
| `/stop` | Para execucao atual | `/stop` |
| `/help` | Lista todos os comandos | `/help` |
| `/review` | Revisao de codigo | `/review` |
| `/build` | Build do projeto | `/build` |
| `/test` | Executa testes | `/test` |
| `/deploy` | Deploy da aplicacao | `/deploy` |
| `/logs` | Exibe logs do sistema | `/logs` |
| `/cancel` | Cancela tarefa | `/cancel` |

### Regras

- Um comando por mensagem
- Case-insensitive (`/GOAL` = `/goal`)
- Pode ser digitado ou dito por voz

---

## 2. Comandos de Voz

Diga qualquer um destes comandos enquanto o microfone estiver ativo (botao ou checkbox "auto").

### Gerais

| Comando de Voz | Acao |
|----------------|------|
| "novo contexto" / "limpar contexto" / "limpa tudo" | Limpa a conversa |
| "parar" / "cancelar" | Interrompe execucao |
| "ajuda" / "help" | Mostra esta ajuda |
| "status" | Ver status do sistema |

### Como usar

1. Clique no botao de microfone ou ative o checkbox "auto"
2. Fale o comando claramente
3. Aguarde 5 segundos para envio automatico (quando "auto" esta ativo)
4. Ou clique no botao de envio para enviar imediatamente

---

## 3. Comandos de Voz - Midia

Controle o player de midia integrado por voz.

| Comando de Voz | Acao |
|----------------|------|
| "pausa" / "pausar musica" | Pausa reproducao |
| "retomar" / "tocar musica" | Continua reproducao |
| "proxima musica" | Proxima faixa |
| "musica anterior" | Faixa anterior |
| "parar musica" / "fechar musica" | Para e fecha midia |
| "tocar no media" / "player interno" | Abre no player interno MEDIA |
| "tocar no windows media" / "tocar no windows" | Abre no Windows Media Player |
| "tocar no sistema" | Abre no player padrao do Windows |
| "fechar arquivo" | Fecha arquivo aberto |
| "fechar video" | Fecha video reproduzindo |
| "fechar tudo" | Fecha todos os arquivos |

---

## 4. Ferramentas do Agente

O agente tem acesso a ferramentas nativas de tool calling. Ele as usa automaticamente conforme a tarefa.

| Ferramenta | Parametros | Descricao |
|------------|------------|-----------|
| `explorer(path, root)` | path: subpasta | Lista pastas e arquivos |
| `read(path, root)` | path: caminho | Le conteudo de arquivo |
| `write(path, content, root)` | path, content | Cria/edita arquivo |
| `bash(command, workdir)` | command: comando | Executa comando no terminal |
| `delete(path, root)` | path | Deleta arquivo/pasta |
| `rename(old_path, new_path)` | old, new | Renomeia arquivo |
| `create_directory(path, root)` | path | Cria pasta |
| `search(pattern, path)` | pattern: texto | Busca texto em arquivos |
| `glob(pattern)` | pattern: glob | Busca arquivos por padrao |
| `file_edit(path, old_string, new_string)` | path, old, new | Edita com find-replace |
| `execute_python(code)` | code: codigo | Executa Python |
| `web_search(query)` | query | Pesquisa na internet |
| `web_fetch(url)` | url | Baixa conteudo de URL |
| `media_play(name, path, isVideo)` | name, path | Abre midia no player interno |
| `close_app(process_name, file_path)` | process ou path | Fecha processo/arquivo |
| `memory_write(namespace, key, content)` | ns, key, content | Salva na memoria |
| `memory_read(namespace, key)` | ns, key | Le da memoria |
| `fork_subagent(task)` | task: descricao | Cria subagente |
| `task_create(subject)` | subject: titulo | Cria tarefa |

### Interceptacao automatica

Quando o modelo tenta usar `bash(start "musica.mp3")`, o sistema converte automaticamente para `media_play` e abre no player interno.

---

## 5. Mencoes

Referenciam agentes especializados.

| Mencao | Agente | Descricao |
|--------|--------|-----------|
| `@general` | Assistente geral | Full-stack |
| `@coder` | Programador | Especialista em implementacao |
| `@architect` | Arquiteto | Arquiteto de software |
| `@debugger` | Debugging | Especialista em erros |
| `@writer` | Escritor | Documentacao tecnica |
| `@planner` | Planejador | Planejamento de tarefas |
| `@reviewer` | Revisor | Revisao de codigo |
| `@helper` | Assistente | Geral prestativo |
| `@analyst` | Analista | Analise de dados |

---

## 6. Confirmacoes de Risco

Mecanismo de protecao contra operacoes destrutivas.

### Niveis de Risco

| Nivel | Cor | Criterio | Exemplos |
|-------|-----|----------|----------|
| Low | Verde | Segura | Criar arquivo, ler arquivo |
| Medium | Amarelo | Impacto moderado | Editar config |
| High | Laranja | Impacto significativo | Mover diretorio |
| Critical | Vermelho | Irreversivel | Deletar arquivos |

### Como Funciona

1. Agente detecta operacao de risco
2. Execucao e interrompida
3. Action Card e gerado no chat
4. Usuario escolhe: Allow once / Allow always / Reject

---

## 7. Checklist Visual

Acompanhamento de progresso em tempo real com estilo terminal laranja.

### O que aparece

- **PLANO DE EXECUCAO** com barra de progresso
- Checkboxes: `[ ]` pendente, `[~]` executando, `[x]` concluido, `[!]` erro
- **Apenas o passo em execucao fica em laranja**
- Outros passos ficam neutros (cinza/verde/vermelho)

### Como funciona

1. Usuario envia tarefa
2. Agente apresenta raciocinio + checkboxes
3. Cada passo e executado com ferramentas
4. Status atualizado em tempo real
5. Barra de progresso avanca automaticamente

---

## 8. MEDIA Player

Player de midia integrado no topo do painel.

### Funcionalidades

- **Botao +**: Adiciona arquivos de audio/mp4 do computador
- **Controles**: Anterior, Play/Pause, Proximo
- **Barra de progresso**: Arraste para avancar/retroceder
- **Volume**: Controle deslizante
- **Lista de musicas**: Clique no nome para ver playlist
- **Tamanhos de video**: XS, SM, MD, LG

### Como adicionar musicas

1. Clique no **+** ao lado de "MEDIA"
2. Selecione arquivos de audio (mp3, wav, ogg, flac) ou video (mp4, avi, mkv)
3. A musica aparece na barra e comeca a tocar

### Como usar por voz

Diga "tocar no media" e o agente abre a musica no player interno.

---

## 9. Monitor

Painel no topo central com metricas do sistema.

### Metricas

- **CPU**: Percentual de uso com barra de progresso
- **RAM**: Memoria usada / total com barra
- **VRAM (GPU)**: Memoria da GPU com barra

### Cores das barras

- Verde: Uso normal
- Vermelho: Uso alto (>85%)

---

## 10. Lifecycle Engine

Maquina de estados que orquestra o ciclo de vida do agente.

### Estados

```
CALL_MODEL -> CHECK_RESPONSE -> CLASSIFY_FINISH
  -> tool_calls -> VALIDATE_TOOL -> EXECUTE_TOOL -> APPEND_OBSERVATION -> CALL_MODEL
  -> stop -> CLASSIFY_CONTENT -> FINAL
  -> length -> TRUNCATED
```

### Protecao contra Loops

| Mecanismo | Limite | Acao |
|-----------|--------|------|
| Tools seguidas | 10 | Forca resposta final |
| Bash repetido | 2x | Bloqueia e pede alternativa |
| Think-only | 3 loops | Encerra com FAILED |
| Max steps | 100 | Salva estado e pede continue |

### Continue

Se o limite for atingido, digite "continue" para retomar.

---

## 11. FAQ

### O agente nao executa tools, so escreve texto
Verifique se o provider/modelo suporta tool calling. MiMo V2.5 e Gemini 1.5 suportam. Para modelos que nao suportam, o sistema usa fallback de extracao de texto.

### A musica abre no Windows Media Player em vez do MEDIA interno
Diga "tocar no media" ou "player interno" por voz. Ou clique em "Player Interno (MEDIA)" quando o popup aparecer.

### O checkbox de execucao nao aparece
O modelo precisa gerar o JSON task_plan ou ter checkboxes no texto. Alguns modelos geram apenas texto sem o JSON.

### O auto-send nao funciona
Verifique se o checkbox "auto" esta marcado. O microfone deve estar ativo. Aguarde 5 segundos apos falar.

### O terminal nao conecta
Verifique se o backend esta rodando na porta 8001. Execute `npm run dev:backend` para iniciar.

### Como fechar um arquivo por voz
Diga "fechar arquivo", "fechar musica", "fechar video" ou "fechar tudo".

---

## Documentos Relacionados

| Documento | Descricao |
|-----------|-----------|
| AGENTS.md | Arquitetura do sistema |
| config.yaml | Configuracoes centrais |
| backend/ | Codigo do servidor Python |
| frontend/ | Codigo do frontend React |

---

> **DEEP-AUREA v2.2** — Instrucoes de uso consolidadas
> Atualizado em: 05/07/2026
