from pydantic import BaseModel


class Message(BaseModel):
    user: str
    provider: str = "openclaude"
    model: str = "deepseek-v4-flash"
    mood: str = "serio"
    temperature: float = 0.7
    system_prompt: str = ""
    root: str = ""      # Diretório raiz configurado no explorador
    path: str = ""      # Subpasta atual no explorador
    api_key: str = ""   # API key do provider (ex: opencode)
    max_steps: int = 0  # 0 = usa o padrao do backend (100)
    task_id: str = ""   # Para continuar uma tarefa anterior
    tool_confirmed: bool = False  # True quando usuario aprovou ferramenta destrutiva
    images: list[str] = []  # Imagens em base64 para modelos de visao
    session_id: str = ""  # ID da sessao para fila de mensagens

class BrainArtifact(BaseModel):
    title: str
    description: str = ""
    plan: list = []
    status: str = "pending"
    files: list = []
    result: str = ""

class AgentTask(BaseModel):
    task: str
    provider: str = "openclaude"
    model: str = "deepseek-v4-flash"
    temperature: float = 0.3
    agent_type: str = "auto"

class ToolRead(BaseModel):
    path: str
    root: str = ""

class ToolWrite(BaseModel):
    path: str
    content: str
    root: str = ""

class ToolBash(BaseModel):
    command: str
    workdir: str = ""

class KnowledgePayload(BaseModel):
    texto: str

class MemoryPayload(BaseModel):
    key: str
    content: str
    namespace: str = "conversations"
