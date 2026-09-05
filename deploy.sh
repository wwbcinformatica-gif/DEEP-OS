#!/bin/bash
# DEEP-OS - Deploy/update script para VPS
# Uso: ./deploy.sh
# Ou automaticamente via GitHub Actions

set -e

cd /root/DEEP-OS

echo "🔄 Atualizando codigo..."
git pull origin master

echo "🐳 Reconstruindo containers..."
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

echo "✅ Deploy concluido!"
echo "🌐 Frontend: http://$(hostname -I | awk '{print $1}'):5176"
echo "🔧 Backend:  http://$(hostname -I | awk '{print $1}'):8001"
