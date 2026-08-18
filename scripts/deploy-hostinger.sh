#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DEEP-AUREA - Script de Deploy para Hostinger VPS
# ═══════════════════════════════════════════════════════════════
# 
# IMPORTANTE: Execute este script no VPS via SSH
# 
# Uso: 
#   1. Conecte ao VPS: ssh root@SEU_IP
#   2. Cole este script no terminal
#   3. Siga as instruções
#
# ═══════════════════════════════════════════════════════════════

set -e

# Cores para mensagens
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# ═══════════════════════════════════════════════════════════════
# CONFIGURAÇÕES (edite aqui)
# ═══════════════════════════════════════════════════════════════

DOMAIN=""          # Ex: deep-aurea.com.br
EMAIL=""           # Seu email para SSL
GROQ_KEY=""        # Sua chave Groq (opcional)
GEMINI_KEY=""      # Sua chave Gemini (opcional)
OPENAI_KEY=""      # Sua chave OpenAI (opcional)
LICENSE_KEY=""     # Chave de licença (opcional)

# ═══════════════════════════════════════════════════════════════
# FUNÇÕES
# ═══════════════════════════════════════════════════════════════

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Execute como root: sudo su"
        exit 1
    fi
}

check_domain() {
    if [ -z "$DOMAIN" ]; then
        print_warning "Domínio não configurado no script"
        read -p "Digite seu domínio (ex: deep-aurea.com.br): " DOMAIN
    fi
    
    if [ -z "$DOMAIN" ]; then
        print_error "Domínio é obrigatório"
        exit 1
    fi
    
    print_success "Domínio: $DOMAIN"
}

check_email() {
    if [ -z "$EMAIL" ]; then
        read -p "Digite seu email (para SSL): " EMAIL
    fi
    
    if [ -z "$EMAIL" ]; then
        print_error "Email é obrigatório para SSL"
        exit 1
    fi
    
    print_success "Email: $EMAIL"
}

# ═══════════════════════════════════════════════════════════════
# PASSO 1: ATUALIZAR SISTEMA
# ═══════════════════════════════════════════════════════════════

update_system() {
    print_status "Atualizando sistema..."
    apt update -y
    apt upgrade -y
    print_success "Sistema atualizado"
}

# ═══════════════════════════════════════════════════════════════
# PASSO 2: INSTALAR DEPENDÊNCIAS
# ═══════════════════════════════════════════════════════════════

install_dependencies() {
    print_status "Instalando dependências..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        print_status "Instalando Docker..."
        curl -fsSL https://get.docker.com | sh
        usermod -aG docker $USER
        print_success "Docker instalado"
    else
        print_success "Docker já instalado"
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_status "Instalando Docker Compose..."
        apt install docker-compose -y
        print_success "Docker Compose instalado"
    else
        print_success "Docker Compose já instalado"
    fi
    
    # NGINX
    if ! command -v nginx &> /dev/null; then
        print_status "Instalando NGINX..."
        apt install nginx -y
        print_success "NGINX instalado"
    else
        print_success "NGINX já instalado"
    fi
    
    # Git
    if ! command -v git &> /dev/null; then
        print_status "Instalando Git..."
        apt install git -y
        print_success "Git instalado"
    else
        print_success "Git já instalado"
    fi
    
    # Certbot
    if ! command -v certbot &> /dev/null; then
        print_status "Instalando Certbot..."
        apt install certbot python3-certbot-nginx -y
        print_success "Certbot instalado"
    else
        print_success "Certbot já instalado"
    fi
}

# ═══════════════════════════════════════════════════════════════
# PASSO 3: BAIXAR DEEP-AUREA
# ═══════════════════════════════════════════════════════════════

clone_project() {
    print_status "Baixando DEEP-AUREA..."
    
    if [ -d "deep-aurea" ]; then
        print_warning "Pasta deep-aurea já existe"
        read -p "Deseja remover e baixar novamente? (s/n): " REMOVE
        if [ "$REMOVE" = "s" ]; then
            rm -rf deep-aurea
            git clone https://github.com/wwbcinformatica-gif/deep-aurea.git
        else
            cd deep-aurea
            git pull
        fi
    else
        git clone https://github.com/wwbcinformatica-gif/deep-aurea.git
        cd deep-aurea
    fi
    
    print_success "Projeto baixado"
}

# ═══════════════════════════════════════════════════════════════
# PASSO 4: CONFIGURAR .ENV
# ═══════════════════════════════════════════════════════════════

configure_env() {
    print_status "Configurando variáveis de ambiente..."
    
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
    fi
    
    # Pede chaves se não estiverem configuradas
    if [ -z "$GROQ_KEY" ]; then
        read -p "Chave Groq (deixe vazio para pular): " GROQ_KEY
    fi
    
    if [ -z "$GEMINI_KEY" ]; then
        read -p "Chave Gemini (deixe vazio para pular): " GEMINI_KEY
    fi
    
    if [ -z "$OPENAI_KEY" ]; then
        read -p "Chave OpenAI (deixe vazio para pular): " OPENAI_KEY
    fi
    
    if [ -z "$LICENSE_KEY" ]; then
        read -p "Chave de licença (deixe vazio para pular): " LICENSE_KEY
    fi
    
    # Atualiza o arquivo .env
    if [ -n "$GROQ_KEY" ]; then
        sed -i "s/GROQ_API_KEY=.*/GROQ_API_KEY=$GROQ_KEY/" backend/.env
    fi
    
    if [ -n "$GEMINI_KEY" ]; then
        sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$GEMINI_KEY/" backend/.env
    fi
    
    if [ -n "$OPENAI_KEY" ]; then
        sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$OPENAI_KEY/" backend/.env
    fi
    
    if [ -n "$LICENSE_KEY" ]; then
        echo "DEEP_AUREA_LICENSE=$LICENSE_KEY" >> backend/.env
    fi
    
    print_success "Variáveis configuradas"
}

# ═══════════════════════════════════════════════════════════════
# PASSO 5: BUILD E INICIAR
# ═══════════════════════════════════════════════════════════════

build_and_start() {
    print_status "Fazendo build e iniciando..."
    
    docker-compose up -d --build
    
    print_success "Containers iniciados"
    print_status "Backend: http://localhost:8001"
    print_status "Frontend: http://localhost:5175"
}

# ═══════════════════════════════════════════════════════════════
# PASSO 6: CONFIGURAR NGINX
# ═══════════════════════════════════════════════════════════════

configure_nginx() {
    print_status "Configurando NGINX..."
    
    cat > /etc/nginx/sites-available/deep-aurea << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL (será configurado pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:5175;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # WebSocket (Charon - voz)
    location /ws/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }
}
EOF

    # Ativa o site
    ln -sf /etc/nginx/sites-available/deep-aurea /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Testa a configuração
    nginx -t
    
    # Reinicia o NGINX
    systemctl restart nginx
    
    print_success "NGINX configurado"
}

# ═══════════════════════════════════════════════════════════════
# PASSO 7: INSTALAR SSL
# ═══════════════════════════════════════════════════════════════

install_ssl() {
    print_status "Instalando SSL..."
    
    # Para o NGINX temporariamente
    systemctl stop nginx
    
    # Instala o certificado
    certbot certonly --standalone \
        -d $DOMAIN \
        -d www.$DOMAIN \
        --email $EMAIL \
        --agree-tos \
        --non-interactive
    
    # Reinicia o NGINX
    systemctl start nginx
    
    # Configura renovação automática
    echo "0 0,12 * * * certbot renew --quiet --post-hook 'systemctl restart nginx'" | crontab -
    
    print_success "SSL instalado"
}

# ═══════════════════════════════════════════════════════════════
# PASSO 8: CONFIGURAR FIREWALL
# ═══════════════════════════════════════════════════════════════

configure_firewall() {
    print_status "Configurando firewall..."
    
    # Instala UFW se não estiver instalado
    if ! command -v ufw &> /dev/null; then
        apt install ufw -y
    fi
    
    # Configura regras
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    
    print_success "Firewall configurado"
}

# ═══════════════════════════════════════════════════════════════
# PASSO 9: VERIFICAR STATUS
# ═══════════════════════════════════════════════════════════════

check_status() {
    print_status "Verificando status..."
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "                    STATUS DO DEPLOY"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Status dos containers
    docker-compose ps
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "                    INFORMAÇÕES"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  URL:        https://$DOMAIN"
    echo "  Backend:    http://localhost:8001"
    echo "  Frontend:   http://localhost:5175"
    echo "  Logs:       docker-compose logs -f"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "                    COMANDOS ÚTEIS"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  Ver logs:          docker-compose logs -f"
    echo "  Reiniciar:         docker-compose restart"
    echo "  Parar:             docker-compose down"
    echo "  Atualizar:         git pull && docker-compose up -d --build"
    echo "  Ver status:        docker-compose ps"
    echo "  Ver recursos:      docker stats"
    echo ""
}

# ═══════════════════════════════════════════════════════════════
# MENU PRINCIPAL
# ═══════════════════════════════════════════════════════════════

show_menu() {
    clear
    echo "═══════════════════════════════════════════════════════════"
    echo "      DEEP-AUREA - Deploy na Hostinger VPS"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  1. Deploy completo (recomendado)"
    echo "  2. Apenas instalar dependências"
    echo "  3. Apenas configurar NGINX"
    echo "  4. Apenas instalar SSL"
    echo "  5. Verificar status"
    echo "  6. Sair"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
}

# ═══════════════════════════════════════════════════════════════
# EXECUÇÃO
# ═══════════════════════════════════════════════════════════════

main() {
    # Verifica se é root
    check_root
    
    # Mostra menu
    show_menu
    read -p "Escolha uma opção: " OPTION
    
    case $OPTION in
        1)
            # Deploy completo
            check_domain
            check_email
            update_system
            install_dependencies
            clone_project
            configure_env
            build_and_start
            configure_nginx
            install_ssl
            configure_firewall
            check_status
            ;;
        2)
            # Apenas dependências
            update_system
            install_dependencies
            ;;
        3)
            # Apenas NGINX
            check_domain
            configure_nginx
            ;;
        4)
            # Apenas SSL
            check_domain
            check_email
            install_ssl
            ;;
        5)
            # Verificar status
            check_status
            ;;
        6)
            # Sair
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida"
            exit 1
            ;;
    esac
}

# Pergunta se quer executar
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  DESEJA EXECUTAR O DEPLOY AGORA?"
echo "═══════════════════════════════════════════════════════════"
echo ""
read -p "Responda (s/n): " EXECUTE

if [ "$EXECUTE" = "s" ]; then
    main
else
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  SCRIPT SALVO - Execute quando estiver pronto"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  Para executar depois:"
    echo "  1. Conecte ao VPS: ssh root@SEU_IP"
    echo "  2. Cole este script no terminal"
    echo "  3. Responda 's' quando perguntar"
    echo ""
fi
