# DEEP-AUREA - Guia de Licenciamento

## Como Funciona

1. **Gere uma chave** para cada cliente
2. **O cliente** configura a chave no `.env`
3. **O sistema** valida a chave ao iniciar
4. **Sem chave válida**, funcionalidades são limitadas

## Geração de Chaves

```python
from backend.core.license import generate_license_key

# Gera chave para 30 dias
key = generate_license_key("cliente-001", days=30)
print(key)  # Ex: a1b2c3d4e5f6...
```

## Configuração do Cliente

No arquivo `backend/.env` do cliente:
```
DEEP_AUREA_LICENSE=a1b2c3d4e5f6...
```

## Validação

```bash
# Verifica licença via API
curl http://localhost:8001/api/license
```

## Painel Administrativo (futuro)

Para gerenciar licenças, crie um endpoint admin:
- Listar clientes
- Gerar chaves
- Revogar licenças
- Monitorar uso
