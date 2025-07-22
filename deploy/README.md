# Deployment Files - AxeCollection

Denna mapp innehåller alla filer som behövs för att deploya AxeCollection i produktion.

## Filer i denna mapp

### Konfiguration
- **`docker-compose.yml`** - Docker Compose-konfiguration för orchestration
- **`env.example`** - Mall för miljövariabler (.env-fil)

### Dokumentation
- **`DEPLOYMENT.md`** - Komplett deployment-guide med steg-för-steg instruktioner
- **`DEPLOYMENT_SUMMARY.md`** - Snabb översikt över deployment-konfigurationen
- **`README.md`** - Denna fil

### Scripts
- **`backup.sh`** - Automatiskt backup-script för databas och media-filer

## Snabb start

1. **Kopiera miljövariabler:**
   ```bash
   cp deploy/env.example .env
   # Redigera .env och sätt SECRET_KEY
   ```

2. **Skapa nödvändiga kataloger:**
   ```bash
   mkdir -p data logs media staticfiles
   ```

3. **Bygg och starta:**
   ```bash
   docker-compose -f deploy/docker-compose.yml build
   docker-compose -f deploy/docker-compose.yml up -d
   ```

4. **Kör migreringar:**
   ```bash
   docker-compose -f deploy/docker-compose.yml run --rm web python manage.py migrate
   docker-compose -f deploy/docker-compose.yml run --rm web python manage.py createsuperuser
   ```

## Backup

Kör backup-scriptet:
```bash
./deploy/backup.sh
```

## Mer information

Se `DEPLOYMENT.md` för komplett guide och `DEPLOYMENT_SUMMARY.md` för snabb översikt. 