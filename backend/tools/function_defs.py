"""
DEEP-AUREA Tool Definitions
============================
OpenAI-compatible function definitions for tool-calling agents.
Can be filtered by toolset using ``get_tools_by_toolset()``.
"""

from tools.toolsets import filter_function_defs, resolve_multiple_toolsets

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": "Le o conteudo de um arquivo ou lista arquivos de um diretorio. Aceita paths absolutos (ex: G:\\DEEP-AUREA, C:\\Users) ou relativos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo ou diretorio. Aceita paths absolutos (G:\\pasta) ou relativos (backend/core)"},
                    "root": {"type": "string", "description": "Diretorio raiz do projeto (opcional)"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "Cria ou sobrescreve um arquivo com conteudo. Aceita paths absolutos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo. Aceita paths absolutos (G:\\pasta\\arquivo.py)"},
                    "content": {"type": "string", "description": "Conteudo do arquivo"},
                    "root": {"type": "string", "description": "Diretorio raiz do projeto (opcional)"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Executa um comando no terminal do sistema. Tem acesso TOTAL a todas as unidades (C:\\, D:\\, G:\\, etc).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Comando a ser executado (ex: dir G:\\, ls C:\\Users)"},
                    "workdir": {"type": "string", "description": "Diretorio de trabalho (opcional)"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "explorer",
            "description": "Lista o conteudo de um diretorio. Aceita paths absolutos (ex: G:\\, C:\\Users\\Desktop).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho absoluto (G:\\pasta) ou subpasta relativa"},
                    "root": {"type": "string", "description": "Diretorio raiz (opcional)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Busca um padrao de texto em arquivos do projeto",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Texto ou regex para buscar"},
                    "path": {"type": "string", "description": "Diretorio onde buscar (opcional)"},
                    "include": {"type": "string", "description": "Filtro de extensao ex: *.py (opcional)"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Executa codigo Python em ambiente isolado",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Codigo Python para executar"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Cria uma ou mais pastas",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho da pasta a criar"},
                    "root": {"type": "string", "description": "Diretorio raiz do projeto (opcional)"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete",
            "description": "Deleta um arquivo ou pasta",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo ou pasta"},
                    "root": {"type": "string", "description": "Diretorio raiz do projeto (opcional)"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename",
            "description": "Renomeia ou move um arquivo ou pasta",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_path": {"type": "string", "description": "Caminho atual"},
                    "new_path": {"type": "string", "description": "Novo caminho"},
                    "root": {"type": "string", "description": "Diretorio raiz do projeto (opcional)"}
                },
                "required": ["old_path", "new_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_mcp_servers",
            "description": "Lista todos os servidores MCP do OpenClaude ativos e suas ferramentas disponiveis",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "init_mcp_plugin",
            "description": "Inicializa um plugin MCP do OpenClaude pelo nome (ex: github, discord, telegram). Apos iniciar, as ferramentas do plugin ficam disponiveis automaticamente com o formato plugin__nomeDaFerramenta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome do plugin MCP (ex: github, discord, telegram, fakechat)"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Abre um programa ou executavel no sistema. Procura em Program Files, AppData, PATH e Start Menu. Use quando o usuario pedir para abrir qualquer programa (ex: 'abra o Chrome', 'abra o Spotify', 'abra calculadora').",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Nome do programa (ex: chrome, spotify, notepad, calc, explorer)"},
                    "path": {"type": "string", "description": "Caminho completo do executavel (opcional, se souber)"},
                    "args": {"type": "string", "description": "Argumentos adicionais (opcional)"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_file",
            "description": "Procura arquivos em TODA a maquina por nome parcial. Use quando o usuario pedir para encontrar musicas, videos, documentos ou qualquer arquivo. Procura em todas as unidades (C:, D:, G:, etc).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome parcial do arquivo (ex: Jefferson, musica, .mp3, hino)"},
                    "pattern": {"type": "string", "description": "Padrao wildcard (ex: *.mp3, *Jefferson*)"},
                    "drive": {"type": "string", "description": "Unidade especifica (ex: C:, D:). Vazio = todas as unidades."}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_app",
            "description": "Fecha um processo ou arquivo aberto no sistema",
            "parameters": {
                "type": "object",
                "properties": {
                    "process_name": {"type": "string", "description": "Nome do processo (ex: notepad.exe)"},
                    "file_path": {"type": "string", "description": "Caminho do arquivo aberto para fechar"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "media_play",
            "description": "Abre um arquivo de midia no player interno do projeto",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome do arquivo de midia"},
                    "path": {"type": "string", "description": "Caminho completo do arquivo"},
                    "isVideo": {"type": "boolean", "description": "true para video, false para musica"}
                },
                "required": ["name", "path"]
            }
        }
    },

    # â”€â”€ Task Management â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "task_create",
            "description": "Cria uma nova tarefa no sistema de gerenciamento de tarefas",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Titulo da tarefa"},
                    "description": {"type": "string", "description": "Descricao detalhada da tarefa"},
                    "active_form": {"type": "string", "description": "Descricao no presente continuo (ex: 'Executando build')"}
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_get",
            "description": "Obtem o status e detalhes de uma tarefa pelo ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ID da tarefa"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_update",
            "description": "Atualiza o status ou metadados de uma tarefa",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ID da tarefa"},
                    "status": {"type": "string", "description": "Novo status: pending, running, completed, failed, killed"},
                    "output": {"type": "string", "description": "Texto de saida/resultado da tarefa"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_list",
            "description": "Lista todas as tarefas, opcionalmente filtradas por status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filtrar por status: pending, running, completed, failed (opcional)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_stop",
            "description": "Para/interrompe uma tarefa em execucao",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ID da tarefa a parar"}
                },
                "required": ["task_id"]
            }
        }
    },
    # â”€â”€ Web Search â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Busca informacoes na internet usando DuckDuckGo. Retorna titulos, URLs e snippets dos resultados.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termo de busca"}
                },
                "required": ["query"]
            }
        }
    },
    # â”€â”€ File Edit â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "file_edit",
            "description": "Edita um arquivo substituindo exatamente um trecho de texto por outro. A string antiga deve ser unica no arquivo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo"},
                    "old_string": {"type": "string", "description": "Texto exato a ser substituido (deve aparecer uma unica vez)"},
                    "new_string": {"type": "string", "description": "Novo texto"},
                    "root": {"type": "string", "description": "Diretorio raiz (opcional)"}
                },
                "required": ["path", "old_string", "new_string"]
            }
        }
    },
    # â”€â”€ Web Fetch â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Busca o conteudo de uma URL e retorna como texto markdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL completa para buscar"},
                    "prompt": {"type": "string", "description": "Instrucao opcional para processar o resultado"}
                },
                "required": ["url"]
            }
        }
    },
    # ── Document Reader ──────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "read_document",
            "description": "Le o conteudo de documentos: PDF, DOCX, XLSX, CSV, XML, TXT, PPTX e outros formatos. Retorna o texto extraido com metadados.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo (relativo ou absoluto)"},
                    "root": {"type": "string", "description": "Diretorio raiz do projeto (opcional)"}
                },
                "required": ["path"]
            }
        }
    },
    # ── Tool Search ─────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "tool_search",
            "description": "Busca ferramentas disponiveis pelo nome ou descricao. Use quando nao souber qual ferramenta usar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "O que voce quer fazer (ex: 'editar arquivo', 'buscar na web')"}
                },
                "required": ["query"]
            }
        }
    },
    # â”€â”€ Glob â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Busca arquivos por padrao glob (ex: **/*.py, src/**/*.tsx).",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Padrao glob para buscar arquivos"},
                    "path": {"type": "string", "description": "Diretorio base (opcional)"}
                },
                "required": ["pattern"]
            }
        }
    },
    # â”€â”€ Agent Forking â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "fork_subagent",
            "description": "Cria um subagente para executar uma tarefa especifica em paralelo. O subagente tem acesso limitado a ferramentas e roda de forma independente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Descricao detalhada da tarefa para o subagente"},
                    "system_prompt": {"type": "string", "description": "Instrucoes adicionais para o subagente (opcional)"}
                },
                "required": ["task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_subagent_result",
            "description": "Obtem o resultado de um subagente apos sua execucao.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subagent_id": {"type": "string", "description": "ID do subagente"}
                },
                "required": ["subagent_id"]
            }
        }
    },
    # â”€â”€ Agent Teams â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "team_create",
            "description": "Cria um time de agentes para coordenacao de tarefas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome do time"},
                    "members": {"type": "array", "items": {"type": "string"}, "description": "Lista de nomes dos membros (opcional)"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "team_delete",
            "description": "Deleta um time de agentes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string", "description": "ID do time"}
                },
                "required": ["team_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Envia uma mensagem para outro agente do time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Nome do agente destinatario"},
                    "message": {"type": "string", "description": "Conteudo da mensagem"}
                },
                "required": ["recipient", "message"]
            }
        }
    },
    # â”€â”€ Cron â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "cron_create",
            "description": "Agenda uma tarefa para execucao recorrente usando expressao cron.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Expressao cron de 5 campos (minuto hora dia mes dia-da-semana). Ex: '0 9 * * *' = todo dia as 9h"},
                    "task": {"type": "string", "description": "Descricao da tarefa a executar"}
                },
                "required": ["expression", "task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cron_delete",
            "description": "Remove um job cron agendado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "ID do job cron"}
                },
                "required": ["job_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cron_list",
            "description": "Lista todos os jobs cron ativos.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    # â”€â”€ Memory Tools â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        "type": "function",
        "function": {
            "name": "memory_write",
            "description": "Salva informacao na memoria de longo prazo do agente (namespace + chave + conteudo).",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace: conversations, project_knowledge, reflections, preferences"},
                    "key": {"type": "string", "description": "Chave unica para recuperacao"},
                    "content": {"type": "string", "description": "Conteudo a ser armazenado"}
                },
                "required": ["namespace", "key", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_read",
            "description": "Le informacao da memoria de longo prazo pelo namespace + chave.",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace: conversations, project_knowledge, reflections, preferences"},
                    "key": {"type": "string", "description": "Chave unica para leitura"}
                },
                "required": ["namespace", "key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_list",
            "description": "Lista todas as chaves salvas em um namespace de memoria.",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace: conversations, project_knowledge, reflections, preferences"}
                },
                "required": ["namespace"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_delete",
            "description": "Apaga uma entrada especifica da memoria de longo prazo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace: conversations, project_knowledge, reflections, preferences"},
                    "key": {"type": "string", "description": "Chave a ser removida"}
                },
                "required": ["namespace", "key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "monitor_dashboard",
            "description": "Coleta dados de CPU, RAM e ultimas linhas de log do servidor para o dashboard de monitoramento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "linhas_log": {"type": "integer", "description": "Quantidade de linhas de log para retornar (padrao 20)"}
                },
                "required": []
            }
        }
    },
]

# â”€â”€ Toolset Integration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def get_tools_by_toolset(toolset_names: list[str] | None = None) -> list[dict]:
    """Filter TOOLS by one or more toolset names.

    Args:
        toolset_names: List of toolset names (e.g. ``["developer"]``).
                       If None or empty, returns ALL tools.

    Returns:
        Filtered list of OpenAI function definitions.
    """
    if not toolset_names:
        return list(TOOLS)

    allowed = resolve_multiple_toolsets(toolset_names)
    return filter_function_defs(TOOLS, allowed)


def get_tools_by_name(tool_names: list[str]) -> list[dict]:
    """Filter TOOLS to only include specific named tools.

    Args:
        tool_names: List of exact tool function names.

    Returns:
        Filtered list matching only the requested tools.
    """
    allowed = set(tool_names)
    return [fd for fd in TOOLS if fd.get("function", {}).get("name") in allowed]


def get_all_tool_names() -> list[str]:
    """Return the name of every registered tool."""
    return [fd["function"]["name"] for fd in TOOLS if "function" in fd]


def build_tool_index() -> dict[str, str]:
    """Build a nameâ†’description index for tool_search."""
    return {
        fd["function"]["name"]: fd["function"]["description"]
        for fd in TOOLS
        if "function" in fd and "name" in fd["function"]
    }
