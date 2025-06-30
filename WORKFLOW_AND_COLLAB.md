# Arbetsflöde och samarbetsprinciper (AI & utvecklare)

Denna fil sammanfattar hur vi har resonerat kring arbetsflöde, branch-hantering och samarbete i projektet, baserat på diskussioner mellan utvecklare och AI-assistent.

## Branch-strategi
- **Feature branches:** Varje större funktionalitet utvecklas i en egen branch, t.ex. `feature/axe-create-edit`, `feature/dark-mode`.
- **Push och PR:** När en feature är klar pushas branchen till GitHub och en Pull Request (PR) skapas mot `main` (eller annan relevant branch).
- **Merge-ordning:** Om branches bygger på varandra, mergeas de i rätt ordning (äldsta/underliggande först).
- **Städning:** Efter merge tas feature-branches bort både lokalt och på GitHub för att hålla repo:t städat.

## Git-arbetsflöde
- **Commit-meddelanden:** Skrivs tydligt och sammanfattar vad som ändrats, gärna punktlistor vid större ändringar.
- **Squash/rebase:** Används ibland för att slå ihop flera commits till en innan PR för en renare historik.
- **Uppdatera main:** Efter merge av PR hämtas alltid senaste main innan nya features påbörjas.

## Samarbetsprinciper
- **Transparens:** Allt arbete och alla beslut dokumenteras i chatten och/eller i markdown-filer.
- **Automatisering:** AI-assistenten hjälper till med git-kommandon, branch-hantering och dokumentation.
- **Dokumentation:** Viktiga resonemang, beslut och arbetsflöden dokumenteras i denna fil för framtida utvecklare och AI-assistenter.

---

*Senast uppdaterad: 2025-06-30* 