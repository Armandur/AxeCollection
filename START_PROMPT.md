# Startprompt för AI-assistenter - AxeCollection

## Projektöversikt
AxeCollection är ett Django-baserat system för att hantera och katalogisera yxsamlingar med avancerad bildhantering, måttregistrering och transaktionshantering. Projektet har både en publik del (för besökare) och en inloggad admin-del (för samlaren).

## Viktiga filer att läsa först
1. **WORKFLOW_AND_COLLAB.md** - Detaljerad information om arbetsflöde, git-hantering och samarbetsprinciper
2. **TODO_FEATURES.md** - Aktuell status och kommande funktioner
3. **UX_DESIGN_DISCUSSION.md** - Designprinciper och UX-beslut
4. **README.md** - Teknisk översikt och installation

## Vårt arbetsflöde
- **Iterativ utveckling**: Jag föreslår lösningar, du testar och ger feedback, vi förbättrar tills det fungerar bra
- **Git-hantering**: Jag hjälper med git-kommandon, branch-hantering och dokumentation
- **Testning**: Testa alltid funktionalitet i webbläsaren innan commit
- **Dokumentation**: Uppdatera TODO_FEATURES.md och andra markdown-filer löpande
- **PowerShell-kompatibilitet**: Använd `;` istället för `&&` för att kedja kommandon

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
- **TODO-lista**: Uppdatera löpande och markera klara med [x]

## Nästa steg
1. Läs igenom markdown-filerna för att förstå projektet
2. Starta servern för att se aktuell status
3. Diskutera vad som ska arbetas med härnäst
4. Följ vårt etablerade arbetsflöde för iterativ utveckling
5. Kontrollera TODO_FEATURES.md för aktuella uppgifter
6. Uppdatera dokumentation efter större ändringar

## Kontakt och kommunikation
- Alla beslut dokumenteras i chatten och markdown-filer
- Transparens är viktigt - dokumentera resonemang och beslut
- Testa och få feedback innan vidareutveckling
- Uppdatera TODO-listan löpande med framsteg och nya idéer 