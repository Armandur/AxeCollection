# Arbetsflöde och samarbetsprinciper (AI & utvecklare)

Denna fil sammanfattar hur vi har resonerat kring arbetsflöde, branch-hantering och samarbete i projektet, baserat på diskussioner mellan utvecklare och AI-assistent.

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

### AJAX och JavaScript
- **Debouncing:** Använd timeout för AJAX-sökningar för att undvika för många requests.
- **Error handling:** Hantera AJAX-fel gracefully med fallback-beteenden.
- **Dropdown management:** Visa/dölj dropdowns baserat på sökresultat och användarinteraktion.

### Formulärdesign
- **Conditional fields:** Visa olika fält beroende på om objekt skapas eller redigeras.
- **Smart defaults:** Sätt smarta standardvärden (t.ex. dagens datum för transaktioner).
- **Validation feedback:** Ge tydlig feedback när validering misslyckas.

## Senaste genomförda förbättringar (2025-01-01)

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

## Framtida riktlinjer
- **Testa alltid:** Testa funktionalitet i webbläsaren innan commit
- **Dokumentera beslut:** Skriv ner tekniska beslut och varför de togs
- **Iterativ feedback:** Ta emot feedback och förbättra iterativt
- **Kodkvalitet:** Håll koden ren och kommenterad för framtida underhåll

---

*Senast uppdaterad: 2025-01-01* 