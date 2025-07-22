# Integrerad Docker Deployment - AxeCollection

Denna guide beskriver hur man deployar AxeCollection med en integrerad Docker-image som innehåller både Django och Nginx.

## Fördelar med integrerad version

- **Enklare deployment**: Endast en container istället för två
- **Bättre för Unraid**: Enklare att hantera i Unraid Docker-appen
- **Färre volymer**: Mindre komplexitet i volymhantering
- **Enklare backup**: Allt i en container

## Snabb start

1. **Kopiera miljöfil**:
   ```bash
   cp env.example .env
   ```

2. **Sätt SECRET_KEY** i `.env`:
   ```bash
   # Generera ny nyckel
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Bygg och starta**:
   ```bash
   docker-compose -f docker-compose.integrated.yml up -d --build
   ```

## Unraid Deployment

### Via Unraid Docker-appen

1. **Lägg till container**:
   - Klicka "Add Container"
   - Namn: `axecollection`
   - Repository: `axecollection:latest` (efter att du byggt image)

2. **Port mapping**:
   - Host Port 1: `80` → Container Port 1: `80`

3. **Volymer**:
   - `/mnt/user/appdata/axecollection/data` → `/app/data`
   - `/mnt/user/appdata/axecollection/media` → `/app/media`
   - `/mnt/user/appdata/axecollection/logs` → `/app/logs`
   - `/mnt/user/appdata/axecollection/staticfiles` → `/app/staticfiles`
   - `/mnt/user/appdata/axecollection/backups` → `/app/backups`
   - `/mnt/user/appdata/axecollection/nginx.integrated.conf` → `/etc/nginx/sites-available/default` (read-only)

4. **Miljövariabler**:
   - `DJANGO_SETTINGS_MODULE` = `AxeCollection.settings_production`
   - `SECRET_KEY` = `din_secret_key_här`

### Via Docker Compose i Unraid

1. **Kopiera filer** till `/mnt/user/appdata/axecollection/`:
   - `docker-compose.integrated.yml`
   - `Dockerfile.integrated`
   - `supervisor.conf`
   - `nginx.integrated.conf`
   - `requirements.txt`
   - Hela projektmappen

2. **Kör**:
   ```bash
   cd /mnt/user/appdata/axecollection
   docker-compose -f docker-compose.integrated.yml up -d --build
   ```

## Backup och återställning

### Backup
```bash
# Backup av data
docker exec axecollection /app/backup.sh

# Backup av volymer
tar -czf axecollection_backup_$(date +%Y%m%d).tar.gz \
  ./data ./media ./logs ./staticfiles ./backups
```

### Återställning
```bash
# Återställ volymer
tar -xzf axecollection_backup_YYYYMMDD.tar.gz

# Återställ från backup-fil
docker exec axecollection python manage.py restore_backup backup_YYYYMMDD.sql
```

## Loggar och felsökning

### Visa loggar
```bash
# Alla loggar
docker logs axecollection

# Nginx loggar
docker exec axecollection tail -f /var/log/nginx/access.log
docker exec axecollection tail -f /var/log/nginx/error.log

# Gunicorn loggar
docker exec axecollection tail -f /var/log/supervisor/gunicorn.out.log
docker exec axecollection tail -f /var/log/supervisor/gunicorn.err.log

# Supervisor loggar
docker exec axecollection tail -f /var/log/supervisor/supervisord.log
```

### Felsökning
```bash
# Kontrollera processer
docker exec axecollection supervisorctl status

# Starta om tjänster
docker exec axecollection supervisorctl restart nginx
docker exec axecollection supervisorctl restart gunicorn

# Kontrollera nginx-konfiguration
docker exec axecollection nginx -t
```

## Prestanda och optimering

### Worker-inställningar
Justera antal Gunicorn-workers i `supervisor.conf`:
```ini
[program:gunicorn]
command=gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 120 ...
```

### Nginx-caching
Nginx är redan konfigurerat med:
- 1 års cache för statiska filer
- Gzip-komprimering
- Security headers

### Nginx-konfiguration
Nginx-konfigurationen (`nginx.integrated.conf`) är monterad som en volym, vilket betyder:
- **Enkel redigering**: Ändra konfigurationen direkt på host-systemet
- **Ingen ombyggning**: Ändringar träder i kraft efter nginx-restart
- **Versionering**: Konfigurationen kan versioneras med git

För att tillämpa ändringar i nginx-konfigurationen:
```bash
# Starta om nginx i containern
docker exec axecollection supervisorctl restart nginx

# Eller starta om hela containern
docker-compose -f docker-compose.integrated.yml restart
```

## Säkerhet

### Firewall
- Öppna endast port 80 (eller 443 för HTTPS)
- Begränsa åtkomst till admin-IP:er om möjligt

### SSL/HTTPS
För HTTPS, lägg till SSL-certifikat och uppdatera nginx-konfigurationen.

## Uppdateringar

### Uppdatera applikationen
```bash
# Stoppa containern
docker-compose -f docker-compose.integrated.yml down

# Bygg ny image
docker-compose -f docker-compose.integrated.yml build --no-cache

# Starta igen
docker-compose -f docker-compose.integrated.yml up -d
```

### Migreringar
```bash
# Kör migreringar
docker exec axecollection python manage.py migrate

# Samla statiska filer
docker exec axecollection python manage.py collectstatic --noinput
```

## Jämförelse med original-versionen

| Aspekt | Original | Integrerad |
|--------|----------|------------|
| Containrar | 2 (web + nginx) | 1 |
| Volymer | 6 | 5 |
| Komplexitet | Högre | Lägre |
| Unraid-kompatibilitet | Sämre | Bättre |
| Prestanda | Samma | Samma |
| Underhåll | Mer | Mindre |

## Felsökning

### Vanliga problem

1. **Port 80 redan används**:
   - Ändra host port i docker-compose.yml
   - Kontrollera att inga andra tjänster använder port 80

2. **Permission denied**:
   - Kontrollera volymbehörigheter
   - Kör `chown -R 1000:1000` på volymerna

3. **Nginx startar inte**:
   - Kontrollera nginx-konfiguration: `docker exec axecollection nginx -t`
   - Titta på nginx-loggar

4. **Gunicorn startar inte**:
   - Kontrollera Django-inställningar
   - Titta på gunicorn-loggar
   - Kontrollera att alla migreringar är körda 