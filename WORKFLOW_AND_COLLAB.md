# Arbetsflöde och samarbetsprinciper (AI & utvecklare)

**Målgrupp:** Denna fil är primärt skriven för AI-assistenter som ska hjälpa till med projektet. Den innehåller instruktioner, historik och beslut som hjälper AI:n att förstå kontext och arbetsflöden.

**Syfte:** Ge AI-assistenter bästa möjliga start för att fortsätta arbetet utan att behöva gå igenom hela chathistoriken. Filen dokumenterar hur vi har resonerat kring arbetsflöde, branch-hantering och samarbete i projektet, baserat på diskussioner mellan utvecklare och AI-assistent.

## Branch-strategi
- **Feature branches:** Varje större funktionalitet utvecklas i en egen branch, t.ex. `feature/axe-create-edit`, `feature/dark-mode`, `feature/contact-integration`.
- **Push och PR:** När en feature är klar pushas branchen till GitHub och en Pull Request (PR) skapas mot `main` (eller annan relevant branch).
- **Merge-ordning:** Om branches bygger på varandra, mergeas de i rätt ordning (äldsta/underliggande först).
- **Städning:** Efter merge tas feature-branches bort både lokalt och på GitHub för att hålla repo:t städat.

## Git-arbetsflöde
- **Commit-meddelanden:** Skrivs tydligt och sammanfattar vad som ändrats, gärna punktlistor vid större ändringar.
- **Squash/rebase:** Används ibland för att slå ihop flera commits till en innan PR för en renare historik.
- **Uppdatera main:** Efter merge av PR hämtas alltid senaste main innan nya features påbörjas.
- **Upstream setup:** Nya branches sätts upp med `git push --set-upstream origin branch-name` för första push.

## Samarbetsprinciper
- **Transparens:** Allt arbete och alla beslut dokumenteras i chatten och/eller i markdown-filer.
- **Automatisering:** AI-assistenten hjälper till med git-kommandon, branch-hantering och dokumentation.
- **Dokumentation:** Viktiga resonemang, beslut och arbetsflöden dokumenteras i denna fil för framtida utvecklare och AI-assistenter.
- **Iterativ utveckling:** Vi arbetar iterativt där AI föreslår lösningar, utvecklaren testar och ger feedback, och vi förbättrar tills det fungerar bra.

## Tekniska beslut och lärdomar

### Django Admin-anpassningar
- **Custom templates:** Använder custom templates för admin-vyer när standardbeteendet inte räcker till.
- **Form-hantering:** Skapar custom forms för admin när vi behöver extra fält eller validering.
- **Context data:** Modifierar context data i admin-klasser för att skicka extra information till templates.
- **File handling:** Hanterar filradering (original + webp) baserat på användarens val via bockruta.

### Template-hantering
- **Filter-begränsningar:** Django templates tillåter inte alla Python-filter. Lösning: Hantera komplex logik i Python och skicka färdig data till templates.
- **Nested lists:** Platta ut nästlade listor i Python innan de skickas till templates för enklare rendering.
- **Safe rendering:** Använd `|safe` filter för HTML-innehåll som ska renderas som HTML.
- **DRY-principer:** Skapa återanvändbara includes för återkommande UI-komponenter för att undvika duplicerad kod.
- **Template-struktur:** Organisera templates med includes för statistik-kort, filter-sektioner och andra återkommande element.
- **Filter-laddning:** Ladda custom filters i includes med `{% load axe_filters %}` för att säkerställa att de fungerar.

### CSS och styling
- **CSS-specificitet:** Använd `!important` och specifika selektorer (t.ex. `table#axesTable tbody tr td .badge`) för att överskriva Bootstrap's standardstyling
- **Inline-styling:** Använd `<strong>` taggar för att tvinga fetstil oavsett CSS-konflikter med ramverk
- **Färgkonflikter:** Undvik färger som redan används för semantiska betydelser (grön för status, röd för ekonomi)
- **Responsiv design:** Testa styling på både desktop och mobil för att säkerställa konsekvent utseende
- **Bootstrap-override:** Förstå Bootstrap's CSS-hierarki för att effektivt överskriva standardstyling

### Django ORM och modeller
- **Related names:** Använd explicit `related_name` för att undvika konflikter med automatiska reverse-relationer
- **Property methods:** Använd `@property` för att skapa beräknade fält som kan användas i templates
- **Migration safety:** Exportera data innan större modelländringar för säkerhet
- **ORM-optimering:** Använd `select_related` och `prefetch_related` för att minska antalet databasqueries
- **Model validation:** Validera data på modellnivå för bättre dataintegritet

### AJAX och JavaScript
- **Debouncing:** Använd timeout för AJAX-sökningar för att undvika för många requests.
- **Error handling:** Hantera AJAX-fel gracefully med fallback-beteenden.
- **Dropdown management:** Visa/dölj dropdowns baserat på sökresultat och användarinteraktion.

### PowerShell och terminal-kommandon
- **Kommandokedning:** Använd `;` istället för `&&` för att kedja kommandon i PowerShell
- **Webbrequests:** Använd `Invoke-WebRequest` med `-UseBasicParsing` för att testa webbsidor
- **Statuskod-kontroll:** Använd `Select-Object -ExpandProperty StatusCode` för att kontrollera HTTP-status
- **Background-jobb:** Använd `-is_background` för långvariga processer som Django-servern

### Dataexport och import
- **CSV-säkerhet:** Hantera radbrytningar och specialtecken i textfält för korrekt export
- **Clean text:** Använd funktioner som ersätter `\n` och `\r` med mellanslag för säker CSV-export
- **Backup:** Exportera data innan större databasändringar för säkerhet
- **Encoding:** Använd UTF-8 för korrekt hantering av svenska tecken

### Formulärdesign
- **Conditional fields:** Visa olika fält beroende på om objekt skapas eller redigeras.
- **Smart defaults:** Sätt smarta standardvärden (t.ex. dagens datum för transaktioner).
- **Validation feedback:** Ge tydlig feedback när validering misslyckas.

## Senaste genomförda förbättringar (2025-07-21)

### API för borttagning av transaktioner och Bootstrap-modal (2025-07-21)
- **API-endpoint för transaktionsborttagning**: Implementerat `/api/transaction/<id>/delete/` endpoint med fullständig säkerhet och felhantering
- **Bootstrap-modal istället för alert**: Ersatt `confirm()` och `alert()` med professionella Bootstrap-modaler för bättre användarupplevelse
- **Separata modaler**: Olika modaler för bekräftelse (varning) och felmeddelanden (fel) för tydlig användarupplevelse
- **Säkerhetsfunktioner**: `@login_required` decorator för att skydda API-endpoints från oauktoriserad åtkomst
- **JavaScript-struktur**: Globala variabler för modal-instanser och återanvändbara funktioner för felhantering
- **Responsiv design**: Modaler anpassas automatiskt för olika skärmstorlekar med konsekvent design
- **Ikoner och färgkodning**: FontAwesome-ikoner och färgkodning för tydlig visuell feedback
- **Tekniska lärdomar**:
  - API-design: Använd RESTful endpoints med tydliga URL-mönster för konsekvent API-struktur
  - Modal-hantering: Bootstrap Modal API ger bättre kontroll och anpassningsbarhet än standard browser-dialoger
  - Felhantering: Separera bekräftelse- och felmodaler för tydligare användarupplevelse och bättre UX
  - CSRF-skydd: `@csrf_exempt` för API-endpoints som inte använder Django-forms, men behåll säkerhet med `@login_required`
  - JavaScript-organisering: Använd globala variabler för modal-instanser och återanvändbara funktioner för DRY-principer
  - UX-konsistens: Alla modaler följer samma designmönster för enhetlig användarupplevelse

### Användarhantering och publik/privat vy (2025-07-21)
- **Inloggningssystem**: Fullständigt Django Auth-system implementerat med anpassade templates, långa sessioner (30 dagar) och starka lösenord (minst 12 tecken)
- **Publik/privat vy**: Konfigurerbart system där känsliga uppgifter (kontakter, priser, plattformar) kan döljas för icke-inloggade användare
- **Settings-modell**: Ny modell med konfigurerbara publika inställningar för flexibel kontroll över vad som visas publikt
- **Context processor**: Automatisk tillgänglighet av publika inställningar i alla templates
- **Inställningssida**: Dedikerad sida för administratörer att konfigurera publika inställningar och sajtinformation
- **Intelligent filtrering**: Global sökning, yxlistor och transaktionsdata respekterar publika inställningar automatiskt
- **Responsiv användarupplevelse**: Login-modal, användardropdown och konsekvent navigation som anpassas efter användarstatus
- **Säkerhetsfunktioner**: @login_required decorator för skyddade vyer, automatisk redirect till login, session-hantering
- **Fallback-hantering**: Robust felhantering om Settings-modellen inte finns ännu
- **Tekniska lärdomar**:
  - Django Auth-system: Använd Django's inbyggda auth-system för säkerhet och enkelhet
  - Context processors: Perfekt för att göra globala inställningar tillgängliga i alla templates
  - Session-hantering: Långa sessioner förbättrar användarupplevelsen men kräver säkerhetsåtgärder
  - Fallback-logik: Alltid ha fallback för nya modeller som kanske inte finns ännu

## Senaste genomförda förbättringar (2025-07-18)

### JavaScript-fel och landsfält-problem (2025-07-18)
- **SyntaxError-fix på yxformuläret**: Fixade `window.axeId = ;` genom att kontrollera om `axe.pk` finns innan värdet sätts
- **Landsfält-simplifiering**: Ersatte komplex sökbar select med enkel dropdown för landsfält på kontaktformuläret
- **Debug-kod rensning**: Tog bort alla `console.log()`-rader från båda formulären för renare kod
- **Django-template-syntax**: Förbättrade felhantering för Django-template-kod i JavaScript genom att flytta logik utanför script-taggar
- **Konsekvent landsfält**: Implementerade enkel dropdown med flagg-emoji och landsnamn som fungerar på alla enheter
- **Redigeringsstöd**: Stöd för att visa befintligt valt land när kontaktformuläret laddas för redigering
- **Kodrensning**: Tog bort onödiga CSS-regler och JavaScript-funktioner som inte längre behövdes
- **Användarupplevelse**: Förbättrade användarupplevelsen med enkel och pålitlig dropdown-lista istället för komplex sökbar select
- **Tekniska lärdomar**:
  - Django-template-syntax: Undvik att blanda Django-template-kod direkt i JavaScript för att undvika linter-fel
  - Felhantering: Kontrollera alltid om variabler finns innan de används (t.ex. `axe.pk` för nya yxor)
  - KISS-princip: Enkel lösning (dropdown) är ofta bättre än komplex (sökbar select) för grundläggande funktionalitet
  - Debug-kod: Ta bort all debug-kod innan kod går till produktion för bättre prestanda och renare kod
  - Cross-browser kompatibilitet: Standard HTML `<select>` fungerar på alla enheter och webbläsare

## Senaste genomförda förbättringar (2025-01-17)

### Flaggemoji för kontakter (2025-01-17)
- **Landskod-stöd**: Implementerat fullständigt stöd för landskoder (ISO 3166-1 alpha-2) i Contact-modellen med automatisk konvertering till flaggemoji
- **Template filter**: Skapat `country_flag` filter som konverterar landskod till motsvarande flaggemoji (t.ex. "SE" → 🇸🇪)
- **Konsekvent visning**: Flaggemoji visas nu på alla ställen där kontakter visas:
  - Kontaktdetaljsidan (rubrik)
  - Transaktionshistoriken på yxdetaljsidan
  - Transaktioner på tillverkardetaljsidan
  - Kontakter som handlat med tillverkaren
  - Mest aktiva kontakter på statistik-sidan
  - Kontaktlistan
  - Transaktionslistan
  - Yxformuläret
- **Sökbart landsfält**: ContactForm har uppdaterats med ett sökbart select-fält som visar flagg-emoji och landsnamn
- **Automatisk datamigrering**: Befintliga kontakter med land "Sverige" och "Finland" har uppdaterats automatiskt med rätt landskod
- **Responsiv design**: Flaggemoji anpassas för olika skärmstorlekar med lämplig marginal (`me-1` eller `me-2`)
- **Tekniska lärdomar**:
  - Template filters: Använd `@register.filter` för att skapa återanvändbara filter
  - Datamigrering: Använd Django management commands för säker uppdatering av befintlig data
  - Konsekvent UX: Implementera funktionalitet på alla relevanta ställen för enhetlig användarupplevelse
  - ISO-standarder: Använd ISO 3166-1 alpha-2 för landskoder för internationell kompatibilitet

### Plattformsfilter och dynamisk färgsättning (2025-07-15)
- **Plattformsfilter i yxlistan**: Implementerat fullständigt stöd för filtrering av yxor på plattform med dropdown och URL-parametrar
- **Dynamisk färgsättning**: Varje plattform får en unik färg baserat på ID för ökad överskådlighet och distinktion
- **Färgkonfliktlösning**: Undviker grön/röd färger som redan används för status/ekonomi-kolumnerna
- **Konsekvent styling**: Alla plattformsnamn visas med fetstil för tydlighet och läsbarhet
- **Django ORM-optimering**: Fixat relationer mellan Axe och Transaction med `related_name='transactions'` för bättre prestanda
- **CSV-export förbättringar**: Säker hantering av radbrytningar i textfält med `clean_text()` funktion för korrekt export
- **Statistikkort-fix**: Statistikkorten visar nu korrekt data för filtrerade yxor istället för hela samlingen
- **Tekniska lärdomar**:
  - CSS-specificitet: Använd `!important` och specifika selektorer för att överskriva Bootstrap
  - Inline-styling: Använd `<strong>` taggar för att tvinga fetstil oavsett CSS-konflikter
  - Django ORM: `related_name` eliminerar konflikter med automatiska reverse-relationer
  - PowerShell-kompatibilitet: Använd `;` istället för `&&` för att kedja kommandon
  - Statistikkort-logik: Beräkna statistik baserat på filtrerade objekt, inte hela databasen

### URL-uppladdning och bildhantering (2025-07-14)
- **URL-uppladdning av bilder**: Implementerat fullständigt stöd för att ladda ner bilder från URL:er med förhandsvisning, drag & drop och automatisk lagring.
- **Förhandsvisning av URL:er**: URL:er visas som riktiga bilder i förhandsvisningen med fallback för CORS-problem.
- **Drag & drop för URL:er**: URL:er kan flyttas och ordnas precis som vanliga bilder.
- **Laddningsindikator**: Visar spinner under nedladdning av URL:er för bättre användarupplevelse.
- **Optimerad omdöpningslogik**: Omdöpning körs endast när nödvändigt (inte vid borttagning av sista bilden).
- **Backend-integration**: Komplett hantering av URL-nedladdning med felhantering och timeout.

### Tillverkarbilder och länkar - Avancerad hantering (2025-07-14)
- **Inline-redigering och drag & drop:** Implementerat fullständig inline-redigering och drag & drop-sortering för både tillverkarbilder och -länkar med AJAX-baserad backendhantering.
- **Lightbox med navigering:** Förbättrad lightbox med navigationsknappar för att bläddra mellan bilder i samma grupp, med förbättrad kontrast och hover-färger.
- **Markdown-stöd:** Implementerat EasyMDE för markdown-redigering av bildbeskrivningar med rendering i lightbox.
- **Klickbara kort:** Hela kortet är nu klickbart för både bilder (öppnar lightbox) och aktiva länkar (öppnar i ny flik), med redigeringsknappar som inte triggar klicket.
- **Visuell hantering för inaktiva länkar:** Gråtonad styling, URL visas som text (inte klickbar), och "Inaktiv"-badge för tydlig statusindikation.
- **Hover-effekter:** Subtila hover-effekter på bild- och länkkort för bättre användarupplevelse utan störande animationer.
- **Template filter:** Skapat `strip_markdown_and_truncate` filter för att visa information i tillverkarlistan med markdown borttagen och text begränsad till 150 tecken.

### Tillverkarbilder och länkar - Grundläggande funktionalitet (2025-07-14)
- **Inline-redigering av tillverkarnamn:** AJAX-baserad redigering av tillverkarnamn utan sidladdning.
- **Markdown-redigerare för information:** EasyMDE-integration för att redigera tillverkarens information med markdown-stöd.
- **Bildhantering:** Drag & drop-sortering, inline-redigering av bildtext och beskrivningar, och kategorisering av bilder (Stämpel/Övrig bild).
- **Länkhantering:** Inline-redigering, borttagning och drag & drop-sortering för tillverkarlänkar med olika typer (Hemsida, Katalog, Video, etc.).
- **Backend-integration:** Komplett AJAX-hantering med vyer för redigering, borttagning och omordning av både bilder och länkar.

## Tidigare genomförda förbättringar (2025-01-01)

### Admin-raderingsvy för yxor
- **Problem:** Standard Django admin visade nästlade listor som Python-strängar och saknade kontroll över bildradering.
- **Lösning:** Custom template med platt lista och bockruta för bildradering.
- **Implementation:** 
  - Custom `AxeAdmin` class med `delete_confirmation_template`
  - `get_flat_deleted_objects()` metod för att platta ut listor
  - Custom template `delete_confirmation.html` med tydlig layout
  - Bockruta för att styra om bildfiler tas bort från disken

### Kontaktsökning och hantering
- **Problem:** Användare behövde skapa kontakter manuellt och kunde inte återanvända befintliga.
- **Lösning:** AJAX-sökning med dropdown-resultat och smart matchning.
- **Implementation:**
  - `search_contacts` view med JSON-response
  - JavaScript med debounced sökning
  - Dropdown med klickbara resultat
  - Fallback till ny kontakt om ingen matchning

### Plattformshantering
- **Problem:** Plattformar skapades manuellt och kunde dupliceras.
- **Lösning:** Samma AJAX-sökning som för kontakter.
- **Implementation:**
  - `search_platforms` view
  - Smart matchning av befintliga plattformar
  - Automatisk skapning av nya vid behov

### Transaktionshantering
- **Problem:** Transaktionstyper hanterades manuellt och var förvirrande.
- **Lösning:** Automatisk typbestämning baserat på pris (negativ = köp, positiv = sälj).
- **Implementation:**
  - Ta bort `transaction_type` fält från formuläret
  - Automatisk beräkning av typ baserat på totalbelopp
  - Visuella badges med ikoner för tydlighet
  - Alltid spara positiva värden i databasen

### UI-förbättringar
- **Badges med ikoner:** Tydligare visning av transaktionstyper
- **Responsiv design:** Bättre layout på olika enheter
- **Separata formulär:** Olika fält för skapande vs redigering
- **Bättre feedback:** Tydligare meddelanden och validering

### Transaktionsflöde och AJAX (2025-07-04)
- Fullständigt AJAX-flöde för transaktioner: lägga till, redigera och ta bort sker nu med AJAX, inklusive bekräftelse och felhantering.
- Responsiv och enhetlig UI: Knappar och modaler är anpassade för både desktop och mobil, med endast ikon på mobil där det är relevant.
- Automatisk typbestämning: Vid redigering visas negativa värden för köp, positiva för sälj.
- Placering av knappar: "Lägg till transaktion" visas nu logiskt under yxinformationen när inga transaktioner finns.
- Iterativ UX-förbättring: Placering, utseende och funktion för knappar och modaler har förbättrats stegvis utifrån feedback och testning.

### Arbetsflöde och TODO
- Konsekvent användning av TODO_FEATURES.md: Delmål bockas av löpande, och nya förbättringsförslag läggs till direkt i filen.
- Dokumentation av UI/UX-beslut: Beslut om t.ex. när text ska döljas på mobil, och när den alltid ska visas, dokumenteras för framtida utveckling.

### Framtida riktlinjer (uppdatering)
- Publik/inloggad vy: Plan för att i framtiden ha både publik och inloggad vy, där känsliga uppgifter maskeras i den publika delen.

### TODO-hantering och dokumentation (2025-01-01)
- **Konsekvent TODO-hantering:** Vi bockar av delmål löpande i TODO_FEATURES.md och lägger till nya förbättringsförslag direkt i filen.
- **Redundanshantering:** Vi regelbundet går igenom TODO-listan för att identifiera och ta bort duplicerade punkter, samt flyttar punkter till rätt sektioner baserat på funktionalitet.
- **Sektionsorganisering:** Vi grupperar punkter logiskt (t.ex. bildhantering, yxhantering, säkerhet) och flyttar punkter som hamnat i fel sektion (t.ex. säkerhetsrelaterade punkter till "Säkerhet och användare").
- **Implementationsstatus:** Vi kontrollerar och uppdaterar [x] markeringar baserat på vad som faktiskt är implementerat, inte bara antar att något är klart.
- **Numrering:** Vi uppdaterar numrering konsekvent när vi flyttar punkter mellan sektioner.

### Kodgranskningsprocess
- **Periodisk stegvis kodgranskning:** Vi går igenom koden i omgångar för att identifiera och åtgärda refaktoreringsbehov, buggfixar och tillsnyggning.
- **Testning per steg:** Varje steg testas innan nästa påbörjas för att säkerställa att ändringar fungerar som förväntat.
- **Kontinuerlig process:** Detta är en pågående aktivitet, inte en engångsgrej.

### Template-förbättringar och DRY-principer (2025-07-12)
- **Återanvändbara includes:** Vi skapar includes för återkommande UI-komponenter för att undvika duplicerad kod.
- **Model-properties:** Flyttar komplexa beräkningar från vyer till model-properties för bättre separation av ansvar.
- **Template-struktur:** Organiserar templates med includes för statistik-kort, filter-sektioner och andra återkommande element.
- **Implementation:**
  - Skapade `_stat_card.html` för generiska statistik-kort
  - Skapade `_axe_stats_cards.html` för yxlistans statistik (6 kort + vinst/förlust)
  - Skapade `_contact_stats_cards.html` för kontaktlistans statistik (3 kort)
  - Skapade `_transaction_stats_cards.html` för transaktionslistans statistik (4 kort + vinst/förlust)
  - Uppdaterade alla list-templates för att använda nya includes
  - Lade till `{% load axe_filters %}` i includes för att säkerställa att custom filters fungerar
  - Skapade återanvändbara includes för transaktionsrader, status-badges och breadcrumbs
  - Förbättrade breadcrumbs och rubrik på detaljsidan: ID - Tillverkare - Modell
- **Fördelar:** Minskad kodduplicering, enklare underhåll, konsekvent utseende

### Kodstruktur och refaktorering (2025-07-12)
- **Vy-separation:** Delade upp stora vy-filer i mindre, fokuserade filer:
  - `views_axe.py` - yxrelaterade vyer
  - `views_contact.py` - kontaktrelaterade vyer  
  - `views_manufacturer.py` - tillverkare-relaterade vyer
  - `views_transaction.py` - transaktionsrelaterade vyer
- **Model-properties för statistik:** Flyttade komplexa beräkningar från vyer till model-properties:
  - `Axe.total_buy_value`, `Axe.total_sale_value`, `Axe.net_value`
  - `Manufacturer.total_buy_value`, `Manufacturer.total_sale_value`, `Manufacturer.net_value`
  - `Contact.total_buy_value`, `Contact.total_sale_value`, `Contact.net_value`
- **Fördelar:** Renare vyer, bättre testbarhet, återanvändbar logik
- **URL-struktur:** Uppdaterade `urls.py` för att importera från nya vy-filer

### Markdown-standarder och formatering
- **TODO_FEATURES.md:** Använder numrerade listor med [ ] för att bocka av (punkt 1, 2, 3...)
- **WORKFLOW_AND_COLLAB.md:** Använder punktlistor med - och **fet text** för rubriker
- **Konsekvent formatering:** Vi följer befintliga standarder i varje fil och uppdaterar inte bara innehåll utan också formatering

### UX-arbete och responsiv design (2025-01-01)
- **Iterativ UX-förbättring:** Vi förbättrar UX stegvis baserat på feedback och testning, inte i stora klumpar.
- **Mobil-först approach:** Vi designar för mobil först och anpassar sedan för desktop, inte tvärtom.
- **Knappplacering och text:** Vi har tydliga riktlinjer för när text ska döljas på mobil (endast ikon) vs alltid visas:
  - Endast ikon på mobil: Transaktionsknappar, redigeringsknappar i listor
  - Alltid text synlig: "Lägg till transaktion" när inga transaktioner finns, viktiga funktioner
- **Responsiv design:** Vi testar alltid på både mobil och desktop innan vi anser något klart.
- **Konsekvent UI:** Vi använder samma mönster för liknande funktioner (t.ex. AJAX-sökning för kontakter och plattformar).

### AJAX och JavaScript-implementation
- **AJAX-flöden:** Vi implementerar fullständiga AJAX-flöden med felhantering och feedback, inte bara enkla requests.
- **Modal-hantering:** Vi använder modaler för komplexa formulär men undviker dem för enkla listor på mobil.
- **DOM-manipulation:** Vi säkerställer att formulär och fält alltid finns i DOM:en innan vi försöker manipulera dem.
- **Event-hantering:** Vi använder event delegation där det är lämpligt och hanterar cleanup ordentligt.
- **Felhantering:** Vi visar tydlig feedback i UI:n när AJAX-anrop misslyckas, inte bara i konsolen.

### Felsökning och buggfixar (2025-07-12)
- **TemplateSyntaxError:** Löstes genom att lägga till `{% load axe_filters %}` i include-filer för att säkerställa att custom filters fungerar.
- **Loader/spinner-problem:** Identifierade och löste problem med laddningsindikatorer på tillverkarsidorna med global CSS/JS-fix.
- **Debug-kod:** Lade till och tog bort debug-kod för att identifiera frontend-problem.
- **NoReverseMatch-fel:** Åtgärdade fel för `search_contacts` och `search_platforms` genom att lägga tillbaka URL-mappning i `urls.py`.
- **404-fel:** Löstes genom att redirecta till senaste yxan och återställa galleri-navigationen.

### Mått-UX och användarfeedback (2025-07-12)
- **Notifikationer före sidladdning:** Användare behöver se bekräftelse innan sidan laddas om. Vi använder `setTimeout` för att fördröja sidladdning så att notifikationer hinner visas.
- **Animationer för feedback:** Smooth övergångar (fade out, slide) ger professionell känsla och tydlig visuell feedback.
- **Laddningsindikatorer:** Spinner och inaktiverade knappar under pågående operationer förhindrar dubbel-submit och ger tydlig feedback.
- **Inline-redigering:** Minskar behovet av sidladdningar och förbättrar flödet. Använd AJAX för små ändringar, sidladdning för stora uppdateringar.
- **Batch-operationer:** Effektivt för att hantera flera objekt samtidigt med tydlig feedback om antal tillagda objekt.
- **DOM-manipulation:** Ta bort element från DOM med animation istället för `location.reload()` för smidigare användarupplevelse.
- **Felhantering:** Återställ UI-tillstånd vid fel för bättre användarupplevelse (knappar, formulär, etc.).

### Transaktionsflöde och datamodell
- **Automatisk typbestämning:** Transaktionstyper bestäms automatiskt baserat på pris (negativ = köp, positiv = sälj).
- **Värdehantering:** Vi sparar alltid positiva värden i databasen men visar negativa för köp i UI:n.
- **Formulärlogik:** Vi använder separata formulär för skapande vs redigering med olika fält beroende på kontext.
- **Smart defaults:** Vi sätter smarta standardvärden (t.ex. dagens datum för transaktioner).

### Arbetsflöde för större ändringar
- **Planering:** Vi diskuterar och planerar större ändringar innan implementation
- **Iterativ utveckling:** Vi arbetar stegvis och testar varje del innan vi går vidare
- **Dokumentation:** Vi uppdaterar både TODO-listan och arbetsflödesdokumentationen löpande
- **Git-hantering:** Vi committar och pushar regelbundet för att spara framsteg
- **Branch-strategi:** Vi använder feature branches för större ändringar och pushar till GitHub för säkerhet
- **Testning:** Vi testar alltid funktionalitet i webbläsaren innan commit

## Framtida riktlinjer
- **Testa alltid:** Testa funktionalitet i webbläsaren innan commit
- **Dokumentera beslut:** Skriv ner tekniska beslut och varför de togs
- **Iterativ feedback:** Ta emot feedback och förbättra iterativt
- **Kodkvalitet:** Håll koden ren och kommenterad för framtida underhåll
- **Periodvis stegvis kodgranskning:** Vi går igenom koden i omgångar för att identifiera och åtgärda refaktoreringsbehov, buggfixar och tillsnyggning. Varje steg testas innan nästa påbörjas.
- **TODO-underhåll:** Regelbundet rensa upp och organisera TODO-listan för att hålla den aktuell och användbar
- **Sektionslogik:** Placera nya punkter i rätt sektion från början och flytta befintliga när de hamnat fel

## Vanliga template-fel och debuggtips

- Kontrollera alltid att varje {% block %} avslutas med {% endblock %} allra sist i filen.
- Lägg aldrig {% endblock %} inuti JavaScript-strängar eller HTML-element.
- Om du får TemplateSyntaxError: Unclosed tag, kontrollera block-taggar och includes.
- Vid problem med next_id: kör python manage.py init_next_axe_id.
- Vid problem med återanvändbara includes: kontrollera att rätt context skickas in (field=...)

### Senaste förbättringar (juli 2025)
- Refaktorering av formulär med återanvändbara komponenter (_form_field, _form_checkbox, _form_input_group)
- Modernisering av AJAX-sökning och sektioner för kontakt/plattform
- Fix av next_id och TemplateSyntaxError

### Tillverkarbildhantering och lightbox (juli 2025)
- **Problem:** Redigeringsformulär och lightbox laddade inte in befintlig information
- **Lösning:** Ändrade JavaScript-selectors från `[data-image-id]` till `img[data-image-id]` för att hitta rätt element
- **Implementation:**
  - Fixade `editImage()` och `openImageLightbox()` funktioner
  - Lade till navigationsknappar för att bläddra mellan bilder i samma grupp
  - Implementerade gruppbaserad navigering (endast inom samma bildtyp)
  - Lade till bildräknare som visar position i gruppen
  - Förbättrade kontrast på navigationsknappar med `btn-outline-dark` och vit bakgrund
  - Vänsterställde text i lightbox för bättre läsbarhet av längre beskrivningar
  - Semi-bold styling för bildtext med `font-weight: 600`
- **Tekniska beslut:**
  - Använder `data-image-type` för att gruppera bilder för navigering
  - Navigationsknappar visas endast när det finns fler bilder i samma grupp
  - CSS med `!important` för att överskriva Bootstrap's hover-styling
  - Bildräknare visar "X av Y" för tydlig positionering

### UX-beslut och lärdomar (juli 2025)
- **Kontrast-problem:** `btn-outline-light` på vit bakgrund ger extremt dålig kontrast
- **Lösning:** `btn-outline-dark` med `background-color: rgba(255,255,255,0.9)` för bra synlighet
- **Text-justering:** Längre beskrivningar är mycket mer läsbara vänsterställda än centrerade
- **Navigationslogik:** Gruppbaserad navigering (endast inom samma bildtyp) ger bättre användarupplevelse än global navigering
- **Debugging:** Linter-fel kan vara falska positiva - alltid testa funktionalitet i webbläsaren

### Deployment och media-filhantering (2025-07-22)
- **Nginx-konfiguration**: Använd Nginx för att servera media-filer direkt i produktion via `location /media/` block
- **Docker-volymer**: Mappa volymer för `/data`, `/media`, `/logs`, `/staticfiles`, `/backups` för data-persistens
- **MEDIA_URL-hantering**: Sätt `MEDIA_URL = '/media/'` i produktion för korrekt URL-generering av Django
- **Sökvägsfix vid backup-återställning**: `restore_backup.py` fixar automatiskt Windows backslashes och `/app/media/` prefix
- **Python-baserad sökvägsfix**: Använd Python-loop istället för SQL-frågor för att hitta och fixa backslashes (mer pålitligt)
- **Miljöspecifik hantering**: Ta bort `media/` prefix i både utveckling och produktion (hanteras automatiskt av Django/Nginx)
- **Docker-rebuild**: Använd `docker-compose build --no-cache` för att säkerställa att alla ändringar inkluderas
- **Settings-kopiering**: Kom ihåg att kopiera uppdaterade settings-filer till containern med `docker-compose cp`
- **Container-restart**: Starta om containern efter settings-ändringar med `docker-compose restart web`

### Statistik och visualisering (2025-07-15)
- **Chart.js för staplade diagram**: Använd `stacked: true` för att visa köp och sälj i samma stapel med tydlig fördelning
- **Färgkodning för statistik**: Konsekvent färgschema - röd för köp/utgifter, blå för sälj/intäkter, grön för köp-aktivitet
- **Datumformatering**: Använd ISO-format (ÅÅÅÅ-MM-DD) genom hela applikationen för konsekvent formatering
- **Django ORM-felhantering**: Validera att fältnamn finns i modellen innan användning i `order_by()` - använd `id` istället för `created_at` när timestamp-fält saknas
- **Senaste aktivitet-sektion**: Visa de 5 senaste aktiviteterna per kategori för snabb översikt, med länkar till detaljsidor
- **Responsiv design för diagram**: Chart.js hanterar responsivitet automatiskt, men testa på olika skärmstorlekar
- **Tooltips och interaktivitet**: Lägg till tooltips med exakta värden för bättre användbarhet av diagram
- **Git-arbetsflöde för små ändringar**: Använd `git commit --amend` för att lägga till små ändringar i föregående commit istället för att skapa nya commits

### Felhantering och debugging (2025-07-15)
- **Django server errors**: Kontrollera terminalen för detaljerade felmeddelanden vid 500-fel - Django ger ofta tydliga ledtrådar om vad som är fel
- **FieldError-hantering**: När Django klagar på att fält inte finns, kontrollera modellens faktiska fält med `model._meta.get_fields()`
- **Linter-fel**: Åtgärda syntaxfel och saknade imports innan testning för att undvika förvirring
- **Git återställning**: Använd `git restore .` för att snabbt återställa oönskade ändringar när implementationer behöver pausas
- **Iterativ utveckling**: Testa funktioner stegvis och få användarfeedback innan vidareutveckling

---

**För AI-assistenter:** Läs igenom denna fil noggrant innan du börjar arbeta med projektet. Den innehåller viktig kontext om arbetsflöden, beslut och riktlinjer som hjälper dig att fortsätta arbetet effektivt.

*Senast uppdaterad: 2025-07-14* 