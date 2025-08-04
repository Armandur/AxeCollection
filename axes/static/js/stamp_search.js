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
        
        if (this.isAxeStampForm) {
            // I add_axe_stamp formuläret - visa som val för select
            const resultsHtml = results.map(stamp => `
                <div class="dropdown-item" style="cursor: pointer;" onclick="selectStamp(${stamp.id}, '${this.escapeHtml(stamp.name)}')">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <strong>${this.escapeHtml(stamp.name)}</strong>
                            <br>
                            <small class="text-muted">
                                ${this.escapeHtml(stamp.manufacturer)} • ${this.escapeHtml(stamp.type)}
                            </small>
                            ${stamp.description ? `
                                <br>
                                <small class="text-muted">${this.escapeHtml(stamp.description)}</small>
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
                </div>
            `).join('');
            
            this.resultsContainer.innerHTML = resultsHtml;
            this.showResults();
        } else {
            // I stämpellistan - visa som länkar
            const resultsHtml = results.map(stamp => `
                <a href="${stamp.url}" class="dropdown-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <strong>${this.escapeHtml(stamp.name)}</strong>
                            <br>
                            <small class="text-muted">
                                ${this.escapeHtml(stamp.manufacturer)} • ${this.escapeHtml(stamp.type)}
                            </small>
                            ${stamp.description ? `
                                <br>
                                <small class="text-muted">${this.escapeHtml(stamp.description)}</small>
                            ` : ''}
                            ${stamp.transcription ? `
                                <br>
                                <small class="text-info">
                                    <i class="fas fa-font"></i> ${this.escapeHtml(stamp.transcription)}
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
            `).join('');
            
            this.resultsContainer.innerHTML = resultsHtml;
            this.showResults();
        }
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