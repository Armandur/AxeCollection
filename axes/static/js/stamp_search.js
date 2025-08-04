/**
 * AJAX-sökning för stämplar
 */
class StampSearch {
    constructor() {
        this.searchInput = document.getElementById('stamp-search-input');
        this.resultsContainer = document.getElementById('stamp-search-results');
        this.searchTimeout = null;
        this.isSearching = false;
        
        // Kontrollera om vi är i add_axe_stamp formuläret
        this.isAxeStampForm = document.querySelector('form[action*="stampel/lagg-till"]') !== null;
        
        this.init();
    }
    
    init() {
        if (!this.searchInput) return;
        
        // Event listeners
        this.searchInput.addEventListener('input', this.debounce(this.performSearch.bind(this), 300));
        this.searchInput.addEventListener('focus', this.showResults.bind(this));
        this.searchInput.addEventListener('blur', this.hideResults.bind(this));
        
        // Klick utanför för att stänga resultat
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.resultsContainer.contains(e.target)) {
                this.hideResults();
            }
        });
    }
    
    debounce(func, wait) {
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(this.searchTimeout);
                func(...args);
            };
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(later, wait);
        }.bind(this);
    }
    
    async performSearch() {
        const query = this.searchInput.value.trim();
        const manufacturerFilter = document.getElementById('manufacturer-filter')?.value || '';
        const stampTypeFilter = document.getElementById('stamp-type-filter')?.value || '';
        
        // Hämta nya sökparametrar
        const searchType = document.querySelector('input[name="search_type"]:checked')?.value || 'partial';
        const searchLogic = document.querySelector('input[name="search_logic"]:checked')?.value || 'and';
        
        // Hämta valda symboler
        const selectedSymbols = Array.from(document.querySelectorAll('input[name="symbols"]')).map(input => input.value);
        
        if (!query && !manufacturerFilter && !stampTypeFilter && selectedSymbols.length === 0) {
            this.hideResults();
            return;
        }
        
        this.showLoading();
        
        try {
            const params = new URLSearchParams({
                q: query,
                manufacturer: manufacturerFilter,
                stamp_type: stampTypeFilter,
                search_type: searchType,
                search_logic: searchLogic
            });
            
            // Lägg till valda symboler
            selectedSymbols.forEach(symbolId => {
                params.append('symbols', symbolId);
            });
            
            const response = await fetch(`/stamplar/sok/?${params}`);
            const data = await response.json();
            
            this.displayResults(data.results);
        } catch (error) {
            console.error('Sökfel:', error);
            this.showError();
        }
    }
    
    displayResults(results) {
        if (!this.resultsContainer) return;
        
        if (results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="dropdown-item text-muted">
                    <i class="fas fa-search"></i> Inga resultat hittades
                </div>
            `;
            return;
        }
        
        // Lägg till sammanfattning av sökresultat
        const summaryHtml = this.buildSearchSummary(results);
        
        // Gruppera resultat efter matchningstyp
        const groupedResults = this.groupResultsByMatchType(results);
        
        if (this.isAxeStampForm) {
            // I add_axe_stamp formuläret - visa som val för select
            const resultsHtml = summaryHtml + this.buildGroupedResultsHtml(groupedResults, true);
            this.resultsContainer.innerHTML = resultsHtml;
            this.showResults();
        } else {
            // I stämpellistan - visa som länkar
            const resultsHtml = summaryHtml + this.buildGroupedResultsHtml(groupedResults, false);
            this.resultsContainer.innerHTML = resultsHtml;
            this.showResults();
        }
    }
    
    buildSearchSummary(results) {
        const query = this.searchInput.value.trim();
        const selectedSymbols = Array.from(document.querySelectorAll('input[name="symbols"]')).map(input => input.value);
        const searchType = document.querySelector('input[name="search_type"]:checked')?.value || 'partial';
        const searchLogic = document.querySelector('input[name="search_logic"]:checked')?.value || 'and';
        
        let summaryText = `Hittade ${results.length} stämpel`;
        if (results.length !== 1) summaryText += 'ar';
        
        const criteria = [];
        if (query) criteria.push(`text: "${query}"`);
        if (selectedSymbols.length > 0) criteria.push(`${selectedSymbols.length} symboler`);
        if (searchType !== 'partial') criteria.push(`söktyp: ${searchType}`);
        if (searchLogic !== 'and') criteria.push(`logik: ${searchLogic}`);
        
        if (criteria.length > 0) {
            summaryText += ` (${criteria.join(', ')})`;
        }
        
        return `
            <div class="dropdown-header">
                <i class="fas fa-info-circle me-2"></i>
                ${summaryText}
            </div>
        `;
    }
    
    groupResultsByMatchType(results) {
        const groups = {
            'name_match': [],
            'description_match': [],
            'transcription_match': [],
            'symbol_match': [],
            'manufacturer_match': [],
            'other': []
        };
        
        const query = this.searchInput.value.trim().toLowerCase();
        const selectedSymbols = Array.from(document.querySelectorAll('input[name="symbols"]')).map(input => input.value);
        
        results.forEach(stamp => {
            let matched = false;
            
            // Använd backend-match_types om tillgängligt, annars beräkna lokalt
            if (stamp.match_types && stamp.match_types.length > 0) {
                stamp.match_types.forEach(matchType => {
                    switch (matchType) {
                        case 'name':
                            groups.name_match.push({...stamp, matchType: 'name'});
                            matched = true;
                            break;
                        case 'description':
                            groups.description_match.push({...stamp, matchType: 'description'});
                            matched = true;
                            break;
                        case 'transcription':
                            groups.transcription_match.push({...stamp, matchType: 'transcription'});
                            matched = true;
                            break;
                        case 'symbol':
                            groups.symbol_match.push({...stamp, matchType: 'symbol'});
                            matched = true;
                            break;
                        case 'manufacturer':
                            groups.manufacturer_match.push({...stamp, matchType: 'manufacturer'});
                            matched = true;
                            break;
                    }
                });
            } else {
                // Fallback till lokal beräkning
                if (query && stamp.name.toLowerCase().includes(query)) {
                    groups.name_match.push({...stamp, matchType: 'name'});
                    matched = true;
                }
                
                if (query && stamp.description && stamp.description.toLowerCase().includes(query)) {
                    groups.description_match.push({...stamp, matchType: 'description'});
                    matched = true;
                }
                
                if (query && stamp.transcription && stamp.transcription.toLowerCase().includes(query)) {
                    groups.transcription_match.push({...stamp, matchType: 'transcription'});
                    matched = true;
                }
                
                if (stamp.symbols && stamp.symbols.length > 0) {
                    const hasSymbolMatch = stamp.symbols.some(symbol => 
                        symbol.toLowerCase().includes(query) || 
                        selectedSymbols.some(selectedId => symbol.includes(selectedId))
                    );
                    if (hasSymbolMatch) {
                        groups.symbol_match.push({...stamp, matchType: 'symbol'});
                        matched = true;
                    }
                }
                
                if (query && stamp.manufacturer.toLowerCase().includes(query)) {
                    groups.manufacturer_match.push({...stamp, matchType: 'manufacturer'});
                    matched = true;
                }
            }
            
            // Om ingen specifik matchning, lägg i "other"
            if (!matched) {
                groups.other.push({...stamp, matchType: 'other'});
            }
        });
        
        return groups;
    }
    
    buildGroupedResultsHtml(groupedResults, isAxeStampForm) {
        const groupLabels = {
            'name_match': 'Namn-matchning',
            'description_match': 'Beskrivning-matchning',
            'transcription_match': 'Transkription-matchning',
            'symbol_match': 'Symbol-matchning',
            'manufacturer_match': 'Tillverkare-matchning',
            'other': 'Andra resultat'
        };
        
        const groupIcons = {
            'name_match': 'fas fa-tag',
            'description_match': 'fas fa-align-left',
            'transcription_match': 'fas fa-font',
            'symbol_match': 'fas fa-icons',
            'manufacturer_match': 'fas fa-industry',
            'other': 'fas fa-list'
        };
        
        let html = '';
        
        Object.keys(groupedResults).forEach(groupKey => {
            const results = groupedResults[groupKey];
            if (results.length === 0) return;
            
            // Lägg till grupp-header
            html += `
                <div class="dropdown-header">
                    <i class="${groupIcons[groupKey]} me-2"></i>
                    ${groupLabels[groupKey]} (${results.length})
                </div>
            `;
            
            // Lägg till resultat i gruppen
            results.forEach(stamp => {
                if (isAxeStampForm) {
                    html += this.buildAxeStampFormItem(stamp);
                } else {
                    html += this.buildStampListItem(stamp);
                }
            });
        });
        
        return html;
    }
    
    buildAxeStampFormItem(stamp) {
        const highlightedName = this.highlightMatch(stamp.name, this.searchInput.value.trim());
        const highlightedDescription = stamp.description ? this.highlightMatch(stamp.description, this.searchInput.value.trim()) : '';
        const highlightedTranscription = stamp.transcription ? this.highlightMatch(stamp.transcription, this.searchInput.value.trim()) : '';
        
        return `
            <div class="dropdown-item" style="cursor: pointer;" onclick="selectStamp(${stamp.id}, '${this.escapeHtml(stamp.name)}')">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <strong>${highlightedName}</strong>
                        <br>
                        <small class="text-muted">
                            ${this.escapeHtml(stamp.manufacturer)} • ${this.escapeHtml(stamp.type)}
                        </small>
                        ${highlightedDescription ? `
                            <br>
                            <small class="text-muted">${highlightedDescription}</small>
                        ` : ''}
                        ${stamp.symbols && stamp.symbols.length > 0 ? `
                            <br>
                            <small class="text-success">
                                <i class="fas fa-icons"></i> ${this.escapeHtml(stamp.symbols.join(', '))}
                            </small>
                        ` : ''}
                        ${highlightedTranscription ? `
                            <br>
                            <small class="text-info">
                                <i class="fas fa-font"></i> ${highlightedTranscription}
                            </small>
                        ` : ''}
                    </div>
                    <span class="badge badge-${this.getStatusBadgeClass(stamp.status)} ml-2">
                        ${this.escapeHtml(stamp.status)}
                    </span>
                </div>
            </div>
        `;
    }
    
    buildStampListItem(stamp) {
        const highlightedName = this.highlightMatch(stamp.name, this.searchInput.value.trim());
        const highlightedDescription = stamp.description ? this.highlightMatch(stamp.description, this.searchInput.value.trim()) : '';
        const highlightedTranscription = stamp.transcription ? this.highlightMatch(stamp.transcription, this.searchInput.value.trim()) : '';
        
        return `
            <a href="${stamp.url}" class="dropdown-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <strong>${highlightedName}</strong>
                        <br>
                        <small class="text-muted">
                            ${this.escapeHtml(stamp.manufacturer)} • ${this.escapeHtml(stamp.type)}
                        </small>
                        ${highlightedDescription ? `
                            <br>
                            <small class="text-muted">${highlightedDescription}</small>
                        ` : ''}
                        ${highlightedTranscription ? `
                            <br>
                            <small class="text-info">
                                <i class="fas fa-font"></i> ${highlightedTranscription}
                            </small>
                        ` : ''}
                        ${stamp.symbols && stamp.symbols.length > 0 ? `
                            <br>
                            <small class="text-success">
                                <i class="fas fa-icons"></i> ${this.escapeHtml(stamp.symbols.join(', '))}
                            </small>
                        ` : ''}
                    </div>
                    <span class="badge badge-${this.getStatusBadgeClass(stamp.status)} ml-2">
                        ${this.escapeHtml(stamp.status)}
                    </span>
                </div>
            </a>
        `;
    }
    
    highlightMatch(text, query) {
        if (!query || !text) return this.escapeHtml(text);
        
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return this.escapeHtml(text).replace(regex, '<mark class="bg-warning">$1</mark>');
    }
    
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    showLoading() {
        if (!this.resultsContainer) return;
        
        this.resultsContainer.innerHTML = `
            <div class="dropdown-item text-muted">
                <i class="fas fa-spinner fa-spin"></i> Söker...
            </div>
        `;
        this.showResults();
    }
    
    showError() {
        if (!this.resultsContainer) return;
        
        this.resultsContainer.innerHTML = `
            <div class="dropdown-item text-danger">
                <i class="fas fa-exclamation-triangle"></i> Ett fel uppstod vid sökning
            </div>
        `;
        this.showResults();
    }
    
    showResults() {
        if (this.resultsContainer) {
            this.resultsContainer.style.display = 'block';
        }
    }
    
    hideResults() {
        if (this.resultsContainer) {
            setTimeout(() => {
                this.resultsContainer.style.display = 'none';
            }, 200);
        }
    }
    
    getStatusBadgeClass(status) {
        switch (status.toLowerCase()) {
            case 'känd':
                return 'success';
            case 'okänd':
                return 'warning';
            case 'osäker':
                return 'danger';
            default:
                return 'secondary';
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global funktion för att välja stämpel i formuläret
function selectStamp(stampId, stampName) {
    const selectElement = document.querySelector('select[name="stamp"]');
    if (selectElement) {
        selectElement.value = stampId;
        // Trigga change event för att uppdatera UI
        selectElement.dispatchEvent(new Event('change'));
    }
    
    // Stäng dropdown
    const resultsContainer = document.getElementById('stamp-search-results');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

// Initialisera sökning när DOM är redo
document.addEventListener('DOMContentLoaded', () => {
    window.stampSearchInstance = new StampSearch();
}); 