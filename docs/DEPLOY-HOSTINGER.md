# DEEP-AUREA - Deploy na Hostinger (Passo a Passo)

## O que Você Precisa

| Item | Onde Comprar | Preço |
|------|--------------|-------|
| **VPS KVM 2** | hostinger.com.br | ~R$35/mês |
| **Domínio** | hostinger.com.br | ~R$40/ano |

## Passo 1: Comprar o VPS na Hostinger

1. Acesse: https://hostinger.com.br/vps
2. Escolha o plano **VPS KVM 2** (recomendado)
   - 2 vCPU
   - 4 GB RAM
   - 50 GB SSD
   - 4 TB de tráfego
3. Escolha **Ubuntu 22.04** como sistema operacional
4. Anote o **IP**, **senha root** e **porta SSH**

## Passo 2: Conectar ao VPS

### No Windows (PowerShell):
```powershell
# Conecte ao VPS
ssh root@SEU_IP

# Digite a senha quando solicitado
```

### Ou use o PuTTY:
1. Baixe: https://putty.org
2. Host Name: `SEU_IP`
3. Port: `22`
4. Clique "Open"
5. Login: `root`
6. Senha: (a que você recebeu da Hostinger)

## Passo 3: Configurar o Servidor

Cole estes comandos **um por um** no terminal:

```bash
# 1. Atualize o sistema
apt update && apt upgrade -y

# 2. Instale Docker
curl -fsSL https://get.docker.com | sh

# 3. Adicione seu usuário ao docker
usermod -aG docker $USER

# 4. Instale Docker Compose
apt install docker-compose -y

# 5. Instale NGINX
apt install nginx -y

# 6. Instale Git
apt install git -y

# 7. Instale Certbot (para SSL grátis)
apt install certbot python3-certbot-nginx -y
```

## Passo 4: Baixar o DEEP-AUREA

```bash
# 1. Clone o repositório
git clone https://github.com/wwbcinformatica-gif/deep-aurea.git

# 2. Entre na pasta
cd deep-aurea

# 3. Configure as chaves de API
cp backend/.env.example backend/.env

# 4. Edite o arquivo .env
nano backend/.env
```

No arquivo `.env`, adicione suas chaves:

```env
# Chaves de API (use pelo menos uma)
GROQ_API_KEY=sua_chave_groq
GEMINI_API_KEY=sua_chave_gemini
OPENAI_API_KEY=sua_chave_openai

# Chave de licença (opcional)
DEEP_AUREA_LICENSE=sua_chave_licenca
```

Para salvar: `Ctrl + X`, depois `Y`, depois `Enter`

## Passo 5: Build e Iniciar

```bash
# 1. Build dos containers
docker-compose up -d --build

# 2. Verifique se está rodando
docker-compose ps

# 3. Veja os logs
docker-compose logs -f
```

## Passo 6: Configurar NGINX

```bash
# 1. Crie o arquivo de configuração
nano /etc/nginx/sites-available/deep-aurea
```

Cole esta configuração:

```nginx
server {
    listen 80;
    server_name seu-dominio.com.br www.seu-dominio.com.br;
    
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com.br www.seu-dominio.com.br;

    # SSL (será configurado depois pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com.br/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:5175;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket (Charon - voz)
    location /ws/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

Para salvar: `Ctrl + X`, depois `Y`, depois `Enter`

```bash
# 2. Ative o site
ln -s /etc/nginx/sites-available/deep-aurea /etc/nginx/sites-enabled/

# 3. Remova a configuração padrão
rm /etc/nginx/sites-enabled/default

# 4. Teste a configuração
nginx -t

# 5. Reinicie o NGINX
systemctl restart nginx
```

## Passo 7: Configurar Domínio

### Na Hostinger (painel):

1. Acesse: https://hpanel.hostinger.com
2. Vá em **Domínios** → **DNS Zone Editor**
3. Adicione estes registros:

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| A | @ | SEU_IP | 14400 |
| A | www | SEU_IP | 14400 |

**Substitua `SEU_IP` pelo IP do seu VPS**

## Passo 8: Instalar SSL Grátis

```bash
# 1. Pare o NGINX temporariamente
systemctl stop nginx

# 2. Instale o SSL
certbot certonly --standalone -d seu-dominio.com.br -d www.seu-dominio.com.br

# 3. Reinicie o NGINX
systemctl start nginx

# 4. Renovação automática
echo "0 0,12 * * * certbot renew --quiet" | crontab -
```

## Passo 9: Testar!

1. Abra o navegador
2. Acesse: `https://seu-dominio.com.br`
3. Você deve ver a tela de login do DEEP-AUREA

## Comandos Úteis

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

# Ver uso de recursos
docker stats
```

## Troubleshooting (Problemas Comuns)

### "Cannot connect to server"
```bash
# Verifique se os containers estão rodando
docker-compose ps

# Reinicie
docker-compose restart
```

### "502 Bad Gateway"
```bash
# Verifique se o backend está rodando
docker-compose logs backend

# Reinicie o backend
docker-compose restart backend
```

### "WebSocket connection failed"
```bash
# Verifique se a porta 8001 está aberta
netstat -tlnp | grep 8001

# Reinicie tudo
docker-compose down && docker-compose up -d
```

### "SSL certificate error"
```bash
# Reinstale o certificado
certbot renew --force-renewal
systemctl restart nginx
```

## Custos na Hostinger

| Item | Plano | Preço |
|------|-------|-------|
| VPS KVM 2 | Ubuntu 22.04 | ~R$35/mês |
| Domínio | .com.br | ~R$40/ano |
| **Total** | | ~R$38/mês |

## Recomendação de Plano

| Clientes | Plano Recomendado | Preço |
|----------|-------------------|-------|
| 1-10 | VPS KVM 2 | R$35/mês |
| 11-50 | VPS KVM 4 | R$70/mês |
| 51-100 | VPS KVM 8 | R$140/mês |

## Segurança Extra

```bash
# 1. Mude a porta SSH
nano /etc/ssh/sshd_config
# Mude: Port 22 para Port 2222
# Reinicie: systemctl restart sshd

# 2. Instale firewall
apt install ufw -y
ufw allow 2222/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 3. Bloqueie login root
nano /etc/ssh/sshd_config
# Adicione: PermitRoot no
# Reinicie: systemctl restart sshd
```

## Resumo

| Passo | Comando/Ação |
|-------|--------------|
| 1 | Comprar VPS KVM 2 na Hostinger |
| 2 | Conectar via SSH |
| 3 | Instalar Docker + NGINX |
| 4 | Clonar DEEP-AUREA |
| 5 | Configurar .env |
| 6 | `docker-compose up -d --build` |
| 7 | Configurar domínio no painel |
| 8 | Instalar SSL com Certbot |
| 9 | Testar! |

**Pronto!** Seu DEEP-AUREA estará rodando na Hostinger e os clientes acessam via navegador! 🚀
