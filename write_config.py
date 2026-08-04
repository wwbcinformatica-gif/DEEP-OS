import sys

file_path = r'C:\WBC-ZERO-G 5.0\config.yaml'

new_content = """agent:
  image_input_mode: image
  max_tool_steps: 100
  max_turns: 25
  personality: jarvis
  system_prompt: "Ao iniciar toda conversa, OBRIGATORIAMENTE cumprimente o usuario com base no horario atual: Bom Dia! (ate 12h), Boa Tarde! (12h as 18h) ou Boa Noite! (a partir das 18h), e em seguida pergunte: Qual o seu nome?. Apos o usuario informar seu nome, Dirija-se sempre ao usuario usando o nome dele em todas as respostas. Responda sempre em portugues voce e um engenheiro senior tem todas as ferramentas necessarias e Modo de Operacao. Modo Desenvolvedor (Acesso total ao sistema) raiz principal deste projeto e ferramentas estao descritas aqui C:\\\\WBC-ZERO-G 5.0\\\\"
  toolset: agent
display:
  accent_theme: verde-palha
  compact: false
  language: pt-BR
  show_reasoning: true
  show_tool_calls: true
  streaming: true
server:
  hostname: 0.0.0.0
  port: 8000
terminal:
  allowed_commands:
  - ls
  - dir
  - cat
  - type
  - echo
  - pwd
  - cd
  - mkdir
  - copy
  - move
  - del
  - git
  - npm
  - node
  - python
  - pip
  - curl
  - find
  - grep
  - rg
  - ollama
  backend: powershell
  cwd: C:\\\\WBC-PDV 2.0
  timeout: 600
watcher:
  ignore:
  - node_modules/**
  - dist/**
  - .git/**
workspace:
  name: WBC-PDV 2.0
  root: C:\\\\WBC-PDV 2.0
workspaces:
- last_opened: ''
  name: WBC-ZERO-G 4.0
  path: C:\\\\WBC-ZERO-G 4.0
- last_opened: ''
  name: WBC-PDV
  path: C:\\\\WBC-PDV
- last_opened: ''
  name: CLAUDECODE
  path: C:\\\\CLAUDECODE
- last_opened: ''
  name: OPENCODE
  path: C:\\\\OPENCODE
- last_opened: ''
  name: WBC-PAD
  path: D:\\\\0-PROJETOS\\\\WBC-PAD
- last_opened: ''
  name: WBC-ZERO-G 5.0
  path: C:\\\\WBC-ZERO-G 5.0
- last_opened: ''
  name: WBC-PDV 2.0
  path: C:\\\\WBC-PDV 2.0
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Arquivo salvo com sucesso!")
