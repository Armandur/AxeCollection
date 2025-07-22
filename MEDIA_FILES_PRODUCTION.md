# Media-filhantering i produktionsmiljö

Denna dokumentation beskriver hur media-filer (uppladdade bilder) hanteras i produktionsmiljön för AxeCollection.

## Problem

I utvecklingsmiljön serverar Django's inbyggda utvecklingsserver automatiskt media-filer från `/media/` URL:en. I produktionsmiljön används Gunicorn som WSGI-server, som inte kan servera statiska filer på samma sätt.

## Lösning

Vi använder **Nginx** som reverse proxy för att:
1. Servera statiska filer (CSS, JS) direkt
2. Servera media-filer (uppladdade bilder) direkt
3. Skicka alla andra förfrågningar till Django/Gunicorn

## Arkitektur

```
Internet → Nginx (port 80) → Gunicorn/Django (port 8000)
                ↓
            Serverar statiska filer och media-filer direkt
```

## Konfiguration

### 1. Nginx-konfiguration (`nginx.conf`)

```nginx
# Media files
location /media/ {
    alias /app/media/;
    expires 1y;
    add_header Cache-Control "public";
    access_log off;
    
    # Handle missing images gracefully
    try_files $uri $uri/ =404;
}
```

### 2. Docker Compose (`docker-compose.yml`)

```yaml
services:
  web:
    # Django/Gunicorn container
    expose:
      - "8000"  # Endast internt tillgänglig
    
  nginx:
    # Nginx container
    ports:
      - "80:80"  # Publikt tillgänglig
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./staticfiles:/app/staticfiles:ro
      - ./media:/app/media:ro
```

## Deployment

### 1. Starta produktionsmiljön

```bash
# Stoppa utvecklingsmiljön först
docker-compose down

# Starta produktionsmiljön
docker-compose up -d

# Kontrollera att containers körs
docker-compose ps
```

### 2. Testa media-filhantering

```bash
# Kör test-scriptet
python test_media_files.py
```

### 3. Verifiera manuellt

1. Öppna webbläsaren på `http://localhost`
2. Navigera till en yxa med bilder
3. Kontrollera att bilderna laddas korrekt
4. Kontrollera att bilderna visas i galleriet

## Felsökning

### Problem: Bilder laddas inte

1. **Kontrollera Docker-containers:**
   ```bash
   docker-compose ps
   ```

2. **Kontrollera Nginx-loggar:**
   ```bash
   docker-compose logs nginx
   ```

3. **Kontrollera Django-loggar:**
   ```bash
   docker-compose logs web
   ```

4. **Verifiera filstruktur:**
   ```bash
   ls -la media/
   ls -la staticfiles/
   ```

### Problem: 404-fel för media-filer

1. **Kontrollera volym-mappning:**
   ```bash
   docker-compose exec nginx ls -la /app/media/
   ```

2. **Verifiera Nginx-konfiguration:**
   ```bash
   docker-compose exec nginx nginx -t
   ```

3. **Kontrollera filbehörigheter:**
   ```bash
   docker-compose exec nginx ls -la /app/media/
   ```

## Prestandaoptimering

### 1. Caching

Nginx är konfigurerat med:
- **1 års cache** för media-filer
- **Gzip-komprimering** för textfiler
- **Access log avstängd** för statiska filer

### 2. Bildoptimering

Bilder optimeras automatiskt:
- **WebP-konvertering** för moderna webbläsare
- **Komprimering** vid uppladdning
- **Lazy loading** i galleriet

## Säkerhet

### 1. Filåtkomst

- Media-filer är publikt tillgängliga (nödvändigt för bildvisning)
- Inga känsliga filer lagras i media-mappen
- Filnamn genereras automatiskt för att undvika path traversal

### 2. Nginx-säkerhet

- **Security headers** konfigurerade
- **Client max body size** begränsad till 100MB
- **Directory listing** inaktiverat

## Underhåll

### 1. Loggrotation

```bash
# Rotera Django-loggar
docker-compose exec web logrotate /etc/logrotate.d/django

# Rotera Nginx-loggar
docker-compose exec nginx logrotate /etc/logrotate.d/nginx
```

### 2. Diskutrymme

```bash
# Kontrollera diskutrymme
docker-compose exec web df -h

# Rensa gamla loggar
docker-compose exec web find /app/logs -name "*.log" -mtime +30 -delete
```

### 3. Backup

Media-filer backas upp automatiskt med:
```bash
python manage.py backup_database
```

## Framtida förbättringar

1. **CDN-integration** för globala distribution
2. **Image optimization** med automatisk storleksanpassning
3. **Cloud storage** (AWS S3, Google Cloud Storage)
4. **SSL/HTTPS** för säker filöverföring

## Relaterade filer

- `nginx.conf` - Nginx-konfiguration
- `docker-compose.yml` - Docker Compose-konfiguration
- `test_media_files.py` - Test-script för verifiering
- `AxeCollection/settings_production.py` - Produktionssettings 