import os

# Define o arquivo que você está utilizando (ajuste o caminho se necessário)
caminho_arquivo = 'config.yaml' # Altere para o nome real do seu arquivo

# Verifica se o arquivo existe antes de continuar
if os.path.exists(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='utf-8') as file:
        conteudo = file.read()
    
    # Substitui o modelo
    novo_conteudo = conteudo.replace('qwen2.5-coder:14b', 'qwen3.5:9b')
    
    # Salva o arquivo atualizado
    with open(caminho_arquivo, 'w', encoding='utf-8') as file:
        file.write(novo_conteudo)
    
    print("Substituição concluída com sucesso!")
else:
    print(f"Arquivo '{caminho_arquivo}' não encontrado. Verifique o nome.")
