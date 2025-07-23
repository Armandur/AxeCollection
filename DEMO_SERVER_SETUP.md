# Demo Server Setup

Denna guide visar hur du sätter upp AxeCollection som en demo-server med dynamisk host-konfiguration.

## Miljövariabler för Demo-Server

### ALLOWED_HOSTS
Konfigurera vilka domäner/IP-adresser som får komma åt servern:

```bash
# För lokal utveckling
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# För demo-server med specifik IP
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100

# För demo-server med domän
ALLOWED_HOSTS=localhost,127.0.0.1,demo.yourdomain.com

# För flera domäner
ALLOWED_HOSTS=localhost,127.0.0.1,demo1.yourdomain.com,demo2.yourdomain.com
```

### CSRF_TRUSTED_ORIGINS
Konfigurera vilka origins som får skicka CSRF-tokens (inkludera protokoll):

```bash
# För HTTP demo-server
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://192.168.1.100

# För HTTPS demo-server
CSRF_TRUSTED_ORIGINS=https://demo.yourdomain.com,https://www.demo.yourdomain.com

# För både HTTP och HTTPS
CSRF_TRUSTED_ORIGINS=http://localhost,https://demo.yourdomain.com
```

## Exempel på .env-fil för Demo-Server

```bash
# Django Settings
SECRET_KEY=your_secret_key_here
DJANGO_SETTINGS_MODULE=AxeCollection.settings_production

# Demo server configuration
ALLOWED_HOSTS=localhost,127.0.0.1,demo.yourdomain.com
CSRF_TRUSTED_ORIGINS=http://localhost,https://demo.yourdomain.com

# Security settings
DEBUG=False

# HTTPS settings (uncomment for HTTPS)
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True
```

## Docker Compose för Demo-Server

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    expose:
      - "8000"
    volumes:
      - ./data:/app/data
      - ./media:/app/media
      - ./logs:/app/logs
      - ./staticfiles:/app/staticfiles
      - ./backups:/app/backups
    environment:
      - DJANGO_SETTINGS_MODULE=AxeCollection.settings_production
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "manage.py", "check"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - axe_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"  # För HTTPS
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./staticfiles:/app/staticfiles:ro
      - ./media:/app/media:ro
      - ./ssl:/etc/nginx/ssl:ro  # För SSL-certifikat
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - axe_network

networks:
  axe_network:
    driver: bridge

volumes:
  data:
  media:
  logs:
  staticfiles:
  backups:
```

## Snabbstart för Demo-Server

1. **Kopiera env.example till .env:**
   ```bash
   cp env.example .env
   ```

2. **Redigera .env med dina inställningar:**
   ```bash
   # Sätt din SECRET_KEY
   SECRET_KEY=din_hemliga_nyckel_här
   
   # Sätt dina hosts
   ALLOWED_HOSTS=localhost,127.0.0.1,demo.din-domain.se
   CSRF_TRUSTED_ORIGINS=http://localhost,https://demo.din-domain.se
   ```

3. **Starta servern:**
   ```bash
   docker-compose up -d
   ```

4. **Kontrollera att allt fungerar:**
   ```bash
   docker-compose logs web
   ```

## Felsökning

### "DisallowedHost" fel
Om du får "DisallowedHost" fel, kontrollera att din IP/domän finns i `ALLOWED_HOSTS`.

### CSRF-fel
Om du får CSRF-fel, kontrollera att din URL finns i `CSRF_TRUSTED_ORIGINS` med rätt protokoll (http/https).

### Exempel på vanliga fel:
```bash
# Fel - saknar protokoll
CSRF_TRUSTED_ORIGINS=localhost,demo.domain.com

# Rätt - inkluderar protokoll
CSRF_TRUSTED_ORIGINS=http://localhost,https://demo.domain.com
```

## Säkerhet för Demo-Server

- Använd alltid en stark `SECRET_KEY`
- Sätt `DEBUG=False` i produktion
- Begränsa `ALLOWED_HOSTS` till endast de domäner du behöver
- Använd HTTPS i produktion
- Uppdatera regelbundet för säkerhetsuppdateringar 