// Måttmall-funktionalitet för återanvändning
class MeasurementTemplateManager {
    constructor(measurementTemplates, axeId) {
        this.measurementTemplates = measurementTemplates;
        this.axeId = axeId;
        this.init();
    }

    init() {
        this.setupBatchForm();
        this.setupGlobalFunctions();
        this.setupEventListeners();
    }

    setupBatchForm() {
        const batchForm = document.getElementById('batchMeasurementForm');
        if (batchForm) {
            batchForm.addEventListener('submit', (e) => this.handleBatchSubmit(e));
        }
    }

    setupGlobalFunctions() {
        // Gör funktioner tillgängliga globalt
        window.loadTemplate = (templateName) => this.loadTemplate(templateName);
        window.removeBatchRow = (idx) => this.removeBatchRow(idx);
        window.hideBatchForm = () => this.hideBatchForm();
    }

    setupEventListeners() {
        // Hantera template-knappar
        document.addEventListener('click', (e) => {
            if (e.target.matches('.template-btn') || e.target.closest('.template-btn')) {
                const btn = e.target.matches('.template-btn') ? e.target : e.target.closest('.template-btn');
                const templateName = btn.getAttribute('data-template');
                if (templateName) {
                    this.loadTemplate(templateName);
                }
            }
        });

        // Hantera hideBatchForm-knappar
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="hideBatchForm"]')) {
                this.hideBatchForm();
            }
        });
    }

    loadTemplate(templateName) {
        const template = this.measurementTemplates[templateName];
        if (!template) {
            alert(`Mall "${templateName}" hittades inte.`);
            return;
        }
        
        const container = document.getElementById('batchMeasurementFormContainer');
        const rows = document.getElementById('batchMeasurementRows');
        if (!container || !rows) {
            console.error('Batch form container not found');
            return;
        }

        rows.innerHTML = '';
        template.forEach((m, idx) => {
            rows.innerHTML += `
                <div class="row mb-2 align-items-end" id="batch-row-${idx}">
                    <div class="col-md-4">
                        <label class="form-label">Måttyp</label>
                        <input type="text" class="form-control" name="measurements[${idx}][name]" value="${m.name}" readonly>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Värde</label>
                        <input type="number" step="any" class="form-control" name="measurements[${idx}][value]" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Enhet</label>
                        <input type="text" class="form-control" name="measurements[${idx}][unit]" value="${m.unit}" required>
                    </div>
                    <div class="col-md-2 d-flex align-items-end">
                        <button type="button" class="btn btn-sm btn-outline-danger" data-action="removeBatchRow" data-row="${idx}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        // Lägg till event listener för soptunne-knappar
        rows.querySelectorAll('[data-action="removeBatchRow"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const rowIdx = parseInt(e.target.closest('button').getAttribute('data-row'));
                this.removeBatchRow(rowIdx);
            });
        });
        
        container.style.display = '';
        container.scrollIntoView({behavior: 'smooth'});
    }

    removeBatchRow(idx) {
        const row = document.getElementById(`batch-row-${idx}`);
        if (row) {
            row.remove();
            // Omindexera de återstående raderna för att undvika problem med formulärdata
            this.reindexBatchRows();
        }
    }

    reindexBatchRows() {
        const rows = document.querySelectorAll('#batchMeasurementRows .row');
        rows.forEach((row, newIdx) => {
            const oldIdx = row.id.replace('batch-row-', '');
            row.id = `batch-row-${newIdx}`;
            
            // Uppdatera input-namn
            const nameInput = row.querySelector('input[name^="measurements["]');
            const valueInput = row.querySelector('input[name*="[value]"]');
            const unitInput = row.querySelector('input[name*="[unit]"]');
            
            if (nameInput) nameInput.name = `measurements[${newIdx}][name]`;
            if (valueInput) valueInput.name = `measurements[${newIdx}][value]`;
            if (unitInput) unitInput.name = `measurements[${newIdx}][unit]`;
            
            // Uppdatera data-row attribut för soptunne-knappen
            const deleteBtn = row.querySelector('button[data-action="removeBatchRow"]');
            if (deleteBtn) {
                deleteBtn.setAttribute('data-row', newIdx);
            }
        });
    }

    hideBatchForm() {
        const container = document.getElementById('batchMeasurementFormContainer');
        if (container) {
            container.style.display = 'none';
        }
    }

    async handleBatchSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                this.showNotification('Fel vid tillägg av mått: ' + (data.error || 'Okänt fel'), 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Fel vid tillägg av mått', 'error');
        }
    }

    showNotification(message, type) {
        const notification = document.getElementById('notification');
        const notificationMessage = document.getElementById('notification-message');
        
        if (notification && notificationMessage) {
            notificationMessage.textContent = message;
            notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
            notification.style.display = 'block';
            
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }
    }
}

// Mått-hantering funktioner
function updateMeasurementCount() {
    // Hitta alla mått-element (både tabellrader och kort)
    const tableRows = document.querySelectorAll('tr[data-measurement-id]');
    const cards = document.querySelectorAll('.measurement-card[data-measurement-id]');
    const measurements = tableRows.length > 0 ? tableRows : cards;
    
    const count = measurements.length;
    
    // Uppdatera räknaren i alla ställen
    const countElements = document.querySelectorAll('.measurement-count');
    countElements.forEach(element => {
        element.textContent = count;
    });
    
    // Kontrollera om vi ska visa tomma staten
    const emptyState = document.querySelector('.measurement-empty-state');
    const measurementList = document.querySelector('.measurement-list');
    
    if (count === 0) {
        // Visa tomma staten
        if (emptyState) {
            emptyState.style.display = 'block';
        }
        if (measurementList) {
            measurementList.style.display = 'none';
        }
    } else {
        // Dölj tomma staten
        if (emptyState) {
            emptyState.style.display = 'none';
        }
        if (measurementList) {
            measurementList.style.display = 'block';
        }
    }
}

window.deleteMeasurement = function(measurementId) {
    if (confirm('Är du säker på att du vill ta bort detta mått?')) {
        fetch(`/yxor/${window.axeId}/matt/${measurementId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const row = document.querySelector(`tr[data-measurement-id="${measurementId}"]`);
                if (row) {
                    row.remove();
                }
                const card = document.querySelector(`.measurement-card[data-measurement-id="${measurementId}"]`);
                if (card) {
                    card.remove();
                }
                updateMeasurementCount();
                showNotification('Mått borttaget', 'success');
            } else {
                showNotification('Fel vid borttagning av mått', 'error');
            }
        })
        .catch(error => {
            console.error('Fel:', error);
            showNotification('Fel vid borttagning av mått', 'error');
        });
    }
    return false;
};

window.updateMeasurement = function(measurementId, value, unit) {
    const formData = new FormData();
    formData.append('value', value);
    formData.append('unit', unit);
    
    fetch(`/yxor/${window.axeId}/matt/${measurementId}/update/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Mått uppdaterat', 'success');
        } else {
            showNotification('Fel vid uppdatering av mått', 'error');
        }
    })
    .catch(error => {
        console.error('Fel:', error);
        showNotification('Fel vid uppdatering av mått', 'error');
    });
};

// Global notifikationsfunktion (DRY - definieras endast här)
function showNotification(message, type) {
    const notification = document.getElementById('notification');
    const notificationMessage = document.getElementById('notification-message');
    
    if (notification && notificationMessage) {
        notificationMessage.textContent = message;
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
        notification.style.display = 'block';
        
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
}

// Automatisk initiering när DOM är redo
document.addEventListener('DOMContentLoaded', function() {
    // Kontrollera om måttmallar finns och initiera
    if (typeof window.measurementTemplates !== 'undefined' && typeof window.axeId !== 'undefined') {
        window.measurementManager = new MeasurementTemplateManager(window.measurementTemplates, window.axeId);
    }
}); 