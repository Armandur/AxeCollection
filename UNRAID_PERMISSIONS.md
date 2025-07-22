# Unraid-behörigheter för AxeCollection

## Problem med behörigheter

Unraid använder standardanvändaren `nobody:users` (UID: 65534, GID: 100) för Docker-containrar. Detta kan orsaka behörighetsproblem med Django-applikationer som förväntar sig andra användare.

## Lösningar

### Alternativ 1: Använd den publicerade imagen med user-mapping

```yaml
# docker-compose.unraid-published.yml
services:
  axecollection:
    image: armandur/axecollection:latest
    user: "65534:100"  # nobody:users
    # ... resten av konfigurationen
```

**Fördelar:**
- Enkel att använda
- Inga ombyggningar behövs
- Fungerar direkt med publicerad imagen

**Nackdelar:**
- Kan fortfarande ha behörighetsproblem med vissa filer

### Alternativ 2: Bygg egen imagen för Unraid

```yaml
# docker-compose.unraid.yml
services:
  axecollection:
    build:
      context: .
      dockerfile: Dockerfile.unraid
    # ... resten av konfigurationen
```

**Fördelar:**
- Perfekt anpassad för Unraid
- Inga behörighetsproblem
- Optimerad för Unraid-miljön

**Nackdelar:**
- Kräver ombyggning
- Större imagen

## Behörigheter för volymer

### På Unraid-servern:

```bash
# Skapa mappar med rätt behörigheter
mkdir -p /mnt/cache/appdata/axecollection/{data,media,logs,staticfiles,backups}

# Sätt behörigheter för nobody:users
chown -R nobody:users /mnt/cache/appdata/axecollection
chmod -R 755 /mnt/cache/appdata/axecollection
```

### Via Unraid Docker-appen:

1. **Skapa mappar** i `/mnt/cache/appdata/axecollection/`
2. **Sätt behörigheter** till `nobody:users`
3. **Mappa volymer** med rätt sökvägar

## Felsökning

### Kontrollera behörigheter:

```bash
# Kontrollera vilken användare containern kör som
docker exec axecollection id

# Kontrollera behörigheter på volymer
ls -la /mnt/cache/appdata/axecollection/

# Kontrollera loggar för behörighetsfel
docker logs axecollection | grep -i permission
```

### Vanliga problem:

1. **Permission denied på loggfiler**:
   - Lösning: Sätt rätt behörigheter på `/mnt/cache/appdata/axecollection/logs`

2. **Permission denied på media-filer**:
   - Lösning: Sätt rätt behörigheter på `/mnt/cache/appdata/axecollection/media`

3. **Permission denied på statiska filer**:
   - Lösning: Sätt rätt behörigheter på `/mnt/cache/appdata/axecollection/staticfiles`

## Rekommenderad approach

För enklaste deployment på Unraid:

1. **Använd `docker-compose.unraid-published.yml`** med den publicerade imagen
2. **Kör deployment-scriptet** som fixar behörigheter automatiskt
3. **Om problem kvarstår**, bygg egen imagen med `Dockerfile.unraid`

## Snabb fix för behörighetsproblem

```bash
# Kör detta på Unraid-servern
sudo chown -R nobody:users /mnt/cache/appdata/axecollection
sudo chmod -R 755 /mnt/cache/appdata/axecollection
docker-compose restart axecollection
``` 