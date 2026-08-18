# Script de Deploy - Hostinger VPS

## Como Usar

### Antes de Executar

1. **Compre o VPS** na Hostinger (KVM 2 recomendado)
2. **Compre o domínio** na Hostinger
3. **Configure o DNS** apontando para o IP do VPS

### Configuração Inicial

Abra o arquivo `deploy-hostinger.sh` e preencha:

```bash
DOMAIN="seu-dominio.com.br"      # Seu domínio
EMAIL="seu@email.com"            # Para SSL
GROQ_KEY="gsk_..."               # Chave Groq (opcional)
GEMINI_KEY="AIza..."             # Chave Gemini (opcional)
OPENAI_KEY="sk-..."              # Chave OpenAI (opcional)
LICENSE_KEY="sua-chave"          # Licença (opcional)
```

### Executar o Script

#### Opção 1: Colar no Terminal

1. Conecte ao VPS:
```bash
ssh root@SEU_IP
```

2. Cole o script completo no terminal

3. Responda `s` quando perguntar se deseja executar

#### Opção 2: Upload e Executar

1. Faça upload do script para o VPS:
```bash
scp deploy-hostinger.sh root@SEU_IP:/root/
```

2. Conecte ao VPS:
```bash
ssh root@SEU_IP
```

3. Execute:
```bash
chmod +x deploy-hostinger.sh
./deploy-hostinger.sh
```

### O que o Script Faz

| Passo | Ação |
|-------|------|
| 1 | Atualiza o sistema Ubuntu |
| 2 | Instala Docker + Docker Compose |
| 3 | Instala NGINX + Certbot |
| 4 | Baixa o DEEP-AUREA do GitHub |
| 5 | Configura as chaves de API |
| 6 | Faz build dos containers |
| 7 | Configura NGINX (proxy reverso) |
| 8 | Instala SSL grátis (Let's Encrypt) |
| 9 | Configura firewall |

### Comandos Úteis Após Deploy

```bash
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Reiniciar tudo
docker-compose restart

# Parar tudo
docker-compose down

# Atualizar o código
git pull
docker-compose up -d --build
```

### Troubleshooting

| Problema | Solução |
|----------|---------|
| "Cannot connect" | `docker-compose restart` |
| "502 Bad Gateway" | `docker-compose logs backend` |
| "SSL error" | `certbot renew --force-renewal` |
| "Port already in use" | `netstat -tlnp | grep :8001` |

### Estrutura após Deploy

```
/root/deep-aurea/
├── backend/
│   ├── .env              # Chaves de API
│   ├── main.py           # Backend FastAPI
│   └── ...
├── frontend/
│   ├── src/              # Interface React
│   └── ...
├── config.yaml           # Configurações
├── docker-compose.yml    # Containers
└── data/                 # Banco de dados
```

### IPs e Portas

| Serviço | Porta | URL |
|---------|-------|-----|
| Frontend | 5175 | https://dominio.com |
| Backend | 8001 | https://dominio.com/api |
| WebSocket | 8001 | wss://dominio.com/ws |
| SSH | 22 | ssh root@IP |
| HTTP | 80 | Redireciona para HTTPS |
| HTTPS | 443 | Acesso principal |

### Backup

```bash
# Backup do banco de dados
cp data/interactions.db data/backup_$(date +%Y%m%d).db

# Backup completo
tar -czf backup_$(date +%Y%m%d).tar.gz data/ config.yaml backend/.env
```

### Segurança

- ✅ SSL ativo (HTTPS)
- ✅ Firewall configurado
- ✅ Rate limiting
- ✅ Senhas hasheadas
- ✅ API keys no .env (não no código)

### Suporte

Em caso de problemas:
1. Verifique os logs: `docker-compose logs -f`
2. Verifique o status: `docker-compose ps`
3. Reinicie: `docker-compose restart`
