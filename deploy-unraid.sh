#!/bin/bash

# AxeCollection Unraid Deployment Script
# Kör detta script på din Unraid-server

set -e

echo "🚀 AxeCollection Unraid Deployment"
echo "=================================="

# Skapa nödvändiga mappar
echo "📁 Skapar mappar..."
mkdir -p /mnt/cache/appdata/axecollection/{data,media,logs,staticfiles,backups}

# Fixa behörigheter för Unraid (nobody:users)
echo "🔐 Fixar behörigheter för Unraid..."
chown -R nobody:users /mnt/cache/appdata/axecollection
chmod -R 755 /mnt/cache/appdata/axecollection

# Kopiera nginx-konfiguration om den inte finns
if [ ! -f "/mnt/cache/appdata/axecollection/nginx.integrated.conf" ]; then
    echo "📄 Kopierar nginx-konfiguration..."
    # Du behöver kopiera nginx.integrated.conf till denna mapp
    echo "⚠️  Kopiera nginx.integrated.conf till /mnt/cache/appdata/axecollection/"
fi

# Skapa .env-fil om den inte finns
if [ ! -f "/mnt/cache/appdata/axecollection/.env" ]; then
    echo "🔑 Skapar .env-fil..."
    cat > /mnt/cache/appdata/axecollection/.env << EOF
# AxeCollection Environment Variables
SECRET_KEY=din_secret_key_här
EOF
    echo "⚠️  Uppdatera SECRET_KEY i /mnt/cache/appdata/axecollection/.env"
fi

# Kopiera docker-compose.yml
echo "📋 Kopierar docker-compose.yml..."
cp docker-compose.unraid.yml /mnt/cache/appdata/axecollection/docker-compose.yml

# Gå till mappen
cd /mnt/cache/appdata/axecollection

# Hämta senaste imagen
echo "⬇️  Hämtar senaste Docker-imagen..."
docker pull armandur/axecollection:unraid

# Starta containern
echo "🚀 Startar AxeCollection..."
docker-compose up -d

echo ""
echo "✅ Deployment klar!"
echo "🌐 AxeCollection är nu tillgänglig på: http://din-unraid-ip"
echo ""
echo "📊 Kontrollera status:"
echo "   docker-compose ps"
echo ""
echo "📝 Visa loggar:"
echo "   docker-compose logs -f"
echo ""
echo "🔄 Uppdatera i framtiden:"
echo "   docker-compose pull && docker-compose up -d" 