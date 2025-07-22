# Projektstruktur - AxeCollection

## Översikt

AxeCollection har nu en tydlig separation mellan utvecklings- och deployment-filer för bättre organisation och underhåll.

## Root-struktur

```
AxeCollection/
├── AxeCollection/              # Django-projekt
│   ├── settings.py            # Utvecklingssettings
│   ├── settings_production.py # Produktionssettings
│   ├── wsgi.py               # Utvecklings-WSGI
│   ├── wsgi_production.py    # Produktions-WSGI
│   └── ...
├── axes/                      # Django-app
├── deploy/                    # 🆕 Deployment-filer
├── Dockerfile                 # Docker-konfiguration
├── .dockerignore             # Docker-ignore
├── requirements.txt           # Python-beroenden
├── manage.py                 # Django management
├── README.md                 # Huvuddokumentation
└── ... (övriga utvecklingsfiler)
```

## Deploy-mappen

```
deploy/
├── README.md                 # Deployment-dokumentation
├── docker-compose.yml        # Docker Compose-konfiguration
├── env.example              # Mall för miljövariabler
├── backup.sh                # Backup-script
├── DEPLOYMENT.md            # Komplett deployment-guide
└── DEPLOYMENT_SUMMARY.md    # Snabb översikt
```

## Fördelar med den nya strukturen

### 🧹 **Renare root-struktur**
- Root-katalogen innehåller bara källkod och väsentliga filer
- Deployment-filer är organiserade i egen mapp
- Enklare att navigera och förstå

### 🔧 **Tydlig separation**
- Utvecklingsfiler i root
- Deployment-filer i `deploy/`
- Docker-filer på standardplatser (root)

### 📚 **Bättre dokumentation**
- `deploy/README.md` förklarar deployment-strukturen
- Tydliga instruktioner för både utveckling och produktion
- Enklare att hitta relevant information

### 🚀 **Flexibilitet**
- Enkelt att ignorera deployment-filer i .gitignore om nödvändigt
- Möjlighet att ha olika deployment-konfigurationer
- Skalbar struktur för framtida behov

## Användning

### Utveckling
```bash
# Standard Django-utveckling
python manage.py runserver
```

### Produktion
```bash
# Använd deployment-filer
cp deploy/env.example .env
docker-compose -f deploy/docker-compose.yml up -d
```

### Backup
```bash
# Kör backup-script
./deploy/backup.sh
```

## Filer som flyttats

**Från root till deploy/:**
- `docker-compose.yml` → `deploy/docker-compose.yml`
- `backup.sh` → `deploy/backup.sh`
- `DEPLOYMENT.md` → `deploy/DEPLOYMENT.md`
- `DEPLOYMENT_SUMMARY.md` → `deploy/DEPLOYMENT_SUMMARY.md`
- `env.example` → `deploy/env.example`

**Kvar i root:**
- `Dockerfile` (Docker-standard)
- `.dockerignore` (Docker-standard)
- `AxeCollection/settings_production.py` (Django-standard)
- `AxeCollection/wsgi_production.py` (Django-standard)

## Kommandon som uppdaterats

### Docker Compose
```bash
# Tidigare
docker-compose up -d

# Nu
docker-compose -f deploy/docker-compose.yml up -d
```

### Backup
```bash
# Tidigare
./backup.sh

# Nu
./deploy/backup.sh
```

## Nästa steg

1. **Testa den nya strukturen** lokalt
2. **Uppdatera CI/CD-pipelines** om du har några
3. **Dokumentera för teamet** om du arbetar med andra
4. **Deploya till produktion** med den nya strukturen

## Resurser

- `deploy/README.md` - Deployment-dokumentation
- `deploy/DEPLOYMENT.md` - Komplett guide
- `README.md` - Huvuddokumentation
- `WORKFLOW_AND_COLLAB.md` - Arbetsflöde och samarbete 