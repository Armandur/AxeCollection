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

### AJAX och JavaScript
- **Debouncing:** Använd timeout för AJAX-sökningar för att undvika för många requests.
- **Error handling:** Hantera AJAX-fel gracefully med fallback-beteenden.
- **Dropdown management:** Visa/dölj dropdowns baserat på sökresultat och användarinteraktion.

### Formulärdesign
- **Conditional fields:** Visa olika fält beroende på om objekt skapas eller redigeras.
- **Smart defaults:** Sätt smarta standardvärden (t.ex. dagens datum för transaktioner).
- **Validation feedback:** Ge tydlig feedback när validering misslyckas.

## Senaste genomförda förbättringar (2025-07-14)

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

---

**För AI-assistenter:** Läs igenom denna fil noggrant innan du börjar arbeta med projektet. Den innehåller viktig kontext om arbetsflöden, beslut och riktlinjer som hjälper dig att fortsätta arbetet effektivt.

*Senast uppdaterad: 2025-07-14* 