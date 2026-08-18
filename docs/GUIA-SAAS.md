# DEEP-AUREA - Guia de Implantação SaaS
# Como hospedar e alugar sem expor o código

## Visão Geral

Neste modelo, VOCÊ hospeda o DEEP-AUREA e os clientes acessam via navegador.
O código-fonte NUNCA sai do seu servidor.

```
┌─────────────────────────────────────────────────┐
│  SEU SERVIDOR (VPS)                            │
│  └── Código protegido                          │
│  └── Banco de dados                            │
│  └── Modelos de IA                             │
└─────────────────────────────────────────────────┘
                    │
                    │ HTTPS (interface apenas)
                    ▼
┌─────────────────────────────────────────────────┐
│  CLIENTE (Navegador)                           │
│  └── Apenas visualiza e interage               │
│  └── NÃO tem acesso ao código                  │
│  └── NÃO baixa nada localmente                 │
└─────────────────────────────────────────────────┘
```

## Passo a Passo

### 1. Escolha um Provedor VPS

| Provedor | Preço | Especificação |
|----------|-------|---------------|
| Hetzner | ~€5/mês | 2 vCPU, 4GB RAM |
| DigitalOcean | $12/mês | 2 vCPU, 2GB RAM |
| AWS Lightsail | $10/mês | 2 vCPU, 2GB RAM |

**Recomendação:** Hetzger CX22 (€5.49/mês) - melhor custo-benefício

### 2. Prepare o Servidor

```bash
# Conecte ao VPS via SSH
ssh root@seu-ip

# Instale Docker e Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Instale Docker Compose
sudo apt install docker-compose -y
```

### 3. Faça Deploy do DEEP-AUREA

```bash
# Clone o repositório (NO SEU SERVIDOR)
git clone https://github.com/wwbcinformatica-gif/deep-aurea.git
cd deep-aurea

# Configure as chaves de API
cp backend/.env.example backend/.env
nano backend/.env  # Adicione suas chaves

# Build e inicie
docker-compose up -d --build
```

### 4. Configure NGINX (Proxy Reverso)

```bash
# Instale NGINX
sudo apt install nginx -y

# Crie a configuração
sudo nano /etc/nginx/sites-available/deep-aurea
```

```nginx
server {
    listen 80;
    server_name deep-aurea.seudominio.com;
    
    # Redireciona para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name deep-aurea.seudominio.com;

    # SSL (use Certbot)
    ssl_certificate /etc/letsencrypt/live/deep-aurea.seudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/deep-aurea.seudominio.com/privkey.pem;

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

    # WebSocket (Charon)
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

```bash
# Ative o site
sudo ln -s /etc/nginx/sites-available/deep-aurea /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Instale SSL com Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d deep-aurea.seudominio.com
```

### 5. Crie o Sistema de Usuários

```python
# backend/routes/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
import secrets

router = APIRouter()

# Banco de dados simples (substitua por PostgreSQL em produção)
users_db = {}

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/auth/register")
async def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(400, "Usuário já existe")
    
    # Hash da senha
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256(f"{salt}{user.password}".encode()).hexdigest()
    
    users_db[user.username] = {
        "salt": salt,
        "hash": password_hash,
        "plan": "free",  # free, pro, enterprise
        "limits": {
            "messages_per_day": 50,
            "models": ["qwen2.5-coder:7b"]
        }
    }
    
    return {"message": "Conta criada com sucesso"}

@router.post("/auth/login")
async def login(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(401, "Credenciais inválidas")
    
    stored = users_db[user.username]
    password_hash = hashlib.sha256(f"{stored['salt']}{user.password}".encode()).hexdigest()
    
    if password_hash != stored["hash"]:
        raise HTTPException(401, "Credenciais inválidas")
    
    # Gera token JWT
    token = generate_jwt(user.username)
    
    return {
        "token": token,
        "plan": stored["plan"],
        "limits": stored["limits"]
    }
```

### 6. Rate Limiting por Usuário

```python
# backend/middleware/rate_limiter.py
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class RateLimiter:
    def __init__(self):
        self.limits = {
            "free": {"messages": 50, "period": 86400},      # 50/dia
            "pro": {"messages": 500, "period": 86400},      # 500/dia
            "enterprise": {"messages": 5000, "period": 86400}  # 5000/dia
        }
    
    async def check_limit(self, user_id: str, plan: str):
        key = f"rate:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
        current = redis_client.get(key)
        
        limit = self.limits.get(plan, self.limits["free"])
        
        if current and int(current) >= limit["messages"]:
            raise HTTPException(
                status_code=429,
                detail=f"Limite diário atingido. Plano {plan}: {limit['messages']}/dia"
            )
        
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, limit["period"])
        pipe.execute()
```

### 7. Planos e Preços

```yaml
# Exemplo de planos
plans:
  free:
    name: "Gratuito"
    price: 0
    features:
      - 50 mensagens/dia
      - Modelo básico (qwen2.5-coder:7b)
      - Sem Charon (voz)
      - Suporte comunitário
    
  pro:
    name: "Profissional"
    price: 49.90
    period: month
    features:
      - 500 mensagens/dia
      - Todos os modelos
      - Charon (voz) incluso
      - Suporte prioritário
      - Histórico completo
    
  enterprise:
    name: "Empresarial"
    price: 199.90
    period: month
    features:
      - Mensagens ilimitadas
      - Modelos premium (GPT-4o, Claude)
      - Charon avançado
      - Suporte 24/7
      - SLA 99.9%
      - API access
      - Multi-usuários
```

## Como o Cliente Acessa

```
1. Cliente abre: https://deep-aurea.seudominio.com

2. Tela de login:
   ┌─────────────────────────────────────┐
   │  DEEP-AUREA                        │
   │                                     │
   │  Usuário: [_______________]        │
   │  Senha:   [_______________]        │
   │                                     │
   │  [Entrar]  [Criar conta]           │
   └─────────────────────────────────────┘

3. Após login, cliente vê a interface:
   ┌─────────────────────────────────────┐
   │  DEEP-AUREA - Bem-vindo!           │
   │                                     │
   │  [Chat] [Terminal] [Explorer]      │
   │                                     │
   │  ┌─────────────────────────────┐   │
   │  │ Como posso ajudar?         │   │
   │  │                             │   │
   │  │ [Enviar mensagem...]       │   │
   │  └─────────────────────────────┘   │
   │                                     │
   │  Plano: Pro | Mensagens: 487/500   │
   └─────────────────────────────────────┘

4. Cliente usa normalmente
   - Envia mensagens
   - Usa terminal
   - Explora arquivos
   - Ativa Charon (voz)

5. O que o cliente NÃO vê:
   ❌ Código-fonte Python
   ❌ Código-fonte React
   ❌ Configurações do servidor
   ❌ Chaves de API
   ❌ Banco de dados
```

## Vantagens deste Modelo

| Vantagem | Descrição |
|----------|-----------|
| **Código protegido** | Nunca sai do seu servidor |
| **Atualização fácil** | Atualiza uma vez, todos usam |
| **Controle total** | Você controla acesso e limites |
| **Receita recorrente** | Assinaturas mensais |
| **Escalável** | Adicione mais VPS conforme crescimento |
| **Backup centralizado** | Fácil de gerenciar |

## Custos Estimados

| Item | Custo Mensal |
|------|--------------|
| VPS (Hetzner CX22) | €5.49 (~R$30) |
| Domínio | ~R$10/ano |
| SSL (Let's Encrypt) | Grátis |
| **Total inicial** | ~R$35/mês |

## Como Cobrar dos Clientes

1. **Stripe** (internacional) - https://stripe.com
2. **Mercado Pago** (Brasil) - https://mercadopago.com.br
3. **Hotmart** (Brasil) - https://hotmart.com
4. **Patreon** - https://patreon.com

## Métricas Importantes

```python
# Monitore no seu painel admin
metrics = {
    "total_users": 150,
    "active_today": 45,
    "messages_today": 2340,
    "revenue_month": 4500.00,
    "server_load": "45%",
    "disk_usage": "12GB/50GB"
}
```

## Próximos Passos

1. ✅ Comprar VPS
2. ✅ Configurar domínio + SSL
3. ✅ Deploy do DEEP-AUREA
4. ✅ Criar sistema de usuários
5. ✅ Integrar pagamento
6. ✅ Criar landing page
7. ✅ Divulgar!
