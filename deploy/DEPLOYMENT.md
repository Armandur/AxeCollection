# Deployment Guide - AxeCollection

Denna guide beskriver hur du deployar AxeCollection med SQLite i produktion, baserat på [denna artikel](https://alldjango.com/articles/definitive-guide-to-using-django-sqlite-in-production).

## Förutsättningar

- Docker och Docker Compose installerat
- En server eller VPS med Linux
- Domännamn (valfritt, men rekommenderat)

## Steg 1: Förberedelser

### 1.1 Skapa produktionsmiljö
```bash
# Klona repot till servern
git clone <your-repo-url>
cd AxeCollection

# Skapa nödvändiga kataloger
mkdir -p data logs media staticfiles
```

### 1.2 Konfigurera SECRET_KEY
```bash
# Generera en säker SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Spara den i en .env-fil
echo "SECRET_KEY=din_genererade_nyckel_här" > .env
```

### 1.3 Uppdatera ALLOWED_HOSTS
Redigera `AxeCollection/settings_production.py` och lägg till din domän:
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'din-domän.com',
    'www.din-domän.com',
]
```

## Steg 2: Migrera data (om du har befintlig data)

### 2.1 Exportera från utvecklingsmiljön
```bash
# På din utvecklingsmaskin
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_backup.json
```

### 2.2 Importera till produktion
```bash
# Kopiera data_backup.json till servern
# Kör sedan:
python manage.py loaddata data_backup.json
```

## Steg 3: Bygg och starta med Docker

### 3.1 Bygg Docker-image
```bash
docker-compose build
```

### 3.2 Kör migreringar
```bash
docker-compose run --rm web python manage.py migrate
```

### 3.3 Skapa superuser
```bash
docker-compose run --rm web python manage.py createsuperuser
```

### 3.4 Starta applikationen
```bash
docker-compose up -d
```

## Steg 4: Konfigurera webbserver (valfritt)

### 4.1 Nginx-konfiguration
Skapa `/etc/nginx/sites-available/axecollection`:
```nginx
server {
    listen 80;
    server_name din-domän.com www.din-domän.com;

    location /static/ {
        alias /path/to/AxeCollection/staticfiles/;
    }

    location /media/ {
        alias /path/to/AxeCollection/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.2 Aktivera Nginx
```bash
sudo ln -s /etc/nginx/sites-available/axecollection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Steg 5: SSL/HTTPS (rekommenderat)

### 5.1 Installera Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 5.2 Skaffa SSL-certifikat
```bash
sudo certbot --nginx -d din-domän.com -d www.din-domän.com
```

### 5.3 Aktivera HTTPS i Django
Redigera `AxeCollection/settings_production.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Steg 6: Backup och underhåll

### 6.1 Automatisk backup
Skapa ett backup-script `backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"

# Backup databas
cp data/db.sqlite3 "$BACKUP_DIR/db_$DATE.sqlite3"

# Backup media-filer
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" media/

# Rensa gamla backuper (behåll senaste 7 dagarna)
find "$BACKUP_DIR" -name "db_*.sqlite3" -mtime +7 -delete
find "$BACKUP_DIR" -name "media_*.tar.gz" -mtime +7 -delete
```

### 6.2 Cron-job för automatisk backup
```bash
# Lägg till i crontab
0 2 * * * /path/to/backup.sh
```

## Steg 7: Övervakning och loggar

### 7.1 Loggövervakning
```bash
# Följ Django-loggar
tail -f logs/django.log

# Följ Docker-loggar
docker-compose logs -f web
```

### 7.2 Health check
```bash
# Kontrollera applikationens hälsa
curl http://localhost:8000/
```

## Vanliga kommandon

```bash
# Starta applikationen
docker-compose up -d

# Stoppa applikationen
docker-compose down

# Visa loggar
docker-compose logs -f web

# Uppdatera applikationen
git pull
docker-compose build
docker-compose up -d

# Backup databas
docker-compose exec web python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup_$(date +%Y%m%d).json

# Återställ från backup
docker-compose exec web python manage.py loaddata backup_20250101.json
```

## Säkerhetsöverväganden

1. **SECRET_KEY**: Använd alltid en säker SECRET_KEY i produktion
2. **DEBUG**: Sätt alltid DEBUG=False i produktion
3. **ALLOWED_HOSTS**: Begränsa till dina faktiska domäner
4. **HTTPS**: Använd alltid HTTPS i produktion
5. **Backup**: Säkerhetskopiera regelbundet
6. **Uppdateringar**: Håll Django och beroenden uppdaterade

## Felsökning

### Problem med statiska filer
```bash
docker-compose run --rm web python manage.py collectstatic --noinput
```

### Problem med databas
```bash
# Kontrollera databasfilen
ls -la data/db.sqlite3

# Reparera databas (om nödvändigt)
docker-compose run --rm web python manage.py dbshell
```

### Problem med behörigheter
```bash
# Fixa behörigheter för volymer
sudo chown -R 1000:1000 data logs media staticfiles
```

## Prestandaoptimering

1. **SQLite-optimering**: Databasen är redan konfigurerad med timeout och thread-safety
2. **Caching**: Lokal cache är aktiverad
3. **Statiska filer**: Served av Nginx för bättre prestanda
4. **Bildoptimering**: .webp-konvertering är redan implementerat

## Skalning

För större trafik kan du överväga:
1. **PostgreSQL**: Byt till PostgreSQL för bättre samtidiga användare
2. **Redis**: Lägg till Redis för caching
3. **Load balancer**: Använd flera instanser bakom en load balancer
4. **CDN**: Använd CDN för statiska filer och media 