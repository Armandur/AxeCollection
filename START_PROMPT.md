# Startprompt för AI-assistenter - AxeCollection

## Projektöversikt
AxeCollection är ett Django-baserat system för att hantera och katalogisera yxsamlingar med avancerad bildhantering, måttregistrering och transaktionshantering. Projektet har både en publik del (för besökare) och en inloggad admin-del (för samlaren).

## Viktiga filer att läsa först
1. **WORKFLOW_AND_COLLAB.md** - Detaljerad information om arbetsflöde, git-hantering och samarbetsprinciper
2. **TODO_FEATURES.md** - Aktuell status och kommande funktioner
3. **UX_DESIGN_DISCUSSION.md** - Designprinciper och UX-beslut
4. **README.md** - Teknisk översikt och installation
5. **todo-manager/README.md** - TODO Manager-verktyget för uppgiftshantering

## Vårt arbetsflöde
- **Iterativ utveckling**: Jag föreslår lösningar, du testar och ger feedback, vi förbättrar tills det fungerar bra
- **Git-hantering**: Jag hjälper med git-kommandon, branch-hantering och dokumentation
- **Testning**: Testa alltid funktionalitet i webbläsaren innan commit
- **Dokumentation**: Uppdatera TODO_FEATURES.md och andra markdown-filer löpande
- **PowerShell-kompatibilitet**: Använd `;` istället för `&&` för att kedja kommandon
- **TODO-hantering**: Använd TODO Manager-verktyget för att strukturerat hantera uppgifter och framsteg

## Tekniska riktlinjer
- **Django 4.x** med Bootstrap 5 och JavaScript (ES6+)
- **Responsiv design**: Mobil-först approach, testa på både mobil och desktop
- **AJAX-flöden**: Fullständiga flöden med felhantering och feedback
- **Template-struktur**: Använd includes för återkommande komponenter
- **Model-properties**: Flytta komplexa beräkningar från vyer till modeller
- **Säkerhet**: @login_required för skyddade vyer, CSRF-skydd

## UX-principer
- **Färgschema**: Grön (status/positiv), Röd (status/negativ), Blå (neutral/sälj)
- **Knappplacering**: Logisk placering, konsekvent mönster för liknande funktioner
- **Feedback**: Tydliga notifikationer och laddningsindikatorer
- **Mobil**: Touch-vänliga knappar, dölj text för sekundära funktioner

## Vanliga kommandon
```powershell
# Starta servern
python manage.py runserver

# Kör tester
python manage.py test

# Skapa migreringar
python manage.py makemigrations

# Kör migreringar
python manage.py migrate

# Samla statiska filer
python manage.py collectstatic

# Docker-produktion
docker-compose up -d
docker-compose build --no-cache
docker-compose cp filnamn web:/app/sökväg/

# Docker-felsökning
docker logs container_name
docker exec -it container_name bash
docker exec -u root container_name chown -R nobody:users /app/data

# Git-workflow
git add .
git commit -m "Svenskt commit-meddelande"
git commit --amend --no-edit  # Lägg till i senaste commit
git push --force-with-lease   # Efter amend

# TODO Manager (från todo-manager/ mapp)
cd todo-manager
python todo_manager.py stats                    # Visa projektstatistik
python todo_manager.py sections                 # Lista alla sektioner
python todo_manager.py add "Uppgift" "Sektion"  # Lägg till uppgift
python todo_manager.py complete 42              # Markera uppgift som klar
python todo_manager.py list "Sektion" --incomplete  # Visa ofinished
```

## Viktiga beslut och lärdomar
- **Publik/privat vy**: Känsliga uppgifter (kontakter, priser) döljs för icke-inloggade användare
- **Flaggemoji**: Kontakter har landskoder som visas som flaggemoji
- **Bildhantering**: Drag & drop, URL-uppladdning, .webp-optimering
- **Måttmallar**: Fördefinierade mallar för olika yxtyper
- **Transaktionshantering**: Automatisk typbestämning baserat på pris
- **Media-filhantering**: Nginx serverar media-filer i produktion, automatisk sökvägsfix vid backup-återställning
- **Deployment**: Docker med volymer för data-persistens, settings-kopiering till containern krävs
- **Docker-problem**: Line endings (CRLF vs LF), behörigheter (nobody:users), Nginx-konfiguration
- **Host-konfiguration**: Dynamisk via UI och miljövariabler för ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS
- **Commit-meddelanden**: Använd svenska enligt användarens preferens
- **TODO-lista**: Använd TODO Manager-verktyget för strukturerad hantering istället för manuell redigering

## TODO Manager - Uppgiftshantering

**VIKTIGT**: Använd TODO Manager-verktyget för alla TODO-operationer istället för manuell redigering.

### Grundläggande användning:
```bash
cd todo-manager
python todo_manager.py stats    # Kontrollera projektets framsteg (77.4% klart)
python todo_manager.py sections # Se alla sektioner och antal uppgifter
```

### Daglig användning:
```bash
# Morgon - kolla status och planera
python todo_manager.py stats
python todo_manager.py list "Sektionsnamn" --incomplete

# Under arbete - lägg till nya uppgifter som dyker upp
python todo_manager.py add "Ny uppgift upptäcktes" "Relevant sektion"

# Efter slutfört arbete - markera klart
python todo_manager.py complete 42
python todo_manager.py complete-multiple 42 43 44  # Flera samtidigt
```

### När du arbetar med uppgifter:
1. **Börja alltid med stats** för att se övergripande status
2. **Lista relevanta sektioner** med `--incomplete` för fokus
3. **Lägg till uppgifter direkt** när nya behov upptäcks
4. **Markera som klara omedelbart** efter slutfört arbete
5. **Organisera** med `move`, `new-section` och `merge` vid behov

### Exempel på arbetsflöde:
```bash
# 1. Se vad som behöver göras
python todo_manager.py list "Bildhantering" --incomplete

# 2. Arbeta med uppgift X
# 3. När klar - markera direkt
python todo_manager.py complete 45

# 4. Om nya uppgifter upptäcks under arbetet
python todo_manager.py add "Fixa CSS-bugg i lightbox" "Bildhantering"

# 5. Slutkontroll av framsteg
python todo_manager.py stats
```

## Nästa steg
1. Läs igenom markdown-filerna för att förstå projektet
2. **Kör `cd todo-manager; python todo_manager.py stats`** för att se aktuell projektstatus
3. Starta servern för att se aktuell status
4. Diskutera vad som ska arbetas med härnäst baserat på TODO-statistik
5. Följ vårt etablerade arbetsflöde för iterativ utveckling
6. **Använd TODO Manager** för alla uppgiftsoperationer
7. Uppdatera dokumentation efter större ändringar

## Kontakt och kommunikation
- Alla beslut dokumenteras i chatten och markdown-filer
- Transparens är viktigt - dokumentera resonemang och beslut
- Testa och få feedback innan vidareutveckling
- Uppdatera TODO-listan löpande med framsteg och nya idéer 