# Startprompt för AI-assistenter - AxeCollection

## Snabbstart för AI-assistenter

### Första stegen när du börjar arbeta:
1. **Kolla projektstatus**: `cd todo-manager; python todo_manager.py stats`
2. **Se vad som behöver göras**: `python todo_manager.py all-incomplete`
3. **Starta servern**: `python manage.py runserver`
4. **Läs relevanta filer**: WORKFLOW_AND_COLLAB.md, .cursorrules, README.md

### Viktiga verktyg att använda aktivt:
- **`codebase_search`** - För att hitta relevant kod
- **`read_file`** - För att läsa specifika filer
- **`grep_search`** - För att hitta exakta textmönster
- **`list_dir`** - För att utforska projektstruktur
- **`run_terminal_cmd`** - För att köra kommandon
- **`edit_file`** - För att göra kodändringar

## Projektöversikt
AxeCollection är ett Django-baserat system för att hantera och katalogisera yxsamlingar med avancerad bildhantering, måttregistrering och transaktionshantering. Projektet har både en publik del (för besökare) och en inloggad admin-del (för samlaren).

## AI-assistent riktlinjer

### Arbetsmetodik
- **Använd verktyg aktivt**: Använd `codebase_search`, `read_file`, `grep_search` för att förstå kodstrukturen
- **Filstruktur**: Använd `list_dir` för att utforska projektstrukturen innan du börjar arbeta
- **Kodanalys**: Läs relevanta filer med `read_file` innan du föreslår ändringar
- **Sökning**: Använd `grep_search` för att hitta specifika funktioner eller mönster
- **Iterativ approach**: Testa dina förslag med användaren innan du implementerar fullständiga lösningar
- **Dokumentation**: Uppdatera relevanta markdown-filer efter större ändringar

### Viktiga filer att läsa först
1. **WORKFLOW_AND_COLLAB.md** - Detaljerad information om arbetsflöde, git-hantering och samarbetsprinciper
2. **UX_DESIGN_DISCUSSION.md** - Designprinciper och UX-beslut
3. **README.md** - Teknisk översikt och installation
4. **todo-manager/README.md** - TODO Manager-verktyget för uppgiftshantering

## Vårt arbetsflöde
- **Iterativ utveckling**: Jag föreslår lösningar, du testar och ger feedback, vi förbättrar tills det fungerar bra
- **Git-hantering**: Jag hjälper med git-kommandon, branch-hantering och dokumentation
- **Testning**: Testa alltid funktionalitet i webbläsaren innan commit
- **Dokumentation**: Uppdatera TODO_FEATURES.md och andra markdown-filer löpande
- **PowerShell-kompatibilitet**: Använd `;` istället för `&&` för att kedja kommandon
- **TODO-hantering**: Använd TODO Manager-verktyget för att strukturerat hantera uppgifter och framsteg

## Tekniska riktlinjer
- **Django 5.2.3** med Bootstrap 5 och JavaScript (ES6+)
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
python todo_manager.py all                     # Visa alla uppgifter (klara och oklara)
python todo_manager.py all-incomplete          # Visa alla ofinished uppgifter
python todo_manager.py sections                # Lista alla sektioner
python todo_manager.py add "Uppgift" "Sektion" # Lägg till uppgift
python todo_manager.py add-sub 42 "Underuppgift" # Lägg till underuppgift
python todo_manager.py complete 42             # Markera uppgift som klar (fungerar med alla nivåer)
python todo_manager.py complete-multiple 42 42.1 43 # Flera samtidigt (blandade typer)
python todo_manager.py list "Sektion" --incomplete  # Visa ofinished
python todo_manager.py show 42                 # Visa detaljerad information
python todo_manager.py move 42 "Ny sektion"    # Flytta uppgift
python todo_manager.py swap 42 43              # Byter plats på uppgifter
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
- **Hierarkiska uppgifter**: TODO Manager stöder 5 nivåer av underuppgifter (42.1, 42.1.1, etc.)
- **Smart complete**: `complete`-kommandot fungerar med både vanliga uppgifter och underuppgifter
- **Blandade typer**: `complete-multiple` kan hantera blandade uppgiftstyper (42, 42.1, 43)
- **Swap-funktion**: Använd `swap` för att byta plats på uppgifter istället för remove/add

## TODO Manager - Uppgiftshantering

**VIKTIGT**: Använd TODO Manager-verktyget för alla TODO-operationer istället för manuell redigering.

### Grundläggande användning:
```bash
cd todo-manager
python todo_manager.py stats                    # Visa projektstatistik
python todo_manager.py all                     # Visa alla uppgifter (klara och oklara)
python todo_manager.py all-incomplete          # Visa alla ofinished uppgifter
python todo_manager.py sections                # Lista alla sektioner
python todo_manager.py add "Uppgift" "Sektion" # Lägg till uppgift
python todo_manager.py complete 42             # Markera uppgift som klar
python todo_manager.py list "Sektion" --incomplete  # Visa ofinished
```

### Hierarkiska underuppgifter (5 nivåer):
```bash
# Lägg till underuppgift till huvuduppgift
python todo_manager.py add-sub 42 "Ny underuppgift"

# Lägg till underuppgift till underuppgift (nivå 3)
python todo_manager.py add-sub 42.1 "Underuppgift till 42.1"

# Markera underuppgifter som klara
python todo_manager.py complete 42.1.2        # Smart funktion - fungerar med alla nivåer
python todo_manager.py complete-multiple 42 42.1 42.2  # Blandade typer

# Visa detaljerad information
python todo_manager.py show 42                # Huvuduppgift med alla underuppgifter
python todo_manager.py show 42.1.2            # Specifik underuppgift
```

### Organisering och flytt:
```bash
# Flytta uppgifter
python todo_manager.py move 42 "Ny sektion"
python todo_manager.py swap 42 43             # Byter plats på uppgifter
python todo_manager.py move-sub 42.1.2 43     # Flytta underuppgift till ny förälder

# Sektionshantering
python todo_manager.py new-section "Ny sektion"
python todo_manager.py merge "Sektion 1" "Sektion 2"

# Ta bort
python todo_manager.py remove 42              # Ta bort uppgift
python todo_manager.py remove-multiple 42 43 44  # Ta bort flera
```

### Daglig användning:
```bash
# Morgon - kolla status och planera
python todo_manager.py stats
python todo_manager.py all-incomplete  # Visa alla ofinished uppgifter
python todo_manager.py list "Sektionsnamn" --incomplete

# Under arbete - lägg till nya uppgifter som dyker upp
python todo_manager.py add "Ny uppgift upptäcktes" "Relevant sektion"
python todo_manager.py add-multiple "Uppgift 1" "Uppgift 2" "Sektion"  # Flera samtidigt

# Efter slutfört arbete - markera klart
python todo_manager.py complete 42            # Fungerar med både vanliga och underuppgifter
python todo_manager.py complete-multiple 42 42.1 43  # Blandade typer
```

### När du arbetar med uppgifter:
1. **Börja alltid med stats** för att se övergripande status
2. **Lista relevanta sektioner** med `--incomplete` för fokus
3. **Lägg till uppgifter direkt** när nya behov upptäcks
4. **Markera som klara omedelbart** efter slutfört arbete
5. **Organisera** med `move`, `swap`, `new-section` och `merge` vid behov
6. **Använd hierarkiska underuppgifter** för komplexa uppgifter

### Exempel på arbetsflöde:
```bash
# 1. Se vad som behöver göras
python todo_manager.py all-incomplete  # Översikt över alla ofinished
python todo_manager.py list "Bildhantering" --incomplete  # Specifik sektion

# 2. Arbeta med uppgift X
# 3. När klar - markera direkt
python todo_manager.py complete 45

# 4. Om nya uppgifter upptäcks under arbetet
python todo_manager.py add "Fixa CSS-bugg i lightbox" "Bildhantering"

# 5. Slutkontroll av framsteg
python todo_manager.py stats
```

## Kodstandarder och best practices

### Python/Django
- Använd svenska för commit-meddelanden och dokumentation
- Följ PEP 8 med black-formatering (line-length = 88)
- Använd type hints där det är lämpligt
- Skriv docstrings för komplexa funktioner
- Använd `@property` för beräknade fält i modeller
- Använd `related_name` för att undvika konflikter med automatiska reverse-relationer

### Template-struktur
- Använd `{% load axe_filters %}` i includes för custom filters
- Skapa återanvändbara includes för återkommande UI-komponenter
- Använd `|safe` filter för HTML-innehåll som ska renderas som HTML
- Platta ut nästlade listor i Python innan de skickas till templates
- Organisera templates med includes för statistik-kort, filter-sektioner och andra återkommande element

### CSS och Styling
- Använd `!important` och specifika selektorer för att överskriva Bootstrap
- Använd `<strong>` taggar för att tvinga fetstil oavsett CSS-konflikter
- Undvik färger som redan används för semantiska betydelser (grön för status, röd för ekonomi)
- Testa styling på både desktop och mobil för konsekvent utseende
- Använd Bootstrap-kort med `h-100` för jämn höjd på olika skärmstorlekar

### JavaScript
- Använd debouncing för AJAX-sökningar (timeout för att undvika för många requests)
- Hantera AJAX-fel gracefully med fallback-beteenden
- Använd event delegation där det är lämpligt
- Undvik att blanda Django-template-kod direkt i JavaScript
- Använd Bootstrap Modal API istället för standard browser-dialoger
- Kontrollera alltid om variabler finns innan de används (t.ex. `axe.pk` för nya yxor)

## Felsökning och debugging

### Vanliga problem
- Kontrollera terminalen för detaljerade felmeddelanden vid 500-fel
- Validera att fältnamn finns i modellen innan användning i ORM-operationer
- Använd `git restore .` för att snabbt återställa oönskade ändringar
- Kontrollera att varje `{% block %}` avslutas med `{% endblock %}`

### Template-fel
- Lägg till `{% load axe_filters %}` i includes för custom filters
- Kontrollera att rätt context skickas in till includes
- Undvik att placera `{% endblock %}` inuti JavaScript-strängar

### Databas-problem
- Exportera data innan större modelländringar för säkerhet
- Använd migrations för säkra databasändringar

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