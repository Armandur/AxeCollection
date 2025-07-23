# Integrerad Docker Deployment - AxeCollection

Denna guide beskriver hur man deployar AxeCollection med en integrerad Docker-image som innehåller både Django och Nginx.

## Fördelar med integrerad version

- **Enklare deployment**: Endast en container istället för två
- **Bättre för Unraid**: Enklare att hantera i Unraid Docker-appen
- **Färre volymer**: Mindre komplexitet i volymhantering
- **Enklare backup**: Allt i en container

## Snabb start

### Lokal testning
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

### Produktion (Unraid)
1. **Använd färdig image från Docker Hub**:
   ```bash
   docker pull armandur/axecollection:unraid
   ```

2. **Kör med docker-compose**:
   ```bash
   docker-compose -f docker-compose.unraid-published.yml up -d
   ```

## Unraid Deployment

### Via Unraid Docker-appen

1. **Lägg till container**:
   - Klicka "Add Container"
   - Namn: `axecollection`
   - Repository: `armandur/axecollection:latest` (från Docker Hub)

2. **Port mapping**:
   - Host Port 1: `8082` → Container Port 1: `80` (eller valfri port)

3. **Volymer** (använd cache för bättre prestanda):
   - `/mnt/cache/appdata/axecollection/data` → `/app/data`
   - `/mnt/cache/appdata/axecollection/media` → `/app/media`
   - `/mnt/cache/appdata/axecollection/logs` → `/app/logs`
   - `/mnt/cache/appdata/axecollection/backups` → `/app/backups`

4. **Miljövariabler**:
   - `DJANGO_SETTINGS_MODULE` = `AxeCollection.settings_production_http`
   - `SECRET_KEY` = `din_secret_key_här`
   - `ALLOWED_HOSTS` = `192.168.1.2,localhost,127.0.0.1` (anpassa efter din setup)
   - `CSRF_TRUSTED_ORIGINS` = `http://192.168.1.2:8082,https://din-domain.se` (anpassa efter din setup)

### Via Docker Compose i Unraid

1. **Kopiera filer** till `/mnt/cache/appdata/axecollection/`:
   - `docker-compose.unraid.yml` (eller `docker-compose.integrated.yml`)
   - `nginx.integrated.conf`
   - `deploy-unraid.sh` (valfritt)

2. **Kör**:
   ```bash
   cd /mnt/cache/appdata/axecollection
   docker-compose up -d
   ```
   
   **Eller använd deployment-scriptet**:
   ```bash
   chmod +x deploy-unraid.sh
   ./deploy-unraid.sh
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

5. **"exec /app/start.sh: no such file or directory"**:
   - Använd den senaste imagen: `armandur/axecollection:latest`
   - Kontrollera att containern har rätt behörigheter

6. **Nginx visar standard-sidan istället för Django**:
   - Använd den senaste imagen som innehåller korrekt Nginx-konfiguration
   - Kontrollera att `nginx.integrated.conf` är korrekt kopierad

7. **CSRF-fel vid inloggning**:
   - Lägg till rätt hosts i miljövariabler:
     ```bash
     ALLOWED_HOSTS="192.168.1.2,localhost,127.0.0.1,din-domain.se"
     CSRF_TRUSTED_ORIGINS="http://192.168.1.2:8082,https://din-domain.se"
     ```
   - Eller använd UI:t: Inställningar → Host-konfiguration

8. **Databasbehörigheter på Unraid**:
   ```bash
   # Fixa behörigheter från host-systemet
   docker exec -u root axecollection chown -R nobody:users /app/data
   docker exec -u root axecollection chmod -R 755 /app/data
   ```

### Demo-installation
För att skapa en demo-installation:
```bash
docker run -d \
  --name axecollection-demo \
  -p 8092:80 \
  -v "/path/to/demo/data:/app/data" \
  -v "/path/to/demo/media:/app/media" \
  -v "/path/to/demo/logs:/app/logs" \
  -v "/path/to/demo/backups:/app/backups" \
  -e DJANGO_SETTINGS_MODULE=AxeCollection.settings_production_http \
  -e ALLOWED_HOSTS="192.168.1.2,192.168.1.97,localhost,127.0.0.1,yxor-demo.pettersson-vik.se" \
  -e CSRF_TRUSTED_ORIGINS="http://192.168.1.2:8092,http://192.168.1.97:8092,https://yxor-demo.pettersson-vik.se" \
  armandur/axecollection:latest

# Skapa testdata
docker exec -it axecollection-demo python manage.py generate_test_data
``` 