# Host-konfiguration via UI

Denna funktion låter dig konfigurera externa hosts och CSRF-tillåtna origins direkt i appen utan att behöva redigera miljövariabler eller starta om servern.

## Funktioner

### **Dynamisk host-konfiguration**
- Konfigurera `ALLOWED_HOSTS` via UI:t
- Konfigurera `CSRF_TRUSTED_ORIGINS` via UI:t
- Ändringar träder i kraft omedelbart
- Kombinerar med befintliga miljövariabler

### **Säkerhet**
- Endast inloggade användare kan ändra inställningar
- Validering av input
- Fallback till standardvärden vid fel

## Användning

### **1. Gå till inställningar**
Navigera till `/installningar/` i appen.

### **2. Hitta host-konfiguration**
Scrolla ner till sektionen "Host-konfiguration" eller klicka på länken i navigeringen.

### **3. Konfigurera externa hosts**
I fältet "Externa hosts" anger du komma-separerade domäner eller IP-adresser:

```
demo.domain.com,192.168.1.100,test.example.com
```

### **4. Konfigurera CSRF-tillåtna origins**
I fältet "CSRF-tillåtna origins" anger du komma-separerade URLs med protokoll:

```
https://demo.domain.com,http://192.168.1.100,https://test.example.com
```

### **5. Spara inställningar**
Klicka på "Spara inställningar" för att applicera ändringarna.

## Exempel på konfigurationer

### **Lokal demo-server**
```
Externa hosts: localhost,127.0.0.1,192.168.1.100
CSRF-tillåtna origins: http://localhost,http://127.0.0.1,http://192.168.1.100
```

### **Publik demo-server med HTTPS**
```
Externa hosts: demo.yourdomain.com,www.demo.yourdomain.com
CSRF-tillåtna origins: https://demo.yourdomain.com,https://www.demo.yourdomain.com
```

### **Flera domäner**
```
Externa hosts: demo1.domain.com,demo2.domain.com,test.example.com
CSRF-tillåtna origins: https://demo1.domain.com,https://demo2.domain.com,https://test.example.com
```

## Teknisk implementation

### **Databasmodell**
Nya fält i `Settings`-modellen:
- `external_hosts`: TextField för externa hosts
- `external_csrf_origins`: TextField för CSRF-origins

### **Settings-filer**
Uppdaterade `settings_production.py` och `settings_production_http.py`:
- Läser hosts från databasen vid startup
- Kombinerar med miljövariabler
- Tar bort duplicerade värden

### **Management-kommando**
`update_hosts`-kommandot:
- Uppdaterar miljövariabler från databasen
- Körs automatiskt när inställningar sparas
- Kan köras manuellt: `python manage.py update_hosts`

### **UI-integration**
- Ny sektion i settings-sidan
- Validering av input
- Automatisk uppdatering vid sparande

## Felsökning

### **"DisallowedHost" fel**
- Kontrollera att din IP/domän finns i "Externa hosts"
- Se till att inga extra mellanslag finns

### **CSRF-fel**
- Kontrollera att din URL finns i "CSRF-tillåtna origins"
- Se till att protokoll (http/https) är korrekt angivet

### **Inställningar sparas inte**
- Kontrollera att du är inloggad
- Kontrollera att alla fält har korrekt format

## Säkerhetsöverväganden

- **Begränsa åtkomst**: Använd endast de hosts du verkligen behöver
- **Använd HTTPS**: I produktion, använd alltid HTTPS för CSRF-origins
- **Regelbunden granskning**: Kontrollera regelbundet vilka hosts som är konfigurerade
- **Backup**: Ta backup av inställningarna regelbundet

## Kompatibilitet

### **Befintliga miljövariabler**
- Miljövariabler `ALLOWED_HOSTS` och `CSRF_TRUSTED_ORIGINS` fungerar fortfarande
- UI-konfiguration läggs till befintliga värden
- Inga konflikter mellan olika konfigurationsmetoder

### **Backward compatibility**
- Befintliga inställningar påverkas inte
- Standardvärden används om inga externa hosts är konfigurerade
- Alla befintliga funktioner fungerar som tidigare 