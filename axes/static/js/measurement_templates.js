// Måttmall-funktionalitet för återanvändning
class MeasurementTemplateManager {
    constructor(measurementTemplates, axeId) {
        this.measurementTemplates = measurementTemplates;
        this.axeId = axeId;
        this.measurementTypes = null; // Kommer att laddas via AJAX
        this.init();
    }

    init() {
        this.setupBatchForm();
        this.setupSingleMeasurementForm();
        this.setupGlobalFunctions();
        this.setupEventListeners();
        this.initializeMeasurementTypes();
    }

    initializeMeasurementTypes() {
        // Standardmåtttyper som används i systemet
        this.measurementTypes = [
            { name: 'Vikt', unit: 'gram' },
            { name: 'Skaftlängd', unit: 'mm' },
            { name: 'Eggbredd', unit: 'mm' },
            { name: 'Nacke till egg', unit: 'mm' },
            { name: 'Huvudvikt', unit: 'gram' },
            { name: 'Ögats bredd', unit: 'mm' },
            { name: 'Ögats höjd', unit: 'mm' }
        ];
    }

    setupBatchForm() {
        const batchForm = document.getElementById('batchMeasurementForm');
        if (batchForm) {
            batchForm.addEventListener('submit', (e) => this.handleBatchSubmit(e));
        }
    }

    setupSingleMeasurementForm() {
        const singleForm = document.getElementById('measurementForm');
        if (singleForm) {
            singleForm.addEventListener('submit', (e) => this.handleSingleMeasurementSubmit(e));
            
            // Hantera visa/dölja custom name field
            const nameSelect = singleForm.querySelector('#measurement-name');
            const customNameField = singleForm.querySelector('#custom-measurement-name');
            const customNameContainer = singleForm.querySelector('.custom-field');
            
            if (nameSelect && customNameField) {
                const handleCustomFieldToggle = (value) => {
                    if (value === 'Övrigt') {
                        if (customNameContainer) {
                            customNameContainer.classList.add('show');
                            customNameContainer.style.display = 'block';
                        } else {
                            customNameField.style.display = 'block';
                        }
                        customNameField.required = true;
                    } else {
                        if (customNameContainer) {
                            customNameContainer.classList.remove('show');
                            customNameContainer.style.display = 'none';
                        } else {
                            customNameField.style.display = 'none';
                        }
                        customNameField.required = false;
                        customNameField.value = '';
                    }
                };
                
                nameSelect.addEventListener('change', (e) => {
                    handleCustomFieldToggle(e.target.value);
                });
                
                // Trigga ändringshändelse vid sidladdning för att sätta rätt tillstånd
                setTimeout(() => {
                    handleCustomFieldToggle(nameSelect.value);
                }, 100);
            } else {
                console.error('Could not find required form elements');
            }
        }
        
        // Lägg till event listeners för redigering och borttagning av befintliga mått
        this.setupMeasurementActions();
    }

    setupMeasurementActions() {
        // Kontrollera om event listeners redan har lagts till för att förhindra dubbletter
        if (this.measurementActionsSetup) {
            return;
        }
        
        // Event listener för redigeringsknapparna
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-edit-measurement') || e.target.closest('.btn-edit-measurement')) {
                e.preventDefault();
                const btn = e.target.matches('.btn-edit-measurement') ? e.target : e.target.closest('.btn-edit-measurement');
                const measurementId = btn.getAttribute('data-measurement-id');
                const name = btn.getAttribute('data-name');
                const value = btn.getAttribute('data-value');
                const unit = btn.getAttribute('data-unit');
                
                this.startInlineEdit(measurementId, name, value, unit);
            }
        });
        
        // Event listener för borttagningsknapparna
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-delete-measurement') || e.target.closest('.btn-delete-measurement')) {
                e.preventDefault();
                const btn = e.target.matches('.btn-delete-measurement') ? e.target : e.target.closest('.btn-delete-measurement');
                const measurementId = btn.getAttribute('data-measurement-id');
                
                this.confirmDeleteMeasurement(measurementId);
            }
        });

        // Event listeners för bekräfta/ångra knappar (dynamiskt skapade)
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-confirm-edit') || e.target.closest('.btn-confirm-edit')) {
                e.preventDefault();
                const btn = e.target.matches('.btn-confirm-edit') ? e.target : e.target.closest('.btn-confirm-edit');
                const measurementId = btn.getAttribute('data-measurement-id');
                this.confirmInlineEdit(measurementId);
            }
            
            if (e.target.matches('.btn-cancel-edit') || e.target.closest('.btn-cancel-edit')) {
                e.preventDefault();
                const btn = e.target.matches('.btn-cancel-edit') ? e.target : e.target.closest('.btn-cancel-edit');
                const measurementId = btn.getAttribute('data-measurement-id');
                this.cancelInlineEdit(measurementId);
            }
        });
        
        // Markera att event listeners har lagts till
        this.measurementActionsSetup = true;
    }

    startInlineEdit(measurementId, name, value, unit) {
        const row = document.querySelector(`tr[data-measurement-id="${measurementId}"]`);
        if (!row) return;

        // Markera raden som under redigering
        row.classList.add('editing');
        
        // Spara ursprungliga värden
        row.setAttribute('data-original-name', name);
        row.setAttribute('data-original-value', value);
        row.setAttribute('data-original-unit', unit);

        // Skapa container för måttyp (dropdown och eventuell textinput)
        const nameCell = row.querySelector('.measurement-name');
        const nameContainer = document.createElement('div');
        nameContainer.className = 'measurement-name-container';
        
        // Skapa dropdown för måttyp
        const measurementTypeSelect = document.createElement('select');
        measurementTypeSelect.className = 'form-control form-control-sm mb-1';
        measurementTypeSelect.id = `edit-name-${measurementId}`;
        
        // Kontrollera om aktuellt mått är av standardtyp eller anpassat
        const isCustomMeasurement = !this.measurementTypes.find(type => type.name === name);
        
        // Lägg till måtttyper i dropdown
        if (this.measurementTypes) {
            this.measurementTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type.name;
                option.textContent = `${type.name} (${type.unit})`;
                if (type.name === name) {
                    option.selected = true;
                }
                measurementTypeSelect.appendChild(option);
            });
        }
        
        // Lägg till "Övrigt" alternativ
        const otherOption = document.createElement('option');
        otherOption.value = 'Övrigt';
        otherOption.textContent = 'Övrigt';
        if (isCustomMeasurement) {
            otherOption.selected = true;
        }
        measurementTypeSelect.appendChild(otherOption);

        // Skapa textinput för anpassat måttnamn
        const customNameInput = document.createElement('input');
        customNameInput.type = 'text';
        customNameInput.className = 'form-control form-control-sm';
        customNameInput.id = `edit-custom-name-${measurementId}`;
        customNameInput.placeholder = 'Ange måttnamn...';
        
        // Sätt värdet för anpassat namn om det är ett anpassat mått
        if (isCustomMeasurement) {
            customNameInput.value = name;
            customNameInput.style.display = 'block';
            customNameInput.required = true;
        } else {
            customNameInput.style.display = 'none';
            customNameInput.required = false;
        }

        nameContainer.appendChild(measurementTypeSelect);
        nameContainer.appendChild(customNameInput);
        
        nameCell.innerHTML = '';
        nameCell.appendChild(nameContainer);

        // Skapa input för värde
        const valueCell = row.querySelector('.measurement-value');
        const valueInput = document.createElement('input');
        valueInput.type = 'number';
        valueInput.step = 'any';
        valueInput.className = 'form-control form-control-sm';
        valueInput.id = `edit-value-${measurementId}`;
        valueInput.value = value;
        valueInput.required = true;

        valueCell.innerHTML = '';
        valueCell.appendChild(valueInput);

        // Skapa input för enhet
        const unitCell = row.querySelector('.measurement-unit');
        const unitInput = document.createElement('input');
        unitInput.type = 'text';
        unitInput.className = 'form-control form-control-sm';
        unitInput.id = `edit-unit-${measurementId}`;
        unitInput.value = unit;
        unitInput.required = true;

        unitCell.innerHTML = '';
        unitCell.appendChild(unitInput);

        // Event listener för måttyp-ändring (auto-uppdatera enhet och visa/dölj anpassat namn)
        measurementTypeSelect.addEventListener('change', (e) => {
            const selectedType = this.measurementTypes.find(type => type.name === e.target.value);
            
            if (e.target.value === 'Övrigt') {
                // Visa textinput för anpassat namn
                customNameInput.style.display = 'block';
                customNameInput.required = true;
                customNameInput.focus();
                
                // Rensa enhetsfältet så användaren kan ange egen enhet
                unitInput.value = '';
            } else if (selectedType) {
                // Dölj textinput för anpassat namn och auto-uppdatera enhet
                customNameInput.style.display = 'none';
                customNameInput.required = false;
                unitInput.value = selectedType.unit;
            }
        });

        // Ändra knappar till bekräfta/ångra
        const actionsCell = row.querySelector('td:last-child');
        actionsCell.innerHTML = `
            <div class="btn-group btn-group-sm" role="group">
                <button type="button" class="btn btn-success btn-confirm-edit" 
                        data-measurement-id="${measurementId}"
                        title="Bekräfta ändringar">
                    <i class="fas fa-check"></i>
                </button>
                <button type="button" class="btn btn-secondary btn-cancel-edit" 
                        data-measurement-id="${measurementId}"
                        title="Ångra ändringar">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }

    async confirmInlineEdit(measurementId) {
        const row = document.querySelector(`tr[data-measurement-id="${measurementId}"]`);
        if (!row) return;

        // Kontrollera om redigering redan pågår för att förhindra dubbla anrop
        if (row.hasAttribute('data-updating')) {
            return;
        }

        // Markera att uppdatering pågår
        row.setAttribute('data-updating', 'true');
        
        // Inaktivera confirm-knappen medan uppdateringen pågår
        const confirmBtn = row.querySelector('.btn-confirm-edit');
        if (confirmBtn) {
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }

        try {
            // Hämta de nya värdena
            const nameSelect = document.getElementById(`edit-name-${measurementId}`);
            const customNameInput = document.getElementById(`edit-custom-name-${measurementId}`);
            const valueInput = document.getElementById(`edit-value-${measurementId}`);
            const unitInput = document.getElementById(`edit-unit-${measurementId}`);

            // Kontrollera att alla element hittades
            if (!nameSelect || !valueInput || !unitInput || !customNameInput) {
                console.error('Could not find required input elements for measurement', measurementId);
                this.showNotification('Fel: kunde inte hitta formulärfält', 'error');
                return;
            }

            // Bestäm vilket måttnamn som ska användas
            let newName;             
            if (nameSelect.value === 'Övrigt') {
                newName = customNameInput.value.trim();
                if (!newName) {
                    this.showNotification('Du måste ange ett måttnamn för Övrigt', 'error');
                    customNameInput.focus();
                    return;
                }
            } else {
                newName = nameSelect.value;
            }

            const newValue = valueInput.value.trim();
            const newUnit = unitInput.value.trim();

            // Validera
            if (!newName || !newValue || !newUnit) {
                this.showNotification('Alla fält måste fyllas i', 'error');
                return;
            }

            // Spara ändringar - bestäm om det är standardmått eller anpassat
            const isStandardMeasurement = nameSelect.value !== 'Övrigt';
            const success = await this.updateMeasurement(measurementId, newName, newValue, newUnit, isStandardMeasurement);
            if (success) {
                // Återställ till normalt läge med nya värden
                this.exitInlineEdit(measurementId, newName, newValue, newUnit);
            }
        } catch (error) {
            console.error('Fel vid uppdatering:', error);
            this.showNotification('Fel vid uppdatering av mått', 'error');
        } finally {
            // Ta bort uppdateringsspärr
            row.removeAttribute('data-updating');
        }
    }

    cancelInlineEdit(measurementId) {
        const row = document.querySelector(`tr[data-measurement-id="${measurementId}"]`);
        if (!row) return;

        // Hämta ursprungliga värden
        const originalName = row.getAttribute('data-original-name');
        const originalValue = row.getAttribute('data-original-value');
        const originalUnit = row.getAttribute('data-original-unit');

        // Återställ till normalt läge med ursprungliga värden
        this.exitInlineEdit(measurementId, originalName, originalValue, originalUnit);
    }

    exitInlineEdit(measurementId, name, value, unit) {
        const row = document.querySelector(`tr[data-measurement-id="${measurementId}"]`);
        if (!row) return;

        // Ta bort redigerings-klass
        row.classList.remove('editing');

        // Återställ cellernas innehåll
        const nameCell = row.querySelector('.measurement-name');
        const valueCell = row.querySelector('.measurement-value');
        const unitCell = row.querySelector('.measurement-unit');

        nameCell.textContent = name;
        valueCell.textContent = value;
        unitCell.textContent = unit;

        // Återställ knappar
        const actionsCell = row.querySelector('td:last-child');
        actionsCell.innerHTML = `
            <div class="btn-group btn-group-sm" role="group">
                <button type="button" class="btn btn-outline-primary btn-edit-measurement" 
                        data-measurement-id="${measurementId}"
                        data-name="${name}"
                        data-value="${value}"
                        data-unit="${unit}"
                        title="Redigera mått">
                    <i class="fas fa-edit"></i>
                </button>
                <button type="button" class="btn btn-outline-danger btn-delete-measurement" 
                        data-measurement-id="${measurementId}"
                        title="Ta bort mått">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        // Rensa temporära attribut
        row.removeAttribute('data-original-name');
        row.removeAttribute('data-original-value');
        row.removeAttribute('data-original-unit');
    }

    confirmDeleteMeasurement(measurementId) {
        // Skapa och visa bekräftelse-modal
        this.showDeleteMeasurementModal(measurementId);
    }

    showDeleteMeasurementModal(measurementId) {
        // Ta bort befintlig modal om den finns
        const existingModal = document.getElementById('deleteMeasurementModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Skapa modal HTML
        const modalHtml = `
            <div class="modal fade" id="deleteMeasurementModal" tabindex="-1" aria-labelledby="deleteMeasurementModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="deleteMeasurementModalLabel">
                                <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                                Bekräfta borttagning
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Stäng"></button>
                        </div>
                        <div class="modal-body">
                            <p>Är du säker på att du vill ta bort detta mått?</p>
                            <p class="text-muted mb-0">
                                <i class="fas fa-info-circle me-1"></i>
                                Denna åtgärd kan inte ångras.
                            </p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-1"></i>Avbryt
                            </button>
                            <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                                <i class="fas fa-trash me-1"></i>Ta bort mått
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Lägg till modal till DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Hämta modal-element
        const modal = document.getElementById('deleteMeasurementModal');
        const confirmBtn = document.getElementById('confirmDeleteBtn');

        // Lägg till event listener för bekräfta-knappen
        confirmBtn.addEventListener('click', () => {
            // Stäng modal
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            bootstrapModal.hide();
            
            // Utför borttagning
            this.deleteMeasurement(measurementId);
        });

        // Visa modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();

        // Ta bort modal från DOM när den stängs
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    async updateMeasurement(measurementId, name, value, unit, isStandardMeasurement = true) {
        const formData = new FormData();
        
        if (isStandardMeasurement) {
            // Standardmått - skicka namn direkt
            formData.append('name', name);
        } else {
            // Anpassat mått - skicka som "Övrigt" med custom_name
            formData.append('name', 'Övrigt');
            formData.append('custom_name', name);
        }
        
        formData.append('value', value);
        formData.append('unit', unit);
        
        try {
            const response = await fetch(`/yxor/${this.axeId}/matt/${measurementId}/update/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Mått uppdaterat', 'success');
                return true;
            } else {
                this.showNotification('Fel vid uppdatering av mått', 'error');
                return false;
            }
        } catch (error) {
            console.error('Fel:', error);
            this.showNotification('Fel vid uppdatering av mått', 'error');
            return false;
        }
    }

    async deleteMeasurement(measurementId) {
        try {
            const response = await fetch(`/yxor/${this.axeId}/matt/${measurementId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Ta bort rad från UI
                const row = document.querySelector(`tr[data-measurement-id="${measurementId}"]`);
                if (row) {
                    row.remove();
                }
                
                // Uppdatera räknare
                this.updateMeasurementCount();
                this.showNotification('Mått borttaget', 'success');
            } else {
                this.showNotification('Fel vid borttagning av mått', 'error');
            }
        } catch (error) {
            console.error('Fel:', error);
            this.showNotification('Fel vid borttagning av mått', 'error');
        }
    }

    updateMeasurementCount() {
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
            if (window.showToast) showToast(`Mall "${templateName}" hittades inte.`, 'warning'); else alert(`Mall "${templateName}" hittades inte.`);
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

    async handleSingleMeasurementSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        
        // Validera att obligatoriska fält är ifyllda
        const nameField = form.querySelector('[name="name"]');
        const customNameField = form.querySelector('[name="custom_name"]');
        const valueField = form.querySelector('[name="value"]');
        const unitField = form.querySelector('[name="unit"]');
        
        let measurementName = nameField ? nameField.value : '';
        if (measurementName === 'Övrigt' && customNameField) {
            measurementName = customNameField.value;
        }
        
        if (!measurementName || !valueField.value || !unitField.value) {
            this.showNotification('Alla fält måste fyllas i', 'error');
            return;
        }
        
        // Inaktivera submit-knappen
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Lägg till...';
        }
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                // Rensa formuläret
                form.reset();
                // Dölj custom name field om det visas
                const customNameContainer = form.querySelector('.custom-field');
                if (customNameContainer) {
                    customNameContainer.classList.remove('show');
                    customNameContainer.style.display = 'none';
                } else if (customNameField) {
                    customNameField.style.display = 'none';
                }
                // Återställ required-attribut
                const customNameField = form.querySelector('#custom-measurement-name');
                if (customNameField) {
                    customNameField.required = false;
                }
                // Uppdatera UI efter kort fördröjning
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                this.showNotification('Fel vid tillägg av mått: ' + (data.error || 'Ogiltiga data'), 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Fel vid tillägg av mått', 'error');
        } finally {
            // Återställ submit-knappen
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-plus me-1"></i><span class="d-none d-md-inline">Lägg till</span>';
            }
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

// Gamla funktioner tagna bort - nu hanteras allt i MeasurementTemplateManager-klassen

// Automatisk initiering när DOM är redo
document.addEventListener('DOMContentLoaded', function() {
    // Kontrollera om måttmallar finns och initiera
    if (typeof window.measurementTemplates !== 'undefined' && typeof window.axeId !== 'undefined') {
        window.measurementManager = new MeasurementTemplateManager(window.measurementTemplates, window.axeId);
    }
}); 